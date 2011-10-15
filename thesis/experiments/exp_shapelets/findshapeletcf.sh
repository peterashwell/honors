#!/bin/bash
args="-t norm_n0.0_a100_m0_s400 -s norm_n0.0_a100_m0_s400 -T 50 -S 50 -c $1"
#args="-t  -s  -T 50 -S 50 -c 1"
outdir=`python getshoutdir.py $args`
echo outdir $outdir
if [[ ! -d $outdir ]]; then
	mkdir $outdir
fi
if [[ ! -d "${outdir}/cf$1" ]]; then
	mkdir "${outdir}/cf$1"
fi
./getshapelets ${args} #-o ${outdir}"
