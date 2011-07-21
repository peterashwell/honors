from distortions import *

import os
import sys
import getopt

class lcDistortions:
	def __init__(self):
		self.LC_DIRECTORY = "lightcurves" # directory with all lcs
		self.RAW_LC_DIRECTORY = "cropped" # raw light curves

		self.normalise = None # normalise lc
		self.pl_distribute = None # power law distribution on lc
		self.missing = None # percentage of data removed
		self.available_pct = None # percentage of data seen
		self.noise = None # noise / signal ratio (0 means none)
		self.file_prefix = None	# directory name for processed light curves
		
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
		options = 
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
		self.file_prefix += '_' + self.dm_name
	
	def preprocess(self):
		# Create test data if it is not already there
		if self.test_dir in os.listdir(self.LC_DIRECTORY):
			print 'directory already exists...'
		else: # does not already exist
			new_directory = self.LC_DIRECTORY + self.test_dir
			os.mkdir(new_directory)
			try:
				for lc_file in os.listdir(self.RAW_LC_DIRECTORY):
					print 'distorting:', lc_file
					lc = LightCurve() # see lightcurve.py
					
					# read in all lc data
					lc_data = open(self.RAW_LC_DIRECTORY + lc_file)
					for line in lc_data:
						line = line.strip().split(',')
						lc.time.append(float(line[0]))
						lc.flux.append(float(line[1]))
					lc_data.close()
					
					# check the parameters
					if (not self.pl_distribute) and (not self.normalise):
						print "no distribution chosen..."
						raise Exception('no distribution chosen')
					lc = all_distortions(lc) # see distortions.py
					
					# write the distorted data out
					lc_out = open('lightcurves/' + self.test_dir + '/' + lc_file, 'w')
					lc_out.write('\n'.join([','.join([str(elem) for elem in obj]) for obj in zip(lc[0], lc[1])]))
					lc_out.close()
			except:
				print "removing", new_directory
				os.rmdir(new_directory)
				exit(2)

if __name__ == '__main__':
	lcproc = lcDistortions()
	lcproc.parse_options()
	lcproc.preprocess()
