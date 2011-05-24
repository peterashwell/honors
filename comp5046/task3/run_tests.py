import psyco
psyco.full()

import random
import os
import time

from perceptron import Perceptron
import features
from featureset import FeatureSet
from itertools import izip

ROUNDS = 1

# Step 1 - load up features into featureset
wordlist_file = open("wordlist")
wl = wordlist_file.read().splitlines()
wordlist_file.close()
taglist_file = open("taglist")
tl = taglist_file.read().splitlines()
taglist_file.close()
print len(wl), len(tl)
cwf = features.wpFeature(wl, tl, 0)
ptf = features.ptFeature(wl, tl)
icf = features.icFeature(wl, tl)
acf = features.acFeature(wl, tl)
pwf = features.wpFeature(wl, tl, -1) # previous word
nwf = features.wpFeature(wl, tl, 1) # next word
fac = features.facFeature(wl, tl)
fbc = features.fbcFeature(wl, tl)
allc = features.allcFeature(wl, tl)
hn = features.hnFeature(wl, tl)
horg = features.horgFeature(wl, tl)
br = features.brFeature(wl, tl)
fs = FeatureSet([cwf, ptf, icf, acf, pwf, nwf])
percept = Perceptron(fs, tl)

# Step 2 - train perceptron for however many rounds on training data
training_data = open("data/engf.train")
sentence = []
true_tags = []
start_time = time.time()
for r in xrange(ROUNDS):
	print "round:", r
	line_num = 0
	for line in training_data:
		if line_num != 0 and line_num % 10000 == 0:
			print "done", line_num, "/", 219552, time.time() - start_time
		line_num += 1	
		line = line.strip()
		if line == '':
			percept.train(sentence, true_tags)
			sentence = []
			true_tags = []
		else:
			line = line.split(' ')
			sentence.append(line[0])
			true_tags.append(line[-1])
	# do last line in file

	training_data.seek(0)
	percept.finish_round()
training_data.close()
#percept.finish_training()
# Step 3 - classify
percept.finish_training()
test_data = open("data/eng.testa")
id_str = '_'.join([f.id for f in fs.features])
results_file = "eng" + "_" + str(ROUNDS) + "_" + id_str + ".out"
fnum = 0
while results_file in os.listdir("results"):
	results_file = results_file.split('.')[0] + str(fnum) + ".out"
	fnum += 1
results_file = "results/" + results_file
output = open(results_file, 'w')
test_lines = []
for line in test_data:
	line = line.strip()
	if line == '':
		tags_star = percept.test([obj[0] for obj in test_lines])
		#print "classified and result:"
		#print [obj[0] for obj in test_lines]
		#print tags_star
		for tl, tt in izip(test_lines, tags_star):
			output.write(' '.join(tl) + ' ' + tt + '\n')
		output.write('\n')
		test_lines = []
	else:
		line = line.split(' ')
		test_lines.append(line)
output.close()
test_data.close()
print "viterbi time:", percept.viterbi_time
print "feature time:", fs.feature_time
