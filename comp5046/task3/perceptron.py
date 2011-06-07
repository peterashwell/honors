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
from Algorithms import greedy
class Perceptron:
	def __init__(self, _featureset, _classes):
		self.featureset = _featureset
		self.classes = _classes
		self.weight_sums = [0] * sum([f.size for f in self.featureset.features])
		self.rounds = 0
		self.viterbi_time = 0

	def train(self, sentence, poslist, tags):
		start = time.time()
		tags_star = viterbi(sentence, poslist, self.classes, self.featureset)
		self.viterbi_time += time.time() - start
		self.featureset.update_weights(sentence, poslist, tags_star, tags)
	
	def train_greedy(self, sentence, poslist, tags):
		tags_star = greedy(sentence, poslist, self.classes, self.featureset)
		self.featureset.update_weights(sentence, poslist, tags_star, tags)		

	def test(self, sentence, poslist):
		start = time.time()
		return viterbi(sentence, poslist, self.classes, self.featureset)
		self.viterbi_time += time.time() - start

	def test_greedy(self, sentence, poslist):
		return greedy(sentence, poslist, self.classes, self.featureset)
			
	def finish_round(self):
		for f in self.featureset.features:
			f.finish_round()
			
	def finish_training(self):
		for f in self.featureset.features:
			f.finish_training()
