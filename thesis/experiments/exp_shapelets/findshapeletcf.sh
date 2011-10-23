#!/bin/bash
outdir="shapelet_testing/"
args="-t $1 -s $2 -T 100 -S 100 -o ${outdir} -c $3"
#args="-t  -s  -T 50 -S 50 -c 1"
outdir=`python getshoutdir.py $args`
echo outdir $outdir
./getshapelets ${args} 
