import random
from perceptron import Perceptron
from features.cw_feature import cwFeature
from features.pt_feature import ptFeature

ROUNDS = 1

# Step 1 - load up features into featureset
cwf = cwFeature("wordlist")
ptf = ptFeature("taglist")
fs = FeatureSet([cwf, ptf])
taglist = open("taglist")
tags = taglist.read().strip().split('\n')
percept = Perceptron(fs, tags)

# Step 2 - train perceptron for however many rounds on training data
training_data = open("data/eng.train")
sentence = []
true_tags = []
for r in xrange(ROUNDS):
	for line in training_data:
		line = line.strip()
		if line == '':
			percept.train(sentence, tags)
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
	

