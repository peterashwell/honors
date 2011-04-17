#!/usr/local/bin/python

from perceptron import Perceptron
import getopt, sys

args = sys.argv[1:]
init_file = args[0]
data_file = args[1]
test_file = args[2]

learner = Perceptron(init_file)
learner.train(data_file)
learner.test(test_file)
