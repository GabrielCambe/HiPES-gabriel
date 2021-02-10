#!/usr/bin/python3
import argparse
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.pyplot import figure

plt.rcParams.update({'font.size': 14})
    
by_first = lambda x: x[0] 

parser = argparse.ArgumentParser(
    description='Create plot from stride status data.'
)
parser.add_argument('-i', '--info', dest='info')
args = parser.parse_args()

def mean(array):
    return sum(array)/float(len(array))

def plot(label, mean, percentages, program_names, plot_filename):


    #plt.xlabel('Programs')
    plt.ylabel(label)

    #Linha 
    plt.axhline(y=mean, color='grey', linestyle='dotted')
    plt.text(mean-1.0, mean, '%d%%' % int(mean*100.0), rotation='horizontal', ha='center', va='bottom')

    axis = plt.gca()
    axis.grid(axis="y")
    axis.set_axisbelow(True)
    
    bar = plt.bar(range(len(percentages)), percentages, align='center', color='k', edgecolor = 'k')
    # Labels
    for rect in bar:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width()/2.0, height + 0.02, '%d%%' % int(height*100.0), rotation='vertical', ha='center', va='bottom')
    
    plt.xticks(range(len(percentages)), program_names, rotation='vertical', color='k')
    plt.yticks(np.arange(0, 1.1, step=0.1), color='k')
    
    plt.tight_layout()
    
    plt.savefig(plot_filename)
    plt.show()
    plt.clf()

#aux
program_names = []
cache_conflicts_percents = []
iSteady_instructions_acesses_percents = []
pSteady_accesses_percents = []
iSteady_accesses_percents = []



with open(args.info, 'r') as info:
    
    name = info.readline()
    memory_instructions_fetched_line = info.readline()
    memory_instructions_analysed_line = info.readline()
    cache_conflicts_line = info.readline()
    memory_instructions_counted_line = info.readline()
    partially_steady_instructions_line = info.readline()
    integrally_steady_instructions_line = info.readline()
    accesses_in_integrally_steady_instructions_line = info.readline()
    memory_accesses_line = info.readline()
    read_accesses_line = info.readline()
    read2_accesses_line = info.readline()
    write_accesses_line = info.readline()
    partially_steady_accesses_line = info.readline()
    integrally_steady_accesses_line = info.readline()

    while name:
        # processa linha
        name = name.split('.')[0]
        label0, memory_instructions_fetched = memory_instructions_fetched_line.split()
        label1, memory_instructions_analysed = memory_instructions_analysed_line.split()
        label2, cache_conflicts = cache_conflicts_line.split()
        label3, memory_instructions_counted = memory_instructions_counted_line.split()
        label4, partially_steady_instructions = partially_steady_instructions_line.split()
        label5, integrally_steady_instructions = integrally_steady_instructions_line.split()
        label12, accesses_in_integrally_steady_instructions = accesses_in_integrally_steady_instructions_line.split()
        label6, memory_accesses = memory_accesses_line.split()
        label7, read_accesses = read_accesses_line.split()
        label8, read2_accesses = read2_accesses_line.split()
        label9, write_accesses = write_accesses_line.split()
        label10, partially_steady_accesses = partially_steady_accesses_line.split()
        label11, integrally_steady_accesses = integrally_steady_accesses_line.split()

        try:
            assert int(accesses_in_integrally_steady_instructions) == int(integrally_steady_instructions)
            assert int(memory_instructions_analysed) == int(memory_instructions_counted)
            assert int(memory_accesses) == int(read_accesses) + int(read2_accesses) + int(write_accesses)
            assert float(cache_conflicts)/float(memory_instructions_fetched) < 0.01
        except AssertionError:
            print(name, cache_conflicts, memory_instructions_fetched)
            print(float(cache_conflicts)/float(memory_instructions_fetched))
            print(int(accesses_in_integrally_steady_instructions) == int(integrally_steady_instructions))

        # atualiza aux
        program_names.append(name)
        cache_conflicts_percents.append(float(cache_conflicts)/float(memory_instructions_fetched))
        iSteady_instructions_acesses_percents.append(float(accesses_in_integrally_steady_instructions)/float(memory_accesses))
        pSteady_accesses_percents.append(float(partially_steady_accesses)/float(memory_accesses))
        iSteady_accesses_percents.append(float(integrally_steady_accesses)/float(memory_accesses))

        # le próxima linha
        name = info.readline()
        memory_instructions_fetched_line = info.readline()
        memory_instructions_analysed_line = info.readline()
        cache_conflicts_line = info.readline()
        memory_instructions_counted_line = info.readline()
        partially_steady_instructions_line = info.readline()
        integrally_steady_instructions_line = info.readline()
        accesses_in_integrally_steady_instructions_line = info.readline()
        memory_accesses_line = info.readline()
        read_accesses_line = info.readline()
        read2_accesses_line = info.readline()
        write_accesses_line = info.readline()
        partially_steady_accesses_line = info.readline()
        integrally_steady_accesses_line = info.readline()

iSteady_instructions_acesses_percents_mean = mean(iSteady_instructions_acesses_percents)
pSteady_accesses_percents_mean = mean(pSteady_accesses_percents)
iSteady_accesses_percents_mean = mean(iSteady_accesses_percents)

iSteady_instructions_accesses_plot = zip(iSteady_instructions_acesses_percents, program_names)
pSteady_accesses_plot = zip(pSteady_accesses_percents, program_names)
iSteady_accesses_plot = zip(iSteady_accesses_percents, program_names)

iSteady_instructions_accesses_plot = sorted(iSteady_instructions_accesses_plot, key=by_first)
pSteady_accesses_plot = sorted(pSteady_accesses_plot, key=by_first)
iSteady_accesses_plot = sorted(iSteady_accesses_plot, key=by_first)

iSteady_instructions_acesses_percents, program_names = zip(*iSteady_instructions_accesses_plot)
pSteady_accesses_percents, program_names = zip(*pSteady_accesses_plot)
iSteady_accesses_percents, program_names = zip(*iSteady_accesses_plot)

figure(num=None, figsize=(8, 8), dpi=80, facecolor='w', edgecolor='k')
plot(
    'Acessos em instruções integralmente regulares',
    iSteady_instructions_acesses_percents_mean,
    iSteady_instructions_acesses_percents,
    program_names,
    "integrally_steady_instructions_plt.pdf"
)

# Não Incluso
# plot(
#     'Acessos regulares',
#     pSteady_accesses_percents_mean,
#     pSteady_accesses_percents,
#     program_names,
#     "steady_accesses_plt.png"
# )

figure(num=None, figsize=(8, 8), dpi=80, facecolor='w', edgecolor='k')
plot(
    'Acessos integralmente regulares',
    iSteady_accesses_percents_mean,
    iSteady_accesses_percents,
    program_names,
    "integrally_steady_accesses_plt.pdf"
)
