#!/bin/bash
for trace in $(ls *.tid0.mem* | sed 's/.tid0.mem.out.gz//'); do
    ../orcs -t $trace | tail -n2 > $trace.memory_info.txt
done