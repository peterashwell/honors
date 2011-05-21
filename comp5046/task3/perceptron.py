import psyco
psyco.full()

from itertools import izip
from numpy import array
from numpy import zeros
import math
import random
import re
import time

from Algorithms import viterbi

class Perceptron:
	def __init__(self, _featureset, _classes):
		self.featureset = _featureset
		self.nfeats = _featureset.size
		self.nclasses = len(_classes)
		self.classes = _classes
		# offsets for each class type
		self.class_offset = {} # OH MY GOD I USED TO BE PUTTING INDICES HERE DONT FORGET THIS (ie not incrementing size)
		offset = 0
		for class_name in _classes:
			self.class_offset[class_name] = offset
			offset += self.nfeats
		#print "CLASS OFFSETS:", self.class_offset

		self.weights = [0] * self.nclasses * self.nfeats #zeros(self.nclasses * self.nfeats) # initial weights
		self.weight_sums = self.weights[:] #zeros(self.nclasses * self.nfeats) # sum of weights for fast averaging		
		self.rounds = 0
		self.viterbi_time = 0

	def train(self, sentence, tags):
		#print "training on:", sentence, tags
		self.rounds += 1
		#print "self.rounds:", self.rounds
		start = time.time()
		tags_star = viterbi(sentence, self.classes, self.weights, self.class_offset, self.featureset)
		self.viterbi_time += time.time() - start
		#print "correct tags:", tags
		self.featureset.update_weights(sentence, tags_star, tags, self.weights, self.class_offset)
		#self.featureset.print_features(self.weights, self.class_offset, self.classes)
		#self.weight_sums += self.weights

	def test(self, sentence):
		start = time.time()
		return viterbi(sentence, self.classes, self.weights, self.class_offset, self.featureset)
		self.viterbi_time += time.time() - start
	
	def finish_training(self):
		for i in xrange(len(self.weight_sums)):
			self.weight_sums[i] /= (self.rounds * 1.0)
		self.weights = self.weight_sums
