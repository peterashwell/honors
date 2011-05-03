# This code runs cross fold validation on all combinations of the feature sets present in the feature folder

import os
import itertools
import perceptron
import time


def write_cm(combination, cm, upto):
	fname = "combination" + str(upto) + ".txt"
	cm_out = open(fname, 'w')
	cm_out.write(','.join(combination) + '\n')
	cm_out.write('\n'.join([','.join([str(col) for col in row]) for row in cm]))
	cm_out.close()


_UPDATE_ITER = True
_NUM_RUNS = 5 # number of training runs

# Part 1 - produce the combinations of the elements of the feature folder
feature_sets = os.listdir("features")
num_articles = 851
num_classes = 16
fold_size = int(num_articles / 10.0)
leftover = num_articles % 10 # spread leftovers over first few folds
upto = 0
for comb_size in xrange(1,len(feature_sets) + 1):
	for combination in itertools.combinations(feature_sets, comb_size):
		upto += 1
		#print combination
		feature_files = [open("features/" + fname) for fname in combination]
		# start and end slices for the cross fold
		start = 0
		end = 0
		cm = [[0] * num_classes for i in xrange(num_classes)]

		for fold_mul in xrange(10): # corresponds to 1 cross validation run
			start = end
			end = start + fold_size
			if leftover > 0:
				end += 1
				leftover -= 1
			learner = perceptron.Perceptron("wiki_init.txt") 
			test_data = []
			time_since = time.time()
			
			first_round = True # first round of training (add test cases to array)
			for round in xrange(_NUM_RUNS):	
				print "CROSSFOLD:", fold_mul, "ROUND:", round 
				for data_file in feature_files:
					data_file.seek(0) # seek data files to 0 for next training round
				done = 0
				for line_num in xrange(num_articles): # for each line_num, either train or store for test data
					if _UPDATE_ITER and done % 30 == 0 and done != 0:
						print str(done) + "/" + str(851 - (end - start)), "in", time.time() - time_since, "seconds.", "eta:", ((851 - (end - start)) - done) * (1/30.0) * (time.time() - time_since), "seconds"
						time_since = time.time()
					current_line = ""
					for data_file in feature_files:
						part_line = data_file.readline()
						current_line += ','.join(part_line.strip().split(',')[:-2])
						line_end = ','.join(part_line.strip().split(',')[-2:])
					#print "line end:", line_end
					current_line += ',' + line_end # tack on last end part to current_line
					#print "FEEDING LINE:", current_line
					#print "LINE LENGTH:", len(current_line)
					if len(current_line) == 0:
						continue
					elif line_num >= start and line_num < end: # should be reserved for test
						if first_round:
							test_data.append(current_line)
					else:
						done += 1
						#print current_line[:3] + current_line[-3:]
						learner.train(current_line) # get the learner to train on one line
				first_round = False # stop adding to test cases
			learner.finish_training()
			print "results for cross fold", fold_mul
			learner.test_on_data(test_data, cm) # TODO make learner accept list of data, make this return metrics
		write_cm(combination, cm, upto)
		for fileobj in feature_files:
			fileobj.close()
