import psyco
psyco.full()

from itertools import izip
import math
import random
import re
class Perceptron:
	def __init__(self, num_features, classes):
		self.num_features = num_features
		self.num_classes = len(classes)
		index = 0
		self.classes = {}
		for class_str in classes:
			self.classes[class_str] = index
			index += 1
		# initialise training data
		self.weights = [0] * self.num_classes * self.num_features # initial weights used for classification
		self.weight_sums = [0] * self.num_classes * self.num_features # sum of weights during training
		self.rounds = 0.0 # rounds during training
		#print "classes:", self.classes
	# train, but do not average
		self.train_class_counts = {}
		for c in self.classes.keys():
			self.train_class_counts[c] = 0
	
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

	def train(self, indices, values, class_data): # passes iterator to trianing data
		self.rounds += 1
		if len(indices) == 0 or len(values) == 0:
			return # do nothing
		true_class = self.classes[class_data.split(',')[1]]
		self.train_class_counts[class_data.split(',')[1]] += 1
		#print "TRUE CLASS NIGGER", true_class
		computed_class = self.compute_class(indices, values)
		if true_class != computed_class:
			weight_start_true = true_class * self.num_features
			weight_start_comp = computed_class * self.num_features
				#print features
			for pos, val in izip(indices, values):
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
			self.weight_sums[index] /= (self.rounds * 1.0) # this is a float
		self.weights = self.weight_sums
		#print "ASSJISM"
		#for c in self.train_class_counts.keys():
		#	print c, self.train_class_counts[c] / self.rounds
			

	def compute_class(self, indices, values, debug=False):
		best_score = None
		best_class = None
		tied_classes = None
		for cn in xrange(self.num_classes):
			#weight_start = cn * self.num_features
			#weight_end = (cn + 1) * self.num_features + 1
			#active_weights = self.weights[weight_start:weight_end]
			score = 0
			for pos, val in izip(indices, values):
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

	def test(self, index_vectors, feature_vectors, desc_vectors,cm):
		class_counts = {}
		for c in self.classes.keys():
			class_counts[c] = 0
		correct = 0
		incorrect = 0
		for line_num in xrange(len(index_vectors)):
			indices = index_vectors[line_num]
			values = feature_vectors[line_num]
			#print "testing:", desc_vectors[line_num].strip().split(',')[0]
			#print "HOT ASS", desc_vectors[line_num]
			true_class = self.classes[desc_vectors[line_num].strip().split(',')[1]]
			computed_class = self.compute_class(indices, values)
			if true_class == computed_class:
				correct += 1
			else:
				incorrect += 1
			cm[computed_class][true_class] += 1
		print "correct:", correct, "incorrect:", incorrect
