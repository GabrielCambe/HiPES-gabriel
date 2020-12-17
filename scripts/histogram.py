#!/usr/bin/python3
import argparse
import matplotlib
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(
    description='Createplot.'
)
parser.add_argument('-i', '--info', dest='info')
args = parser.parse_args()
program_names = []
steady_accesses_percentages = []
with open(args.info, 'r') as info:
    name = info.readline()
    total_instructions = info.readline()
    steady_instructions = info.readline()
    while name and total_instructions and steady_instructions:
        name = name.split('.')[0]
        label1, total = total_instructions.split()
        label2, steady = steady_instructions.split()

        program_names.append(name)
        steady_accesses_percentages.append(int(steady)/int(total))

        name = info.readline()
        total_instructions = info.readline()
        steady_instructions = info.readline()

percentages_mean = sum(steady_accesses_percentages)/float(len(steady_accesses_percentages))

# print(program_names)
# print(steady_accesses_percentages)
# print(percentages_mean)

plt.axhline(y=percentages_mean, color='r', linestyle='--')
plt.bar(range(len(steady_accesses_percentages)), steady_accesses_percentages, align='center', color='g')
plt.xticks(range(len(steady_accesses_percentages)), program_names, rotation='vertical')
plt.tight_layout()
plt.show()
