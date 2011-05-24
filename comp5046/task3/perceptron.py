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

	def train(self, sentence, tags):
		start = time.time()
		tags_star = viterbi(sentence, self.classes, self.featureset)
		self.viterbi_time += time.time() - start
		self.featureset.update_weights(sentence, tags_star, tags)
	
	def train_greedy(self, sentence, tags):
		tags_star = greedy(sentence, self.classes, self.featureset)
		self.featureset.update_weights(sentence, tags_star, tags)		

	def test(self, sentence):
		start = time.time()
		return viterbi(sentence, self.classes, self.featureset)
		self.viterbi_time += time.time() - start

	def test_greedy(self, sentence):
		return greedy(sentence, self.classes, self.featureset)
			
	def finish_round(self):
		for f in self.featureset.features:
			f.finish_round()
			
	def finish_training(self):
		for f in self.featureset.features:
			f.finish_training()
