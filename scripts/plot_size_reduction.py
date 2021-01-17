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
    steady_sizes = []
    steady_names = []

    # calcula o tamanho da redução prevista para os traços uncompressed dos programas
    for program_steady_percentages in steady_instructions_plot:
        steady_sizes.append((int(program_steady_percentages[0]*program_sizes[program_steady_percentages[1]]), program_steady_percentages[1])) 

    # ordena os tamanhos das reduções
    steady_sizes = sorted(steady_sizes, key=by_first)
    steady_sizes, steady_names = zip(*steady_sizes)
    steady_sizes = list(steady_sizes)
    # calcula media das reduções
    steady_sizes_mean = sum([x/GBFACTOR for x in steady_sizes])/float(len(steady_sizes))

    ##
    # steady_accesses_plot = list(zip(steady_accesses_percentages, program_names))

    # steady_instructions_plot = sorted(steady_instructions_plot, key=by_first)
    # steady_accesses_plot = sorted(steady_accesses_plot, key=by_first)

    # steady_instructions_percentages, program_names = zip(*steady_instructions_plot)
    # steady_accesses_percentages, program_names = zip(*steady_accesses_plot)

    if args.plot:
        # plt.xlabel('Programs')
        # plt.ylabel('Integral Steady Accesses')
        # plt.axhline(y=instruction_percentages_mean, color='r', linestyle='--')
        # bar = plt.bar(range(len(steady_instructions_percentages)), steady_instructions_percentages, align='center', color='g')
        # for rect in bar:
        #     height = rect.get_height()
        #     plt.text(rect.get_x() + rect.get_width()/2.0, height, '%d%%' % int(height*100.0), ha='center', va='bottom')
        # plt.xticks(range(len(steady_instructions_percentages)), program_names, rotation='vertical')
        # plt.tight_layout()
        # plt.savefig("integrally_memory_accesses_plt.png")
        # plt.show()
        # plt.clf()

        # plt.xlabel('Programs')
        # plt.ylabel('Steady Accesses')
        # plt.axhline(y=accesses_percentages_mean, color='r', linestyle='--')
        # bar = plt.bar(range(len(steady_accesses_percentages)), steady_accesses_percentages, align='center', color='g')
        # for rect in bar:
        #     height = rect.get_height()
        #     plt.text(rect.get_x() + rect.get_width()/2.0, height, '%d%%' % int(height*100.0), ha='center', va='bottom')
        # plt.xticks(range(len(steady_accesses_percentages)), program_names, rotation='vertical')
        # plt.tight_layout()
        # plt.savefig("partially_memory_accesses_plt.png")
        # plt.show()

        # labels dos eixos
        plt.xlabel('Programs')
        plt.ylabel('Size Reduction in GB')

        # plota tamanho dos traços de memoria uncompressed
        whole_program_sizes = [program_sizes[program_name]/GBFACTOR for program_name in steady_names]
        whole_program_sizes_bar = plt.bar(range(len(whole_program_sizes)), whole_program_sizes, align='center', color='b')

        # plota tamanho das reduções dos traços de memoria uncompressed e sua média e escreve o valor em cima de cada barra
        plt.axhline(y=steady_sizes_mean, color='r', linestyle='--')
        steady_sizes = [x/GBFACTOR for x in steady_sizes]
        bar = plt.bar(range(len(steady_sizes)), steady_sizes, align='center', color='g')
        for rect in bar:
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width()/2.0, height, '%s' % size(int(height*GBFACTOR)), ha='center', va='bottom')

        # plota o nome dos programas no eixo x        
        plt.xticks(range(len(steady_sizes)), steady_names, rotation='vertical')

        # salva o grafico plotado
        plt.tight_layout()
        plt.savefig("size_reduction_plt.png")
        plt.show()
        plt.clf()
