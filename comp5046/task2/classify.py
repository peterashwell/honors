#!/usr/local/bin/python
import math
from perceptron import Perceptron
import getopt, sys

args = sys.argv[1:]
init_file = args[0]
split_pct = float(args[1])
file_root = args[2].split('.')[0]

num_files = int(math.ceil(100.0 / split_pct))
left_out = 0
for left_out in xrange(10):
	learner = Perceptron(init_file)
	for fnum in range(10):
		if fnum == left_out:
			continue # skip the one left out
		else: # process it
			filename = file_root + "_split" + str(fnum) + ".data"
			learner.train(filename)
	learner.finish_training()
	learner.test(file_root + "_split" + str(left_out) + ".data")
