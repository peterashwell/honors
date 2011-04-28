import math
import random
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
		else:
			self.num_features = num_features
			self.num_classes = num_classes
			self.classes = classes
		# initialise training data
		self.weights = [0] * self.num_classes * self.num_features # initial weights used for classification
		self.weight_sums = [0] * self.num_classes * self.num_features # sum of weights during training
		self.rounds = 0.0 # rounds during training
	
	# train, but do not average
	def train(self, train_file):
		last_weight = self.weights
		train_data = open(train_file)
		for line in train_data:
			self.rounds += 1
			split_line = line.strip().split(',')
			features = [float(obj.strip()) for obj in split_line[:-1]]
			true_class = self.classes[split_line[-1].strip()]
			computed_class = self.compute_class(features)
			if true_class != computed_class:
				weight_start_true = true_class * self.num_features
				weight_start_comp = computed_class * self.num_features
				for index in xrange(self.num_features):
					last_weight[weight_start_true + index] += features[index]
					last_weight[weight_start_comp + index] -= features[index]
			for index in xrange(self.num_features * self.num_classes):
				self.weight_sums[index] += last_weight[index] # wtf, didn't have * self.num_classes before...
			self.weights = last_weight
		#for index in xrange(self.num_features):
		#	weight_sums[index] /= rounds # average the weights
		#self.weights = weight_sums # update main weights
		# DO NOT AVERAGE ^^^
		pass # done
	
	def finish_training(self):
		for index in xrange(self.num_features * self.num_classes):
			self.weight_sums[index] /= self.rounds # this is a float
		self.weights = self.weight_sums

	def compute_class(self, features):
		best_score = None
		best_class = None
		tied_classes = None
		for cn in xrange(self.num_classes):
			weight_start = cn * self.num_features
			weight_end = (cn + 1) * self.num_features + 1
			active_weights = self.weights[weight_start:weight_end]
			score = sum(x * y for x, y in zip(features, active_weights)) # computes dot product
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

	def test(self, test_file):
		test_data = open(test_file)
		correct = 0
		incorrect = 0
		for line in test_data:
			split_line = line.strip().split(',')
			features = [float(obj.strip()) for obj in split_line[:-1]]
			true_class = self.classes[split_line[-1].strip()]
			computed_class = self.compute_class(features)
			if true_class == computed_class:
				correct += 1
			else:
				incorrect += 1
		print "correct:", correct, "incorrect:", incorrect
