#!/bin/bash
# for trace in $(ls *.tid0.mem* | sed 's/.tid0.mem.out.gz//'); do
#     echo "$trace" 1>&2
#     ../OrCS/orcs -t $trace | tail -n 4 > $trace.memory_info.txt
# done
./group_steady_accesses_info.sh > steady_accesses_info.txt
