import psyco
psyco.full()

from classifier import lcClassifier
from dist_funcs import dtw
from dist_funcs import simplegrammar
from utils import crossfold
from utils import sample
from utils import normalise
from utils import distribute
from os import listdir
import sys
import getopt

cm = {}
testdir = "lightcurves"
clsf = lcClassifier(dtw, testdir)
dataset = listdir(testdir)
N = 5 # nearest neighbors to consider

class lcExperiment:
	def __init__(self):
		self.missing = 0
		self.normalise = None
		self.distribute = None
		self.available = 100
		self.noise = 0
		self.distance_measure = None
		self.cm = {}
		self.clsf = None

	# parse command line options
	def parse_options(self):
		try:
			opts, args = getopt.getopt(sys.argv[1:], "dun:a:m:")
		except getopt.GetoptError as (errno, strerror):
			print "Input error", strerror
			self.usage()
			sys.exit(2)
		if len(opts) == 0:
			self.usage()
		print opts
		for opt, arg in opts:
			if opt == '-d':
				if self.normalise:
					print "cannot be distributed and normalised at the same time"
					sys.exit(2)
				self.distribute = True
			if opt == '-u':
				if self.distribute:
					print "cannot be distributed and normalised at the same time"
					sys.exit(2)
				else:
					self.normalise = True
			if opt == '-n':
				self.noise = arg
			if opt == '-a':
				self.available = arg
			if opt == '-m':
				self.missing = arg
		print "miss:", self.missing
		print "av:", self.available
		print "noise:", self.noise
		print "norm:", self.normalise
		print "dist:", self.distribute
	
	def usage(self):
		print """usage:
			[-dun:a:m:]
			[-d ] distribute according to -2.3 power law
			[-u] distribute uniformly (normalise mean intensity)
			[-n n_sig] set noise signal ratio of all data to n_sig
			[-a av_amt] set seen amount of curve to av_amt
			[-m m_pct] remove m_pct of the data as random chunks
			"""

	def do_experiment(self):
		tested_count = 0
		for test, train in crossfold(10, 
			if tested_count % 50 == 0 and tested_count != 0:
				print "up to:" tested_count
			tested_count += 1
		
lce = lcExperiment()
lce.parse_options()


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
		test_lc = distribute(test_lc)
		normalise(test_lc)
		test_lc = sample(test_lc, 400)
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
