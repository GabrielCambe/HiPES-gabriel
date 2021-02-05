#!/bin/bash
for info in $(ls *.memory_info.txt); do
    echo $info
    cat $info | tail -n 12
done