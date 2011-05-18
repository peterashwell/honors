#/usr/local/bin/python
# This code runs cross fold validation on all combinations of the feature sets present in the feature folder

import os
from itertools import izip
import perceptron
import time
import psyco
psyco.full()

def write_cm(filename, cm, rounds):
	fname = "conf_matrices/" + filename + "bin_" + str(rounds) + ".csv"
	cm_out = open(fname, 'w')
	cm_out.write('\n'.join([','.join([str(col) for col in row]) for row in cm]))
	cm_out.close()


UPDATE_ITER = True
TRAINING_ROUNDS = 10 # number of training runs
NUM_ARTICLES = 851
class_data = open("wiki_data/classes.txt") # TODO change this back
CLASSES = class_data.read().strip().split('\n')
NUM_CLASSES = len(CLASSES)
class_data.close() 
LEAVEOUT_SIZE = int(NUM_ARTICLES / 10.0)
LEAVEOUT_RESIDUE = NUM_ARTICLES % 10 # spread leftovers over first few folds

combination_index = open("combinations_index.csv") # TODO change this
comb_data = [obj.strip().split(',') for obj in combination_index.read().strip().split('\n')]
combination_roots = [obj[0] for obj in comb_data]
NUM_FEATURES = [int(obj[1]) for obj in comb_data]
combination_sources = {}
for obj in comb_data:
	combination_sources[obj[0]] = ''.join([name[:3] for name in obj[2:]])
print combination_sources
feature_desc = open("feature_index.csv") # TODO change this back

print "NUM_FEATURES", NUM_FEATURES
print "NUM_ARTICLES", NUM_ARTICLES
print "NUM_CLASSES", NUM_CLASSES
for combination_root, num_features in izip(combination_roots, NUM_FEATURES):
	print "running tests on", combination_root
	feature_index = open(combination_root + ".index")
	feature_value = open(combination_root + ".values")

	# read the files into main memory for speed (hopefully doesn't crash my pc)
	cached_indices = []
	cached_values = []
	
	for line_num in xrange(NUM_ARTICLES):
		index_line = feature_index.readline().strip()
		value_line = feature_value.readline().strip()
		if len(index_line) > 0 and len(value_line) > 0:
			cached_indices.append([int(obj) for obj in index_line.split(',')]) # REMOVE FLOAT TOOD
			cached_values.append([int(obj) for obj in value_line.split(',')]) # REMOVE FLOAT TODO
		else:
			cached_indices.append([])
			cached_values.append([])
	leaveout_start = 0
	leaveout_end = 0
	conf_matrix = [[0] * NUM_CLASSES for i in xrange(NUM_CLASSES)]
	
	for fold_num in xrange(10): # Do 10-fold validation
		# update positions of leftout data
		leaveout_start = leaveout_end
		leaveout_end = leaveout_start + LEAVEOUT_SIZE
		if LEAVEOUT_RESIDUE > 0:
			leaveout_end += 1
			LEAVEOUT_RESIDUE -= 1
		
		learner = perceptron.Perceptron(num_features, CLASSES) 
		leftout_desc = [] # rows left out for validation
			
		time_since = time.time()
		for round in xrange(TRAINING_ROUNDS):
			print "crossfold", fold_num, "training round:", round
			feature_desc.seek(0)
			done = 0
			for line_num in xrange(NUM_ARTICLES): # train on each line of data
				if line_num >= leaveout_start and line_num < leaveout_end: # should be reserved for test
					leftout_desc.append(feature_desc.readline())
					continue
				if UPDATE_ITER and done % 30 == 0 and done > 0:
					print str(done) + "/" + str(851 - (leaveout_end - leaveout_start)), "in", time.time() - time_since, "seconds."
					time_since = time.time()
				learner.train(cached_indices[line_num], cached_values[line_num], feature_desc.readline().strip())
				done += 1
		learner.finish_training()
		print "results for cross fold", fold_num

		learner.test(cached_indices[leaveout_start:leaveout_end], \
						cached_values[leaveout_start:leaveout_end],
						leftout_desc, conf_matrix) # TODO make learner accept list of data, make this return metrics
	
	write_cm(combination_sources[combination_root], conf_matrix, TRAINING_ROUNDS)
	feature_index.close()
	feature_value.close()
feature_desc.close()
