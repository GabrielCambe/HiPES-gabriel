#!/usr/bin/python3
import argparse
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
by_first = lambda x: x[0] 

parser = argparse.ArgumentParser(
    description='Create plot from stride status data.'
)
parser.add_argument('-i', '--info', dest='info')
args = parser.parse_args()

def mean(array):
    return sum(array)/float(len(array))

def plot(label, mean, percentages, program_names, plot_filename):
    plt.xlabel('Programs')
    plt.ylabel(label)
    plt.axhline(y=mean, color='r', linestyle='--')
    bar = plt.bar(range(len(percentages)), percentages, align='center', color='g')
    for rect in bar:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width()/2.0, height + 0.02, '%d%%' % int(height*100.0), rotation='vertical', ha='center', va='bottom')
    plt.xticks(range(len(percentages)), program_names, rotation='vertical')
    plt.yticks(np.arange(0, 1.1, step=0.1))
    plt.tight_layout()
    plt.savefig(plot_filename)
    plt.show()
    plt.clf()

#aux
program_names = []
cache_conflicts_percents = []
pSteady_instructions_percents = []
iSteady_instructions_percents = []
pSteady_accesses_percents = []
iSteady_accesses_percents = []


# le arquivo de informações dos acessos passado para a opção -i
with open(args.info, 'r') as info:
    # lê primeira linha
    name = info.readline()
    memory_instructions_fetched_line = info.readline()
    memory_instructions_analysed_line = info.readline()
    cache_conflicts_line = info.readline()
    memory_instructions_counted_line = info.readline()
    partially_steady_instructions_line = info.readline()
    integrally_steady_instructions_line = info.readline()
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
        label6, memory_accesses = memory_accesses_line.split()
        label7, read_accesses = read_accesses_line.split()
        label8, read2_accesses = read2_accesses_line.split()
        label9, write_accesses = write_accesses_line.split()
        label10, partially_steady_accesses = partially_steady_accesses_line.split()
        label11, integrally_steady_accesses = integrally_steady_accesses_line.split()

        try:
            assert int(memory_instructions_analysed) == int(memory_instructions_counted)
            assert int(memory_accesses) == int(read_accesses) + int(read2_accesses) + int(write_accesses)
            assert float(cache_conflicts)/float(memory_instructions_fetched) < 0.01
        except AssertionError:
            print(name, cache_conflicts, memory_instructions_fetched)
            print(float(cache_conflicts)/float(memory_instructions_fetched))

        # atualiza aux
        program_names.append(name)
        cache_conflicts_percents.append(float(cache_conflicts)/float(memory_instructions_fetched))
        pSteady_instructions_percents.append(float(partially_steady_instructions)/float(memory_instructions_fetched))
        iSteady_instructions_percents.append(float(integrally_steady_instructions)/float(memory_instructions_fetched))
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
        memory_accesses_line = info.readline()
        read_accesses_line = info.readline()
        read2_accesses_line = info.readline()
        write_accesses_line = info.readline()
        partially_steady_accesses_line = info.readline()
        integrally_steady_accesses_line = info.readline()

pSteady_instructions_percents_mean = mean(pSteady_instructions_percents)
iSteady_instructions_percents_mean = mean(iSteady_instructions_percents)
pSteady_accesses_percents_mean = mean(pSteady_accesses_percents)
iSteady_accesses_percents_mean = mean(iSteady_accesses_percents)

pSteady_instructions_plot = zip(pSteady_instructions_percents, program_names)
iSteady_instructions_plot = zip(iSteady_instructions_percents, program_names)
pSteady_accesses_plot = zip(pSteady_accesses_percents, program_names)
iSteady_accesses_plot = zip(iSteady_accesses_percents, program_names)

pSteady_instructions_plot = sorted(pSteady_instructions_plot, key=by_first)
iSteady_instructions_plot = sorted(iSteady_instructions_plot, key=by_first)
pSteady_accesses_plot = sorted(pSteady_accesses_plot, key=by_first)
iSteady_accesses_plot = sorted(iSteady_accesses_plot, key=by_first)

pSteady_instructions_percents, program_names = zip(*pSteady_instructions_plot)
iSteady_instructions_percents, program_names = zip(*iSteady_instructions_plot)
pSteady_accesses_percents, program_names = zip(*pSteady_accesses_plot)
iSteady_accesses_percents, program_names = zip(*iSteady_accesses_plot)

plot(
    'Instruções regulares',
    pSteady_instructions_percents_mean,
    pSteady_instructions_percents,
    program_names,
    "steady_instructions_plt.png"
)

plot(
    'Instruções integralmente regulares',
    iSteady_instructions_percents_mean,
    iSteady_instructions_percents,
    program_names,
    "integrally_steady_instructions_plt.png"
)

plot(
    'Acessos regulares',
    pSteady_accesses_percents_mean,
    pSteady_accesses_percents,
    program_names,
    "steady_accesses_plt.png"
)

plot(
    'Acessos integralmente regulares',
    iSteady_accesses_percents_mean,
    iSteady_accesses_percents,
    program_names,
    "integrally_steady_accesses_plt.png"
)
