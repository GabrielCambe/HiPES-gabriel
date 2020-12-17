#!/bin/bash
for trace in $(ls *.tid0.mem* | sed 's/.tid0.mem.out.gz//'); do
    echo "$trace" 1>&2
    ../orcs -t $trace | tail -n 4 > $trace.memory_info.txt
done