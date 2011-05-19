import psyco
psyco.full()

import random
import time
from perceptron import Perceptron
from features import cwFeature
from features import ptFeature
from featureset import FeatureSet

ROUNDS = 1

# Step 1 - load up features into featureset
cwf = cwFeature("wordlist")
ptf = ptFeature("taglist")
fs = FeatureSet([cwf, ptf])
taglist = open("taglist")
global_tags = taglist.read().strip().split('\n')
percept = Perceptron(fs, global_tags)

# Step 2 - train perceptron for however many rounds on training data
training_data = open("data/eng.train")
sentence = []
true_tags = []
start_time = time.time()
vit_time = 0
for r in xrange(ROUNDS):
	line_num = 0
	for line in training_data:
		if line_num != 0 and line_num % 10 == 0:
			print "done", line_num, "/", 219552, time.time() - start_time, vit_time
		line_num += 1	
		line = line.strip()
		if line == '':
			vit_time += percept.train(sentence, true_tags)
			sentence = []
			true_tags = []
		else:
			line = line.split(' ')
			sentence.append(line[0])
			true_tags.append(line[-1])
	training_data.seek(0)
training_data.close()

# Step 3 - classify
test_data = open("data/eng.testa")
output = open("results/eng.testa_tested", 'w')
test_lines = []
for line in test_data:
	line = line.strip()
	if line == '':
		tags_star = percept.test([obj[0] for obj in test_lines])
		for tl, tt in izip(test_lines, tags_star):
			output.write(' '.join(tl) + ' ' + tt)
		test_lines = []
	else:
		line = line.split(' ')
		test_lines.append(line)
	

