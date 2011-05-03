import psyco
psyco.full()

import math
import random
import re
class Perceptron:
	def __init__(self, init_file=None, num_features=None, num_classes=None, classes=None):
		if init_file is not None:
			init_data = open(init_file)
			self.num_classes = int(init_data.readline().strip())
			self.num_features = int(init_data.readline().strip())
			index = 0
			self.classes = {}
			for line in init_data:
				self.classes[line.strip()] = index
				index += 1
		else:
			self.num_features = num_features
			self.num_classes = num_classes
			self.classes = classes
		# initialise training data
		self.weights = [0] * self.num_classes * self.num_features # initial weights used for classification
		self.weight_sums = [0] * self.num_classes * self.num_features # sum of weights during training
		self.rounds = 0.0 # rounds during training
		#print "classes:", self.classes
	# train, but do not average
	
	def sparse_line(self, line):
		#print "PROCESSING LINE >>>" + str(line) + "<<<"
		sparse_features = []
		for pos_val in line:
			if len(pos_val) == 0:
				return []
			pos_val = pos_val.strip().split('_')
			if len(pos_val) == 1:
				continue
			#print "ASSBALLS", pos_val
			sparse_features.append((int(pos_val[0]), int(pos_val[1])))
		return sparse_features

	def train_on_file(self, train_file):
		train_data = open(train_file)
		self.train(train)
		train_data.close()

	def train(self, line): # passes iterator to trianing data
		self.rounds += 1
		split_line = line.strip().split(',')
		features = self.sparse_line(split_line[:-2])
		true_class = self.classes[split_line[-2].strip()]
		computed_class = self.compute_class(features)
		if true_class != computed_class:
			weight_start_true = true_class * self.num_features
			weight_start_comp = computed_class * self.num_features
				#print features
			for pos, val in features:
				self.weights[weight_start_true + pos] += val
				self.weights[weight_start_comp + pos] -= val
		for index in xrange(self.num_features * self.num_classes):
			self.weight_sums[index] += self.weights[index] # wtf, didn't have * self.num_classes before...
		#for index in xrange(self.num_features):
		#	weight_sums[index] /= rounds # average the weights
		#self.weights = weight_sums # update main weights
		# DO NOT AVERAGE ^^^
	
	def finish_training(self):
		for index in xrange(self.num_features * self.num_classes):
			self.weight_sums[index] /= self.rounds # this is a float
		self.weights = self.weight_sums

	def compute_class(self, features, debug=False):
		best_score = None
		best_class = None
		tied_classes = None
		for cn in xrange(self.num_classes):
			#weight_start = cn * self.num_features
			#weight_end = (cn + 1) * self.num_features + 1
			#active_weights = self.weights[weight_start:weight_end]
			score = 0
			for pos, val in features:
				weight_start = cn * self.num_features
				score += val * self.weights[weight_start + pos] 
			#if debug:
			#	print cn, score, "|",
			if best_score is None:
				best_score = score
				best_class = cn
				tied_classes = [cn]
			else:
				if math.fabs(score - best_score) < 1e-10: # scores equal
					tied_classes.append(cn)
				elif score > best_score: # if we found a better class
					best_score = score
					best_class = cn
					tied_classes = [cn]
		if len(tied_classes) > 1:
			return random.choice(tied_classes)
		else:
			return best_class

	def test_on_file(self, test_file):
		test_data = open(test_file)
		self.test(test_data)
		test_data.close()
	
	def test_on_data(self, data, cm):
		self.test(data, cm)

	def test(self, test_data, cm):
		correct = 0
		incorrect = 0
		for line in test_data:
			split_line = line.strip().split(',')
			features = self.sparse_line(split_line[:-2])
			true_class = self.classes[split_line[-2].strip()]
			#print "true class:", true_class
			computed_class = self.compute_class(features, True)
			if true_class == computed_class:
				correct += 1
			else:
				incorrect += 1
			cm[computed_class][true_class] += 1
		print "correct:", correct, "incorrect:", incorrect
