#!/usr/bin/python3
import argparse
import matplotlib
import matplotlib.pyplot as plt
from hurry.filesize import size

by_first = lambda x: x[0] 

parser = argparse.ArgumentParser(
    description='Create plot from stride status data.'
)
parser.add_argument('-i', '--info', dest='info')
parser.add_argument('-s', '--size', dest='size')
parser.add_argument('-p', '--plot', dest='plot', action='store_true')
args = parser.parse_args()
program_names = []
steady_instructions_percentages = []
steady_accesses_percentages = []
GBFACTOR = 1 << 30

program_sizes = {}
if args.size:
    with open(args.size, 'r') as info:
        line = info.readline()
        while line:
            split = line.split()
            if(split[0] == 'compressed'):
                line = info.readline()
                continue
            print(split[3].split('.')[0], size(int(split[1])))
            # print(split[3], split[1])
            program_sizes.update({split[3].split('.')[0]: float(split[1])})
            line = info.readline()

if args.info:
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

    steady_instructions_plot = list(zip(steady_instructions_percentages, program_names))
    steady_sizes = []
    steady_names = []
    for instruction in steady_instructions_plot:
        # steady_sizes.append(int(instruction[0]*program_sizes[instruction[1]]))
        # steady_names.append(instruction[1])
        steady_sizes.append((int(instruction[0]*program_sizes[instruction[1]]), instruction[1])) 
        print(instruction[1], size(int(instruction[0]*program_sizes[instruction[1]]))) 
    steady_sizes = sorted(steady_sizes, key=by_first)
    steady_sizes, steady_names = zip(*steady_sizes)
    steady_sizes = list(steady_sizes)
    steady_sizes_mean = sum([x/GBFACTOR for x in steady_sizes])/float(len(steady_sizes))

    steady_accesses_plot = list(zip(steady_accesses_percentages, program_names))

    steady_instructions_plot = sorted(steady_instructions_plot, key=by_first)
    steady_accesses_plot = sorted(steady_accesses_plot, key=by_first)

    steady_instructions_percentages, program_names = zip(*steady_instructions_plot)
    steady_accesses_percentages, program_names = zip(*steady_accesses_plot)

    if args.plot:
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

        plt.xlabel('Programs')
        plt.ylabel('Size Reduction in GB')
        plt.axhline(y=steady_sizes_mean, color='r', linestyle='--')
        steady_sizes = [x/GBFACTOR for x in steady_sizes]
        bar = plt.bar(range(len(steady_sizes)), steady_sizes, align='center', color='g')
        for rect in bar:
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width()/2.0, height, '%s' % size(int(height*GBFACTOR)), ha='center', va='bottom')
        plt.xticks(range(len(steady_sizes)), steady_names, rotation='vertical')
        plt.tight_layout()
        plt.savefig("size_reduction_plt.png")
        plt.show()
        plt.clf()
