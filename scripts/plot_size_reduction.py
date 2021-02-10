#!/usr/bin/python3
import argparse
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from calmsize import size, ByteSize
from matplotlib.pyplot import figure
figure(num=None, figsize=(10, 6), dpi=80, facecolor='w', edgecolor='k')
plt.rcParams.update({'font.size': 14})

by_first = lambda x: x[0]

parser = argparse.ArgumentParser(
    description='Create plot from stride status data.'
)
parser.add_argument('-i', '--info', dest='info')
parser.add_argument('-s', '--size', dest='size')
parser.add_argument('-p', '--plot', dest='plot', action='store_true')
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true')
args = parser.parse_args()

def mean(array):
    return sum(array)/float(len(array))

# aux
program_sizes = {}
GBFACTOR = 1 << 30

# le o arquivo de tamanhos passados pra opção -s
if args.size:
    with open(args.size, 'r') as info:
        line = info.readline()
        while line:
            split = line.split()

            # se a linha começa com a palavra uncompressed ela é cabeçalho
            if(split[0] == 'compressed'):
                line = info.readline()
                continue
            
            # pega a coluna uncompressed
            program_sizes.update({split[3].split('.')[0]: float(split[1])})
            line = info.readline()

if args.verbose:
    print(program_sizes, end="\n\n")

#aux
program_names = []
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
        label6, memory_accesses = memory_accesses_line.split()
        label7, read_accesses = read_accesses_line.split()
        label8, read2_accesses = read2_accesses_line.split()
        label9, write_accesses = write_accesses_line.split()
        label10, partially_steady_accesses = partially_steady_accesses_line.split()
        label11, integrally_steady_accesses = integrally_steady_accesses_line.split()

        try:
            assert int(memory_instructions_analysed) == int(memory_instructions_counted)
            assert int(memory_accesses) == int(read_accesses) + int(read2_accesses) + int(write_accesses)
            assert float(cache_conflicts) / float(memory_instructions_fetched) < 0.01
        except AssertionError:
            print(name, cache_conflicts, memory_instructions_fetched)
            print(float(cache_conflicts)/float(memory_instructions_fetched))

        # atualiza aux
        program_names.append(name)
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

    iSteady_accesses_percents_mean = mean(iSteady_accesses_percents)

    # aux
    iSteady_accesses_percents_plot = list(zip(iSteady_accesses_percents, program_names))
    reduced_sizes = []
    reduced_names = []

    # calcula o tamanho da redução prevista para os traços uncompressed dos programas
    for program_steady_percentage in iSteady_accesses_percents_plot:
        program_name = program_steady_percentage[1]
        steady_size = int(program_steady_percentage[0]*program_sizes[program_name])
        reduced_size = program_sizes[program_name] - steady_size
        reduced_sizes.append((reduced_size, program_name))

    # ordena os tamanhos das reduções
    reduced_sizes = sorted(reduced_sizes, key=by_first)
    reduced_sizes, reduced_names = zip(*reduced_sizes)
    reduced_sizes = list(reduced_sizes)
    # calcula media das reduções
    reduced_sizes_mean = sum([x/GBFACTOR for x in reduced_sizes])/float(len(reduced_sizes))


    if args.plot:
        # seta os labels dos eixos e o tamanho máximo do eixo y
        #plt.xlabel('Programas')
        plt.ylabel('Tamanho do traço de memória em GB')
        axes = plt.gca()
        axes.set_ylim([0,4.7])
        axes.grid(axis="y")
        axes.set_axisbelow(True)



        # plota tamanho dos traços de memoria uncompressed
        whole_program_sizes = [program_sizes[program_name]/GBFACTOR for program_name in reduced_names]
        whole_sizes_bar = plt.bar(range(len(whole_program_sizes)), whole_program_sizes, align='center', color='grey', edgecolor='k')

        # plota tamanho das reduções dos traços de memoria uncompressed e sua média
        # plt.axhline(y=reduced_sizes_mean, color='r', linestyle='--')
        reduced_sizes = [x/GBFACTOR for x in reduced_sizes]
        reduced_sizes_bar = plt.bar(range(len(reduced_sizes)), reduced_sizes, align='center', color='k')

        # Escreve o valor da redução do traço em cima de cada barra
        for rects in zip(whole_sizes_bar, reduced_sizes_bar):
            whole_height = rects[0].get_height()
            reduced_height = rects[1].get_height()

            plt.text(rects[0].get_x() + rects[0].get_width()/2.0, whole_height+0.1, '-%s' % '{:.2f}'.format(size(int((whole_height - reduced_height)* GBFACTOR))), rotation='vertical', ha='center', va='bottom')

        # plota o nome dos programas no eixo x e seta os ticks do eixo y       
        plt.xticks(range(len(reduced_sizes)), reduced_names, rotation='vertical')
        plt.yticks(np.arange(0, 5, step=0.5))

        # salva o grafico plotado
        plt.tight_layout()
        plt.savefig("size_reduction_plt.pdf")
        plt.show()
        plt.clf()
