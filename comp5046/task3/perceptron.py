import psyco
psyco.full()

from itertools import izip
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
		self.class_offset = {}
		for index, class_name in enumerate(_classes):
			self.class_offset[class_name] = index
		
		self.weights = [0] * self.nclasses * self.nfeats # initial weights
		self.weight_sums = self.weights[:] # sum of weights for fast averaging		
		self.rounds = 0
	
	def train(self, sentence, tags):
		#print "training on:", sentence, tags
		self.rounds += 1
		vit_start = time.time()
		tags_star = viterbi(sentence, self.classes, self.weights, self.class_offset, self.featureset)
		vit_end = time.time() - vit_start
		self.featureset.update_weights(sentence, tags_star, tags, self.weights, self.class_offset)
		return vit_end
	
	def finish_training(self):
		for index in xrange(self.nfeats * self.nclasses):
			self.weight_sums[index] /= (self.rounds * 1.0)
		self.weights = self.weight_sums

	def test(self, sentence):
		return viterbi(sentence, self.classes, self.weights, self.class_offset, self.featureset)
