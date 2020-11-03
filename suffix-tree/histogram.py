#!./pypy3.7-v7.3.2-linux64/bin/pypy3
import argparse

parser = argparse.ArgumentParser(
    description="Create memory stride histogram from memory trace."
)
parser.add_argument("-mem", "--memory_trace", dest="mem_trace")
parser.add_argument("-stat", "--static_trace", dest="stat_trace")
parser.add_argument("-out", "--output", dest="output")
parser.add_argument("-v", "--verbose", action="store_true")
args = parser.parse_args()

#####
# STAT
# assembler_instruction, opcode_type, instruction_addr,
# instruction_size, number_of_read_registers, read_registers,
# number_of_write_registers, write_registers, base_register,
# index_register, is_read_flag, is_read2_flag, is_write_flag,
# is_branch_flag, is_predicated_flag, is_prefetch_flag = line.split()

# MEM
# op, size, address, block = line.split()
#####

def write_next_fields(instruction, instruction_field, instruction_field_value, instruction_fields_iter, line_iter):
    instruction.update({instruction_field: instruction_field_value})
    instruction_field = next(instruction_fields_iter)
    for i in range(int(instruction_field_value)):
        reg = next(line_iter)
        instruction.update(
            {instruction_field + "_" + str(i): reg}
        )

    return instruction

memory_instructions_in_block = []
number_of_memory_instructions_in_block = 0
stat_trace_aux = []
stat_trace = []
with open(args.stat_trace, "r") as stat:
    line = stat.readline()
    while line:
        if not line.startswith("#"):
            if line.startswith("@"):
                stat_trace.append(stat_trace_aux)
                stat_trace_aux = []

                memory_instructions_in_block.append(
                    number_of_memory_instructions_in_block
                )
                number_of_memory_instructions_in_block = 0

            else:
                line_iter = iter(line.split())
                # was_memory_instruction = False
                instruction = {}
                instruction_fields_iter = iter(
                    [
                        "assembler_instruction",
                        "opcode_type",
                        "instruction_addr",
                        "instruction_size",
                        "number_of_read_registers",
                        "read_registers",
                        "number_of_write_registers",
                        "write_registers",
                        "base_register",
                        "index_register",
                        "is_read_flag",
                        "is_read2_flag",
                        "is_write_flag",
                        "is_branch_flag",
                        "is_predicated_flag",
                        "is_prefetch_flag",
                    ]
                )
                while True:
                    try:
                        instruction_field = next(instruction_fields_iter)
                        instruction_field_value = next(line_iter)

                        if instruction_field == "number_of_read_registers":
                            instruction = write_next_fields(instruction, instruction_field, instruction_field_value, instruction_fields_iter, line_iter)

                        elif instruction_field == "number_of_write_registers":
                            instruction = write_next_fields(instruction, instruction_field, instruction_field_value, instruction_fields_iter, line_iter)
                        
                        elif (
                            instruction_field == "is_read_flag"
                            and instruction_field_value == "1"
                        ):
                            number_of_memory_instructions_in_block += 1
                            instruction.update(
                                {instruction_field: instruction_field_value}
                            )
                            # was_memory_instruction = True

                        elif (
                            instruction_field == "is_read2_flag"
                            and instruction_field_value == "1"
                        ):
                            number_of_memory_instructions_in_block += 2
                            instruction.update(
                                {instruction_field: instruction_field_value}
                            )
                            # was_memory_instruction = True

                        elif (
                            instruction_field == "is_write_flag"
                            and instruction_field_value == "1"
                        ):
                            number_of_memory_instructions_in_block += 1
                            instruction.update(
                                {instruction_field: instruction_field_value}
                            )
                            # was_memory_instruction = True

                        else:
                            instruction.update(
                                {instruction_field: instruction_field_value}
                            )

                    except StopIteration:
                        # if was_memory_instruction:
                        stat_trace_aux.append(instruction)
                        # break

        line = stat.readline()

    stat_trace.append(stat_trace_aux)
    memory_instructions_in_block.append(number_of_memory_instructions_in_block)


def updateStrideInAccess(info, address, access):
    stride = int(address) - info["last_address_in_" + access]
    if stride in info[access + "_strides"].keys():
        info[access + "_strides"].update(
            {stride: info[access + "_strides"][stride] + 1}
        )
    else:
        info[access + "_strides"].update({stride: 1})
    info.update({"last_address_in_" + access: int(address)})
    return info


memory_instructions_info = {}
with open(args.mem_trace, "r") as mem:
    line = mem.readline()
    i = 0
    while line:
        if line.startswith("#"):
            line = mem.readline()
            continue

        if i >= 20:
            break

        # print(line, end="\n")
        op, size, address, block = line.split()

        for j in range(memory_instructions_in_block[int(block)]):
            # print("LOOP: " + str(j))
            # print(stat_trace[int(block)][j]["instruction_addr"], end="\n\n")
            instruction = stat_trace[int(block)][j]["instruction_addr"]
            info = {
                "access1_strides": {},
                "last_address_in_access1": None,
                "access2_strides": {},
                "last_address_in_access2": None,
                "access3_strides": {},
                "last_address_in_access3": None,
                "count": 0,
            }

            if stat_trace[int(block)][j]["is_read_flag"] == "1":
                if instruction in memory_instructions_info.keys():
                    info = memory_instructions_info[instruction]
                    info = updateStrideInAccess(info, address, "access1")

                    if stat_trace[int(block)][j]["is_write_flag"] == "1":
                        op, size, address, block = mem.readline().split()

                        info = updateStrideInAccess(info, address, "access3")

                    info.update({"count": info["count"] + 1})

                else:
                    info["access1_strides"].update({int(address): 1})
                    info.update({"last_address_in_access1": int(address)})

                    if stat_trace[int(block)][j]["is_write_flag"] == "1":
                        op, size, address, block = mem.readline().split()

                        info["access3_strides"].update({int(address): 1})
                        info.update({"last_address_in_access3": int(address)})

                    info.update({"count": 1})

            elif stat_trace[int(block)][j]["is_read2_flag"] == "1":
                if instruction in memory_instructions_info.keys():
                    info = memory_instructions_info[instruction]
                    info = updateStrideInAccess(info, address, "access1")

                    op, size, address, block = mem.readline().split()

                    info = updateStrideInAccess(info, address, "access2")

                    if stat_trace[int(block)][j]["is_write_flag"] == "1":
                        op, size, address, block = mem.readline().split()

                        info = updateStrideInAccess(info, address, "access3")

                    info.update({"count": info["count"] + 1})

                else:
                    info["access1_strides"].update({int(address): 1})
                    info.update({"last_address_in_access1": int(address)})

                    op, size, address, block = mem.readline().split()

                    info["access2_strides"].update({int(address): 1})
                    info.update({"last_address_in_access2": int(address)})

                    if stat_trace[int(block)][j]["is_write_flag"] == "1":
                        op, size, address, block = mem.readline().split()

                        info["access3_strides"].update({int(address): 1})
                        info.update({"last_address_in_access3": int(address)})

                    info.update({"count": 1})

            memory_instructions_info.update({instruction: info})
        line = mem.readline()
        i = i + 1

print(memory_instructions_info)