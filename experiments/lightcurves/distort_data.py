import os
import sys
import getopt
import gc

from itertools import izip
from distortions import *
from lightcurve import LightCurve

class lcDistortions:
	def __init__(self):
		self.LC_DIRECTORY = "lightcurves" # directory with all lcs
		self.RAW_LC_DIRECTORY = "raw_lightcurves" # raw light curves

		self.normalise = None # normalise lc
		self.pl_distribute = None # power law distribution on lc
		self.missing = 0 # percentage of data removed
		self.available_pct = 100 # percentage of data seen
		self.noise = 0 # noise / signal ratio (0 means none)
		self.file_prefix = None	# directory name for processed light curves
		self.max_size = 400
		
	# print usage
	def usage(self):
		print """usage:
			[-dun:a:m:]
			[-d ] distribute according to -2.3 power law
			[-u] distribute uniformly (normalise mean intensity)
			[-n n_sig] set noise signal ratio of all data to n_sig
			[-a av_amt] set seen amount of curve to av_amt
			[-m m_pct] remove m_pct of the data as random chunks
			"""

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
		
		for opt, arg in opts:
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
				self.noise = float(arg)
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
	
	def preprocess(self):
		# Create test data if it is not already there
		new_directory = self.LC_DIRECTORY + '/' + self.file_prefix
		exists = False
		incomplete = False
		if self.file_prefix in os.listdir(self.LC_DIRECTORY):
			if len(os.listdir(new_directory)) == len(os.listdir(self.LC_DIRECTORY + '/' + self.RAW_LC_DIRECTORY)):
				exists = True
				print "directory exists:", new_directory
			else:
				incomplete = True
				pass # figure out how to delete directory with files
				# os.rmdir(new_directory)
		if not exists:
			if not incomplete:
				os.mkdir(new_directory)
			done = 0
			increment = 5
			for lc_file in os.listdir(self.LC_DIRECTORY + '/' + self.RAW_LC_DIRECTORY):
				if done % (len(os.listdir(self.LC_DIRECTORY + '/' + self.RAW_LC_DIRECTORY))) == 0:
					print "{0}/{1}".format(done, len(os.listdir(self.LC_DIRECTORY + '/' + self.RAW_LC_DIRECTORY)))
				done += 1
				lc = 'a'
				lc = LightCurve() # see lightcurve.py
				
				# read in all lc data
				lc_data = open(self.LC_DIRECTORY + '/' + self.RAW_LC_DIRECTORY + '/' + lc_file)
				for line in lc_data:
					line = line.strip().split('\t')
					lc.time.append(float(line[0]))
					lc.flux.append(float(line[1]))
				lc_data.close()
				
				# check the parameters
				if (not self.pl_distribute) and (not self.normalise):
					print "no distribution chosen..."
					raise Exception('no distribution chosen')
				lc = all_distortions(lc, self.noise, self.available_pct, self.missing, self.pl_distribute) # see distortions.py
				# write the distorted data out
				print "writing file..."
				lc_out = open('lightcurves/' + self.file_prefix + '/' + lc_file, 'w')
				for index in xrange(len(lc.time)):
					lc_out.write('{0}\t{1}\n'.format(str(lc.time[index]), str(lc.flux[index])))
				lc_out.close()
				print "done writing"

#	except Exception, e:
#		print e
#		print "removing", new_directory
#		os.rmdir(new_directory)
#		exit(2)

if __name__ == '__main__':
	lcproc = lcDistortions()
	lcproc.parse_options()
	lcproc.preprocess()
