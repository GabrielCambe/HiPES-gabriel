#!./pypy3.7-v7.3.2-linux64/bin/pypy3
import argparse
import simplejson as json

parser = argparse.ArgumentParser(
    description="Create memory stride histogram from memory trace."
)
parser.add_argument("-mem", "--memory_trace", dest="mem_trace")
parser.add_argument("-stat", "--static_trace", dest="stat_trace")
parser.add_argument("-out", "--output", dest="output")
parser.add_argument("-v", "--verbose", action="store_true")
args = parser.parse_args()

program_name = args.stat_trace.split('.')[0]
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


stat_trace_aux = []
stat_trace = []
with open(args.stat_trace, "r") as stat:
    line = stat.readline()
    while line:
        if line.startswith("#"):
            line = stat.readline()
            continue

        if line.startswith("@"):
            stat_trace.append(stat_trace_aux)
            stat_trace_aux = []

        else:
            line_iter = iter(line.split())
            was_memory_instruction = False
            instruction = {}
            instruction_fields_iter = iter([
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
            ])
            while True:
                try:
                    instruction_field = next(instruction_fields_iter)
                    instruction_field_value = next(line_iter)

                    if (
                        instruction_field == "number_of_read_registers"
                        or instruction_field == "number_of_write_registers"
                    ):
                        instruction = write_next_fields(instruction, instruction_field, instruction_field_value, instruction_fields_iter, line_iter)
       
                    elif (
                        (instruction_field == "is_read_flag" or instruction_field == "is_write_flag")
                        and instruction_field_value == "1"
                    ):
                        instruction.update(
                            {instruction_field: instruction_field_value}
                        )
                        was_memory_instruction = True

                    elif (
                        instruction_field == "is_read2_flag"
                        and instruction_field_value == "1"
                    ):
                        instruction.update(
                            {instruction_field: instruction_field_value}
                        )
                        was_memory_instruction = True

                    else:
                        instruction.update(
                            {instruction_field: instruction_field_value}
                        )

                except StopIteration:
                    if was_memory_instruction:
                        stat_trace_aux.append(instruction)
                    break

        line = stat.readline()

    stat_trace.append(stat_trace_aux)

with open("stat_memory_instructions_" + program_name + ".json", "w+") as stat_info_json:
    json.dump(stat_trace, stat_info_json)


def updateStrideInAccess(info, address, access):
    if info["last_address_in_" + access]:
        stride = int(address) - info["last_address_in_" + access]
    else:
        stride = int(address)

    if stride in info[access + "_strides"].keys():
        info[access + "_strides"].update(
            {stride: info[access + "_strides"][stride] + 1}
        )
    else:
        info[access + "_strides"].update({stride: 1})

    info.update({"last_address_in_" + access: int(address)})
    return info

i = 0
memory_instructions_info = {}
with open(args.mem_trace, "r") as mem:
    line = mem.readline()
    while line:
        if line.startswith("#"):
            line = mem.readline()
            continue
        i += 1
        if i == 15:
            break
        op, size, address, block = line.split()
        blk = int(block)
        for j in range(len(stat_trace[blk])):
            print(blk, j)
            print(stat_trace[blk][j])
            print(line)

            op, size, address, block = line.split()
            instruction = stat_trace[blk][j]["instruction_addr"]
            info = {
                "access1_strides": {},
                "last_address_in_access1": None,
                "access2_strides": {},
                "last_address_in_access2": None,
                "access3_strides": {},
                "last_address_in_access3": None,
                "count": 0,
            }

            if stat_trace[blk][j]["is_read_flag"] == "1":
                if instruction in memory_instructions_info.keys():
                    info = updateStrideInAccess(memory_instructions_info[instruction], address, "access1")
                else:
                    info = updateStrideInAccess(info, address, "access1")
                
            elif stat_trace[blk][j]["is_read2_flag"] == "1":
                if instruction in memory_instructions_info.keys():
                    info = updateStrideInAccess(memory_instructions_info[instruction], address, "access1")

                    line = mem.readline()
                    op, size, address, block = line.split()

                    info = updateStrideInAccess(info, address, "access2")
                else:
                    info = updateStrideInAccess(info, address, "access1")

                    line = mem.readline()
                    op, size, address, block = line.split()

                    info = updateStrideInAccess(info, address, "access2")

            if stat_trace[blk][j]["is_write_flag"] == "1":
                if instruction in memory_instructions_info.keys():
                    info = updateStrideInAccess(memory_instructions_info[instruction], address, "access3")
                else:
                    info = updateStrideInAccess(info, address, "access3")

            info.update({"count": info["count"] + 1})
            memory_instructions_info.update({instruction: info})
            line = mem.readline()

with open("strides_" + program_name + ".json", "w+") as memory_info_json:
    json.dump(memory_instructions_info, memory_info_json)
