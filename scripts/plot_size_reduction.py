#!/usr/bin/python3
import argparse
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from calmsize import size, ByteSize

by_first = lambda x: x[0]

parser = argparse.ArgumentParser(
    description='Create plot from stride status data.'
)
parser.add_argument('-i', '--info', dest='info')
parser.add_argument('-s', '--size', dest='size')
parser.add_argument('-p', '--plot', dest='plot', action='store_true')
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true')
args = parser.parse_args()

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

# aux
program_names = []
steady_instructions_percentages = []
steady_accesses_percentages = []

# le arquivo de informações dos acessos passado para a opção -i
if args.info:
    with open(args.info, 'r') as info:
        name = info.readline()
        total_instructions = info.readline()
        steady_instructions = info.readline()
        memory_accesses = info.readline()
        steady_accesses = info.readline()

        while name and total_instructions and steady_instructions:
            # processa linha
            name = name.split('.')[0]
            label1, total = total_instructions.split()
            label2, steady = steady_instructions.split()
            label3, total_accesses = memory_accesses.split()
            label4, steady_accesses = steady_accesses.split()

            # atualiza aux
            program_names.append(name)
            steady_instructions_percentages.append(float(steady)/float(total))
            steady_accesses_percentages.append(float(steady_accesses)/float(total_accesses))

            # le a proxima linha
            name = info.readline()
            total_instructions = info.readline()
            steady_instructions = info.readline()
            memory_accesses = info.readline()
            steady_accesses = info.readline()

    # calcula media das porcentagens
    instruction_percentages_mean = sum(steady_instructions_percentages)/float(len(steady_instructions_percentages))
    accesses_percentages_mean = sum(steady_accesses_percentages)/float(len(steady_accesses_percentages))

    # aux
    steady_instructions_plot = list(zip(steady_instructions_percentages, program_names))
    reduced_sizes = []
    reduced_names = []

    # calcula o tamanho da redução prevista para os traços uncompressed dos programas
    for program_steady_percentages in steady_instructions_plot:
        program_name = program_steady_percentages[1]
        steady_size = int(program_steady_percentages[0]*program_sizes[program_name])
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
        plt.xlabel('Programas')
        plt.ylabel('Tamanho do traço de memória em GB')
        axes = plt.gca()
        axes.set_ylim([0,4.6])

        # plota tamanho dos traços de memoria uncompressed
        whole_program_sizes = [program_sizes[program_name]/GBFACTOR for program_name in reduced_names]
        whole_sizes_bar = plt.bar(range(len(whole_program_sizes)), whole_program_sizes, align='center', color=( 1, 0.65, 0.65, 1), edgecolor='r')

        # plota tamanho das reduções dos traços de memoria uncompressed e sua média
        # plt.axhline(y=reduced_sizes_mean, color='r', linestyle='--')
        reduced_sizes = [x/GBFACTOR for x in reduced_sizes]
        reduced_sizes_bar = plt.bar(range(len(reduced_sizes)), reduced_sizes, align='center', color='r')

        # Escreve o valor da redução do traço em cima de cada barra
        for rects in zip(whole_sizes_bar, reduced_sizes_bar):
            whole_height = rects[0].get_height()
            reduced_height = rects[1].get_height()

            plt.text(rects[0].get_x() + rects[0].get_width()/2.0, whole_height+0.1, '-%s' % '{:.2f}'.format(size(int((whole_height - reduced_height)* GBFACTOR))), rotation='vertical', ha='center', va='bottom')

        # plota o nome dos programas no eixo x e seta os ticks do eixo y       
        plt.xticks(range(len(reduced_sizes)), reduced_names, rotation='vertical')
        plt.yticks(np.arange(0, 4.6, step=0.5))

        # salva o grafico plotado
        plt.tight_layout()
        plt.savefig("size_reduction_plt.png")
        plt.show()
        plt.clf()
