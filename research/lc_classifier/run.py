import psyco
psyco.full()
import os
from classifier import lcClassifier
from dist_funcs import dtw
from dist_funcs import simplegrammar
from dist_funcs import euclidean
from utils import crossfold
from utils import sample
from utils import normalise
from utils import distribute
from utils import available
from utils import signal_noise
from os import listdir
import sys
import getopt

cm = {}
#testdir = "lightcurves"
#clsf = lcClassifier(dtw, testdir)
#dataset = listdir(testdir)
N = 5 # nearest neighbors to consider

class lcExperiment:
	def __init__(self):
		self.missing = 0
		self.normalise = None
		self.pl_distribute = None
		self.available_pct = 100
		self.noise = 0
		self.distance_measure = None
		self.max_size = 400
		self.cm = {}
		self.dm_name = None
		#self.logfile = None
		self.incorr_file = None
		self.cm_file = None
		self.N = 5 # nearest neighbor N

	# parse command line options
	def parse_options(self):
		try:
			opts, args = getopt.getopt(sys.argv[1:], "dun:a:m:g:")
		except getopt.GetoptError as (errno, strerror):
			print "Input error", strerror
			self.usage()
			sys.exit(2)
		if len(opts) == 0:
			self.usage()
		print opts
		for opt, arg in opts:
			if opt == '-g':
				print 'arg:', arg
				if arg == 'dtw':
					self.distance_measure = dtw
					self.dm_name = "dtw"
				elif arg == 'euclidean':
					self.distance_measure = euclidean
					self.dm_name = "euclidean"
				else:
					print arg == 'dtw'
					print arg == 'euclidean'
					print "no distance measure chosen"
					sys.exit(2)
			if opt == '-d':
				if self.normalise:
					print "cannot be distributed and normalised at the same time"
					sys.exit(2)
				self.pl_distribute = True
			if opt == '-u':
				if self.pl_distribute:
					print "cannot be distributed and normalised at the same time"
					sys.exit(2)
				else:
					self.normalise = True
			if opt == '-n':
				self.noise = int(arg)
			if opt == '-a':
				self.available_pct = int(arg)
			if opt == '-m':
				self.missing = int(arg)
		if not (self.pl_distribute or self.normalise):
			print "no distribution chosen"
			exit(2)
		
		self.file_prefix = ''
		if self.pl_distribute:
			self.file_prefix += 'powlaw'
		elif self.normalise:
			self.file_prefix += 'norm'
		self.file_prefix += '_n' + str(self.noise)
		self.file_prefix += '_a' + str(self.available_pct)
		self.file_prefix += '_m' + str(self.missing)
		self.file_prefix += '_s' + str(self.max_size)
		self.test_dir = self.file_prefix # training data
		self.file_prefix += '_' + self.dm_name

	def usage(self):
		print """usage:
			[-dun:a:m:g:]
			[-d ] distribute according to -2.3 power law
			[-u] distribute uniformly (normalise mean intensity)
			[-n n_sig] set noise signal ratio of all data to n_sig
			[-a av_amt] set seen amount of curve to av_amt
			[-m m_pct] remove m_pct of the data as random chunks
			[-g dist] use distance measure dist to compare lcs
			"""

	def preliminary(self):
		print "preliminary..."
		# fix up file suffixes
		#self.log_file = self.file_prefix + '-0.log'
		print self.file_prefix
		self.incorr_file = self.file_prefix + '-0.incorrect'
		self.conf_file = self.file_prefix + '-0.confmat'
		
		# Rename log and result files if they already exist
		while self.incorr_file in os.listdir('results'):
			print "self.incorr_file:", self.incorr_file
			self.incorr_file = self.incorr_file.split('.')[0].split('-')
			upto = int(self.incorr_file[1]) + 1
			
			#self.log_file = self.log_file[0] + '-' + str(upto) + '.log'
			self.incorr_file = self.incorr_file[0] + '-' + str(upto) + '.incorrect'
			self.conf_file = self.conf_file.split('.')[0].split('-')[0] + '-' + str(upto) + '.confmat'

		# Create test data if it is not already there
		if self.test_dir not in os.listdir('lightcurves/'):
			os.mkdir('lightcurves/' + self.test_dir)
			for lc_file in os.listdir('lightcurves/cropped'):
				#print lc_file
				lc_data = open('lightcurves/cropped/' + lc_file)
				lc = [[],[]]
				for line in lc_data:
					line = line.strip().split(',')
					lc[0].append(float(line[0]))
					lc[1].append(float(line[1]))
				if self.pl_distribute:
					lc = distribute(lc)
				elif self.normalise:
					lc = normalise(lc)
				else:
					print "cannot proceed: no data distribution chosen"
					exit(2)
				if self.missing > 0:
					print "misisng data not implemented yet!"
				# Sample before making available amount
				lc = sample(lc, 400)
				if self.noise != 0:
					lc = signal_noise(lc, self.noise)
				if self.available_pct != 100.0:
					lc = available(lc, self.available_pct)
				lc_data.close()
				lc_procout = open('lightcurves/' + self.test_dir + '/' + lc_file, 'w')
				lc_procout.write('\n'.join([','.join([str(elem) for elem in obj]) for obj in zip(lc[0], lc[1])]))
				lc_procout.close()
		
		#self.log = open('results/' + self.log_file, 'w')
		#self.log.write('derp writing to logfile\n') 
		self.incorr = open('results/' + self.incorr_file, 'w')
		self.confmat = open('results/' + self.conf_file, 'w')
		self.clsf = lcClassifier(self.distance_measure, 'lightcurves/' + self.test_dir)
		
	def do_experiment(self):
		print "starting classification..."
		tested_count = 0
		for test, train in crossfold(10, os.listdir('lightcurves/' + self.test_dir)):
			for test_obj in test:
				if tested_count % 50 == 0 and tested_count != 0:
					print str(tested_count) + "/" + str(len(test) + len(train))
				tested_count += 1
				true_class = test_obj.strip().split('_')[0]
		
				# Read the test light curve in
				test_lc_data = open('lightcurves/' + self.test_dir + '/' + test_obj)
				test_lc = [[],[]]
				for line in test_lc_data:
					line = line.strip().split(',')
					test_lc[0].append(float(line[0]))
					test_lc[1].append(float(line[1]))
				test_lc_data.close()
				test_lc = distribute(test_lc)
				lc = normalise(test_lc)
				test_lc = sample(test_lc, 400)
				
				classification = self.clsf.nn_classify(self.N, test_lc, train)
				classified_as = classification[0]
				best_matches = classification[1]
				if classified_as not in self.cm.keys():
					new_dict = {}
					new_dict[true_class] = 1
					self.cm[classified_as] = new_dict
				else:
					if true_class in self.cm[classified_as].keys():
						self.cm[classified_as][true_class] += 1
					else:
						self.cm[classified_as][true_class] = 1
				
				# TODO write this to its own file
				self.incorr.write(test_obj + ',' + classified_as + ',' + ','.join(best_matches) + '\n')
				#self.log.write(str(self.cm) + '\n')
			self.incorr.flush()
			#self.log.flush()

	def print_cm(self):
		if self.cm is None:
			self.confmat.write("no cm to print")
		else:
			classes = set(self.cm.keys())
			add_classes = set()
			for key in classes:
				for other_class in self.cm[key]:
					if other_class not in classes:
						add_classes.add(other_class)
			classes = classes.union(add_classes)
			self.confmat.write('\t')
			for c in sorted(classes):
				self.confmat.write(c[:3] + '\t')
			self.confmat.write('\n')
			for c in sorted(classes):
				self.confmat.write(c[:3] + '\t')
				for other_c in sorted(classes):
					if c in self.cm.keys():
						if other_c in self.cm[c].keys():
							self.confmat.write(str(self.cm[c][other_c]) + '\t')
							continue
					self.confmat.write('0\t')
				self.confmat.write('\n')
	
	def finish(self):
		#self.log.close()
		self.incorr.close()
		self.confmat.close()
