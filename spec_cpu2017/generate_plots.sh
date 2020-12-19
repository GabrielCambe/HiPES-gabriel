#!/bin/bash
./group_steady_accesses_info.sh > steady_accesses_info.txt
python3 ../../scripts/plot_stride_percentages.py -i steady_accesses_info.txt