import psyco
psyco.full()

import random
import os
import time

from perceptron import Perceptron
import features
from featureset import FeatureSet
from itertools import izip

ROUNDS = 50

# Step 1 - load up features into featureset
wordlist_file = open("wordlist")
wl = wordlist_file.read().splitlines()
wordlist_file.close()
taglist_file = open("taglist")
tl = taglist_file.read().splitlines()
taglist_file.close()
poslist_file = open("poslist")
pl = poslist_file.read().splitlines()
poslist_file.close()
preflist_file = open("preflist")
pfl = preflist_file.read().splitlines()
preflist_file.close()
sufflist_file = open("sufflist")
sfl = sufflist_file.read().splitlines()
sufflist_file.close()

print len(wl), len(tl)

cwf = features.wpFeature(wl, tl, 0) # current word
ptf = features.ptFeature(wl, tl) # previous tag
icf = features.icFeature(wl, tl) # word is capitalised
adjcf = features.acFeature(wl, tl) # adjacent capitalised words
pwf = features.wpFeature(wl, tl, -1) # previous word
nwf = features.wpFeature(wl, tl, 1) # next word
p2wf = features.wpFeature(wl, tl, -2) # 2 words before
n2wf = features.wpFeature(wl, tl, 2) # 2 words after
fac = features.facFeature(wl, tl) # first word after capitalisation
fbc = features.fbcFeature(wl, tl) # first word before capitalisation
allc = features.allcFeature(wl, tl) # all caps word (not in all caps sentence though)
hn = features.hnFeature(wl, tl) # sentence has at least %30 words as numbers
horg = features.horgFeature(wl, tl) # handpicked org words (team, group etc)
br = features.brFeature(wl, tl) # bracketed words
cpos = features.ppFeature(wl, tl, pl, 0) # pos features 
ppos = features.ppFeature(wl, tl, pl, -1)
npos = features.ppFeature(wl, tl, pl, 1)
p2pos = features.ppFeature(wl, tl, pl, -2)
n2pos = features.ppFeature(wl, tl, pl, 2)
sfnf = features.suffFeature(sfl, tl, 1) # suffix of words in front
sfpf = features.suffFeature(sfl, tl, -1) # suffix of words behind
pfnf = features.prefFeature(pfl, tl, 1) # prefix of words in front
pfpf = features.prefFeature(pfl, tl, -1) # prefix of words behind
hypf = features.hypFeature(wl, tl)
basefeatures = [cwf, ptf, icf, pwf, p2wf, n2wf, nwf, cpos, npos, n2pos, ppos, p2pos]
extrafeatures = [br, horg, hn, fac, fbc, allc, adjcf]

fs = FeatureSet(basefeatures) 
percept = Perceptron(fs, tl)

# Step 2 - train perceptron for however many rounds on training data
training_data = open("data/engf.train")
sentence = []
poslist = []
true_tags = []
start_time = time.time()
for r in xrange(ROUNDS):
	print "round:", r
	line_num = 0
	for line in training_data:
		if line_num != 0 and line_num % 5000 == 0:
			print "done", line_num, "/", 219552, time.time() - start_time
		line_num += 1	
		line = line.strip()
		if line == '':
			percept.train_greedy(sentence, poslist, true_tags)
			sentence = []
			poslist = []
			true_tags = []
		else:
			line = line.split(' ')
			sentence.append(line[0])
			poslist.append(line[1])
			true_tags.append(line[-1])
	training_data.seek(0)
	percept.finish_round()
training_data.close()
#percept.finish_training()
# Step 3 - classify	
percept.finish_training()
test_data = open("data/eng.testb")
id_str = '_'.join([f.id for f in fs.features])
results_file = "eng_leftout_greedy" + "_" + str(ROUNDS) + "_" + id_str + ".out"
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
		tags_star = percept.test_greedy([obj[0] for obj in test_lines], [obj[1] for obj in test_lines])
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
