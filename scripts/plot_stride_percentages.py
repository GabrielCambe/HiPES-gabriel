#!/usr/bin/python3
import argparse
import matplotlib
import matplotlib.pyplot as plt

by_first = lambda x: x[0] 

parser = argparse.ArgumentParser(
    description='Create plot from stride status data.'
)
parser.add_argument('-i', '--info', dest='info')
args = parser.parse_args()
program_names = []
steady_instructions_percentages = []
steady_accesses_percentages = []

with open(args.info, 'r') as info:
    name = info.readline()
    total_instructions = info.readline()
    steady_instructions = info.readline()
    memory_accesses = info.readline()
    steady_accesses = info.readline()

    while name and total_instructions and steady_instructions:
        name = name.split('.')[0]
        label1, total = total_instructions.split()
        label2, steady = steady_instructions.split()
        label3, total_accesses = memory_accesses.split()
        label4, steady_accesses = steady_accesses.split()

        program_names.append(name)
        steady_instructions_percentages.append(float(steady)/float(total))
        steady_accesses_percentages.append(float(steady_accesses)/float(total_accesses))

        name = info.readline()
        total_instructions = info.readline()
        steady_instructions = info.readline()
        memory_accesses = info.readline()
        steady_accesses = info.readline()

instruction_percentages_mean = sum(steady_instructions_percentages)/float(len(steady_instructions_percentages))
accesses_percentages_mean = sum(steady_accesses_percentages)/float(len(steady_accesses_percentages))

steady_instructions_plot = zip(steady_instructions_percentages, program_names)
steady_accesses_plot = zip(steady_accesses_percentages, program_names)

steady_instructions_plot = sorted(steady_instructions_plot, key=by_first)
steady_accesses_plot = sorted(steady_accesses_plot, key=by_first)

steady_instructions_percentages, program_names = zip(*steady_instructions_plot)
steady_accesses_percentages, program_names = zip(*steady_accesses_plot)

plt.xlabel('Programs')
plt.ylabel('Integral Steady Accesses')
plt.axhline(y=instruction_percentages_mean, color='r', linestyle='--')
bar = plt.bar(range(len(steady_instructions_percentages)), steady_instructions_percentages, align='center', color='g')
for rect in bar:
    height = rect.get_height()
    plt.text(rect.get_x() + rect.get_width()/2.0, height, '%d%%' % int(height*100.0), ha='center', va='bottom')
plt.xticks(range(len(steady_instructions_percentages)), program_names, rotation='vertical')
plt.tight_layout()
plt.savefig("integrally_memory_accesses_plt.png")
plt.show()
plt.clf()

plt.xlabel('Programs')
plt.ylabel('Steady Accesses')
plt.axhline(y=accesses_percentages_mean, color='r', linestyle='--')
bar = plt.bar(range(len(steady_accesses_percentages)), steady_accesses_percentages, align='center', color='g')
for rect in bar:
    height = rect.get_height()
    plt.text(rect.get_x() + rect.get_width()/2.0, height, '%d%%' % int(height*100.0), ha='center', va='bottom')
plt.xticks(range(len(steady_accesses_percentages)), program_names, rotation='vertical')
plt.tight_layout()
plt.savefig("partially_memory_accesses_plt.png")
plt.show()
