############################################################
# size_of_block = []
# bsize = 0
# # Count the amount of instructions in each basic block
# with open(args.stat_trace, "r") as stat:
#     line = stat.readline()
#     while line:
#         if not line.startswith("#"):
#             # assembler_instruction, opcode_type, instruction_addr,
#             # instruction_size, number_of_read_registers, read_registers,
#             # number_of_write_registers, write_registers, base_register,
#             # index_register, is_read_flag, is_read2_flag, is_write_flag,
#             # is_branch_flag, is_predicated_flag, is_prefetch_flag = line.split()

#             if line.startswith("@"):
#                 size_of_block.append(bsize)
#                 bsize = 0
#             else:
#                 bsize = bsize + 1

#         line = stat.readline()

#     size_of_block.append(bsize)

# # stride_histogram_per_block = [None, {}, {}, {}, ...]
# stride_histogram_per_block = [{} for x in range(0, len(size_of_block))]
# stride_histogram_per_block[0] = None

# last_address_seen_in_block = [0] * len(size_of_block)

# with open(args.mem_trace, "r") as mem:
#     line = mem.readline()
#     i = 0
#     while line:
#         if not line.startswith("#"):
#             if i >= 50:
#                 break
#             op, size, address, block = line.split()
#             # if int(block) == 5:
#             print(op, size, address, block)

#             # Calculo o stride subtraindo o endereço atual do último endereço visto
#             stride = int(address) - last_address_seen_in_block[int(block)]

#             # Atualizo o último endereço visto no bloco
#             last_address_seen_in_block[int(block)] = int(address)

#             # Se esse stride já aconteceu eu atualizo a contagem
#             if stride in stride_histogram_per_block[int(block)].keys():
#                 stride_count = stride_histogram_per_block[int(block)].get(stride) + 1

#             # Senão eu inicializo ele
#             else:
#                 stride_count = 1

#             # Atualizo o histograma do bloco correspondente
#             stride_histogram_per_block[int(block)].update({stride: stride_count})
#             i = i + 1

#         line = mem.readline()


# # print(stride_histogram_per_block)
# with open(args.output, "w") as output:
#     print(stride_histogram_per_block, file=output)
#     output.close()
#############################################################

# print(memory_instructions_in_block)

# # stride_histogram_per_block = [None, {}, {}, {}, ...]
# stride_histogram_per_block = [{} for x in range(0, len(size_of_block))]
# stride_histogram_per_block[0] = None

# last_address_seen_in_block = [0] * len(size_of_block)


#             stride = int(address) - last_address_seen_in_block[int(block)]
#             last_address_seen_in_block[int(block)] = int(address)
#             if stride in stride_histogram_per_block[int(block)].keys():
#                 stride_count = stride_histogram_per_block[int(block)].get(stride) + 1
#             else:
#                 stride_count = 1
#             stride_histogram_per_block[int(block)].update({stride: stride_count})
#             i = i + 1

#         line = mem.readline()


# print(stride_histogram_per_block)
# with open(args.output, "w") as output:
#     print(stride_histogram_per_block, file=output)
#     output.close()


# SEPARATE BLOCKS IN MEMORY TRACE
# with open(args.mem_trace, "r") as mem:
#     line = mem.readline()
#     i = 0
#     while line:
#         if line.startswith("#"):
#             line = mem.readline()
#             continue

#         if i >= 50:
#             break

#         j = 0
#         while True:
#             op, size, address, block = line.split()
#             print(op, size, address, block)
#             j = j + 1
#             if j < memory_instructions_in_block[int(block)]:
#                 line = mem.readline()
#             else:
#                 break

#         print()
#         line = mem.readline()
#         i = i + 1