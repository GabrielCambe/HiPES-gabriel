#!/usr/bin/python3
import argparse
import numpy as np

parser = argparse.ArgumentParser(
    description='Check sanity of stride analysis output.'
)
parser.add_argument('-f', '--file', dest='file')
parser.add_argument('-v', '--verbose', action='store_true')
args = parser.parse_args()

stride_analysis_info = {}
if args.file:
    with open(args.file, 'r') as argfile:
        line = argfile.readline()
        while line:
            line = line.replace(":", " ")
            split = line.split()

            if len(split) == 0:
                line = argfile.readline()
                continue

            elif split[0].startswith("#") or split[0] == 'End' or split[0] == 'trace_reader_t' or split[0] == 'processor_t' or split[0] == 'Counting':
                line = argfile.readline()
                continue

            if (split[0].startswith(".")):
                trace_name = split[0]
                line = argfile.readline()
                continue

            # if args.verbose:
            #     print(split)
            
            stride_analysis_info[split[0]] = int(split[1])

            line = argfile.readline()

    if args.verbose:
        print(stride_analysis_info)

    if stride_analysis_info['memory_instructions_fetched'] != stride_analysis_info['memory_instructions_analysed'] + stride_analysis_info['cache_conflicts']:
        print ('\nFailed memory_instructions_fetched == memory_instructions_analysed + cache_conflicts')
        print ('memory_instructions_fetched: ', stride_analysis_info['memory_instructions_fetched'])
        print ('memory_instructions_analysed: ', stride_analysis_info['memory_instructions_analysed'])
        print ('cache_conflicts: ', stride_analysis_info['cache_conflicts'])
    else:
        print ('\nPassed memory_instructions_fetched == memory_instructions_analysed + cache_conflicts')


    if stride_analysis_info['memory_instructions_analysed'] != stride_analysis_info['memory_instructions_counted']:
        print ('\nFailed memory_instructions_analysed == memory_instructions_counted')
        print ('memory_instructions_analysed: ', stride_analysis_info['memory_instructions_analysed'])
        print ('memory_instructions_counted: ', stride_analysis_info['memory_instructions_counted'])
    else:
        print ('\nPassed memory_instructions_analysed == memory_instructions_counted')

    if stride_analysis_info['memory_accesses'] != (stride_analysis_info['read_accesses'] + stride_analysis_info['read2_accesses'] + stride_analysis_info['write_accesses']):
        print ('\nFailed memory_accesses == read_accesses + read2_accesses + write_accesses')
        print ('memory_accesses: ', stride_analysis_info['memory_accesses'])
        print ('read_accesses: ', stride_analysis_info['read_accesses'])
        print ('read2_accesses: ', stride_analysis_info['read2_accesses'])
        print ('write_accesses: ', stride_analysis_info['write_accesses'])


    else:
        print ('\nPassed memory_accesses == read_accesses + read2_accesses + write_accesses')
    


    # ['memory_instructions_fetched', '823464808']
    # ['memory_instructions_analysed', '801893863']
    # ['cache_conflicts', '21570945']
    # ['memory_instructions_counted', '801954758']
    # ['partially_steady_instructions', '327259118']
    # ['integrally_steady_instructions', '306491502']
    # ['accesses_in_integrally_steady_instructions', '306431216']
    # ['memory_accesses', '804213411']
    # ['read_accesses', '644648653']
    # ['read2_accesses', '0']
    # ['write_accesses', '159564296']
    # ['partially_steady_accesses', '331485046']
    # ['integrally_steady_accesses', '310478191']
