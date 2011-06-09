import psyco
psyco.full()

from classifier import lcClassifier
from dist_funcs import dtw
from dist_funcs import simplegrammar
from utils import crossfold
from utils import sample
from os import listdir

cm = {}
testdir = "lightcurves"
clsf = lcClassifier(dtw, testdir)
dataset = listdir(testdir)
N = 5 # nearest neighbors to consider
for test, train in crossfold(10, dataset):
	upto = 0
	for test_obj in test:
		print "test case:", upto
		upto += 1
		true_class = test_obj.strip().split('_')[0]
		
		# Read the test light curve in
		test_lc_data = open(testdir + '/' + test_obj)
		test_lc = [[],[]]
		for line in test_lc_data:
			line = line.strip().split(',')
			test_lc[0].append(float(line[0]))
			test_lc[1].append(float(line[1]))
		test_lc_data.close()
		test_lc = sample(test_lc, 600)
		# Classify and record result
		print N
		print test_obj
		print len(test_lc)
		print true_class
		print len(train)
		classified_as = clsf.nn_classify(N, test_lc, train)
		if classified_as not in cm.keys():
			new_dict = {}
			new_dict[true_class] = 1
			cm[classified_as] = new_dict
		else:
			if true_class in cm[classified_as].keys():
				cm[classified_as][true_class] += 1
			else:
				cm[classified_as][true_class] = 1
		print test_obj, classified_as
		cm_out = []
		print cm
	for row, classified_as in enumerate(sorted(cm.keys())):
		cm_out.append([classified_as])
		for true_class in sorted(cm[classified_as].keys()):
			cm_out[row].append(str(cm[classified_as][true_class]))
	print '\n'.join('\t'.join(obj) for obj in cm_out)
# Final CM
cm_out = []
for row, classified_as in enumerate(sorted(cm.keys())):
	cm_out.append([classified_as])
	for true_class in sorted(cm[classified_as].keys()):
		cm_out[row].append(str(cm[classified_as][true_class]))
print '\n'.join('\t'.join(obj) for obj in cm_out)
