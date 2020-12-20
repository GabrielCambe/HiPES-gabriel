#!/bin/bash
# for info in $(ls *.memory_info.txt); do
# for trace in $(ls *.tid0.mem* | sed 's/.tid0.mem.out.gz//'); do
for trace in $(ls *.tid0.mem*); do
    # echo "$trace" 1>&2
    gzip -l $trace
    # ../OrCS/orcs -t $trace | tail -n 4 > $trace.memory_info.txt
done
