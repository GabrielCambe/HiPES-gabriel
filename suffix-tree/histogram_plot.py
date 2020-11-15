#!./pypy3.7-v7.3.2-linux64/bin/pypy3
import argparse
import matplotlib
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(
    description="Create memory stride histogram from memory trace."
)
parser.add_argument("-mem", "--memory_trace", dest="mem_trace")
parser.add_argument("-stat", "--static_trace", dest="stat_trace")
parser.add_argument("-out", "--output", dest="output")
parser.add_argument("-v", "--verbose", action="store_true")
args = parser.parse_args()


for instruction_address in memory_instructions_info.keys():
    fig, ax = plt.subplots(3)
    fig.suptitle("Instruction in address " + instruction_address)
    print(list(memory_instructions_info[instruction_address]['access1_strides'].keys()))
    print(memory_instructions_info[instruction_address]['access1_strides'].values())
    ax[0].bar(
        list(memory_instructions_info[instruction_address]['access1_strides'].keys())[1:],
        list(memory_instructions_info[instruction_address]['access1_strides'].values())[1:],
        color='b'
    )
    # ax2.bar(
    #     list(memory_instructions_info[instruction_address]['access2_strides'].keys()),
    #     memory_instructions_info[instruction_address]['access2_strides'].values(),
    #     color='b', label='read2'
    # )
    # ax3.bar(
    #     list(memory_instructions_info[instruction_address]['access3_strides'].keys()),
    #     memory_instructions_info[instruction_address]['access3_strides'].values(),
    #     color='g', label='write'
    # )
    plt.show()
    break