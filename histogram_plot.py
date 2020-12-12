# #!./pypy3.7-v7.3.2-linux64/bin/pypy3
# import argparse
# import matplotlib
# import matplotlib.pyplot as plt

# parser = argparse.ArgumentParser(
#     description="Create memory stride histogram from memory trace."
# )
# parser.add_argument("-mem", "--memory_trace", dest="mem_trace")
# parser.add_argument("-stat", "--static_trace", dest="stat_trace")
# parser.add_argument("-out", "--output", dest="output")
# parser.add_argument("-v", "--verbose", action="store_true")
# args = parser.parse_args()


# for instruction_address in memory_instructions_info.keys():
#     fig, ax = plt.subplots(3)
#     fig.suptitle("Instruction in address " + instruction_address)
#     print(list(memory_instructions_info[instruction_address]['access1_strides'].keys()))
#     print(memory_instructions_info[instruction_address]['access1_strides'].values())
#     ax[0].bar(
#         list(memory_instructions_info[instruction_address]['access1_strides'].keys())[1:],
#         list(memory_instructions_info[instruction_address]['access1_strides'].values())[1:],
#         color='b'
#     )
#     # ax2.bar(
#     #     list(memory_instructions_info[instruction_address]['access2_strides'].keys()),
#     #     memory_instructions_info[instruction_address]['access2_strides'].values(),
#     #     color='b', label='read2'
#     # )
#     # ax3.bar(
#     #     list(memory_instructions_info[instruction_address]['access3_strides'].keys()),
#     #     memory_instructions_info[instruction_address]['access3_strides'].values(),
#     #     color='g', label='write'
#     # )
#     plt.show()
#     break



# #!../pypy3.7-v7.3.2-linux64/bin/pypy3
# import argparse
# import simplejson as json
# import matplotlib
# import matplotlib.pyplot as plt

# class StatusMachine(object):
#     current_status = 'LEARN'
#     last_stride = None
        
#     def StatusMachine(self):
#         pass

#     def update(self, stride):
#         last_status = self.current_status

#         if last_status == 'LEARN':
#             if stride:
#                 self.status = 'STEADY' 

#         elif last_status == 'STEADY':
#             if self.last_stride == stride:
#                 self.status = 'STEADY'
#             else: 
#                 self.status = 'NON-LINEAR' 

#         elif last_status == 'NON-LINEAR':
#             pass

#         return last_status

# parser = argparse.ArgumentParser(
#     description="Create memory stride histogram from memory trace."
# )
# parser.add_argument("-t", "--trace", dest="trace")
# args = parser.parse_args()

# program_name = 'astar'

# def updateStrideInAccess(info, address, access):
#     if info["last_address_in_" + access]:
#         stride = int(address) - info["last_address_in_" + access]
#     else:
#         stride = int(address)

#     if stride in info[access + "_strides"].keys():
#         info[access + "_strides"].update(
#             {stride: info[access + "_strides"][stride] + 1}
#         )
#     else:
#         info[access + "_strides"].update({stride: 1})

#     info.update({"last_address_in_" + access: int(address)})
#     return info

# memory_instructions_info = {}
# with open(args.trace, "r") as mem:
#     line = mem.readline()
#     i = 0
#     while line:
#         i += 1
#         if i == 100:
#             break

#         instruction, read_address, read2_address, write_address = line.split()
#         info = {
#             "access1_strides": {},
#             "last_address_in_access1": None,
#             "access2_strides": {},
#             "last_address_in_access2": None,
#             "access3_strides": {},
#             "last_address_in_access3": None,
#             "count": 0,
#         }

#         if read_address != "-1":
#             if instruction in memory_instructions_info.keys():
#                 info = updateStrideInAccess(memory_instructions_info[instruction], read_address, "access1")
#             else:
#                 info = updateStrideInAccess(info, read_address, "access1")
                
#         if read2_address != "-1":
#             if instruction in memory_instructions_info.keys():
#                 info = updateStrideInAccess(memory_instructions_info[instruction], read2_address, "access2")
#             else:
#                 info = updateStrideInAccess(info, read2_address, "access2")

#         if write_address != "-1":
#             if instruction in memory_instructions_info.keys():
#                 info = updateStrideInAccess(memory_instructions_info[instruction], write_address, "access3")
#             else:
#                 info = updateStrideInAccess(info, write_address, "access3")

#         info.update({"count": info["count"] + 1})
#         memory_instructions_info.update({instruction: info})
#         line = mem.readline()


# with open("strides_" + program_name + ".json", "w+") as memory_info_json:
#     json.dump(memory_instructions_info, memory_info_json)


# info = {
#     "access1_strides": {},
#     "access2_strides": {},
#     "access3_strides": {},
# }
# for instruction_address in memory_instructions_info.keys():
#     info["access1_strides"].update(memory_instructions_info[instruction_address]["access1_strides"])
#     info["access2_strides"].update(memory_instructions_info[instruction_address]["access2_strides"])
#     info["access3_strides"].update(memory_instructions_info[instruction_address]["access3_strides"])

# print(info)

# # fig, ax = plt.subplots(3)
# # fig.suptitle("Stride Histograms")
# print(list(info['access1_strides'].keys()))
# # count = [ x*100 for x in ]

# plt.bar(range(len(list(info['access1_strides'].values()))), list(info['access1_strides'].values()), align='center', color='r')
# plt.xticks(range(len(list(info['access1_strides'].values()))), list(info['access1_strides'].keys()))

# # ax[1].bar(
# #     list(info['access2_strides'].keys())[1:],
# #     list(info['access2_strides'].values())[1:],
# #     color='b', label='read2'
# # )

# # ax[2].bar(
# #     list(info['access3_strides'].keys())[1:],
# #     list(info['access3_strides'].values())[1:],
# #     color='g', label='write'
# # )

# plt.show()
