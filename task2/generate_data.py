# Script to generate light curve data with transient and non-transient sources
# Incorporates script written by Kitty Lo (genLightCurves.py)
# Generates data sets including the following:
#   * Radio SNe
#	 * ESEs
#   * IDVs
#   * Sinusoids with small variance (uninteresting sources)
# Events arise/disappear suddenly (from zero flux) or from/to uninteresting sources
# Written by Peter Ashwell
# Date: 15 Mar 2011

import math
import sys
import getopt
import random
from generate_lc import *

class FluxDistributor:
	def __init__(self, fmin, fmax, num_sources, power=-2.3, buckets=100):
		self.fmin = fmin
		self.fmax = fmax
		self.num_sources = num_sources
		self.power = power # power of curve

		# Solve integral to find constant giving the distribution over the desired max / min
		self.constant = (self.power - 1) * self.num_sources / (fmax ** (self.power - 1) - fmin ** (self.power - 1))
		self.buckets = buckets
		self.bucketsize = (self.fmax - self.fmin) * 1.0 / self.buckets
		self.used = 0
		print 'bs:', self.bucketsize, 'cons:', self.constant 

	def evaluate_integral(self, fmin, fmax):
		# Find the number of sources between the given flux bounds 
		return self.constant * (fmax ** (self.power - 1) - fmin ** (self.power - 1)) / (self.power - 1)
	
	def initialise_distribution(self):
		self.bucket_srccount = {} # stores total sources per bucket b at index b
		for b in xrange(self.buckets):
			# evalute the integral across the bucket
			print 'evaluating from:', self.bucketsize * b + self.fmin, 'to:', self.bucketsize * (b + 1) + self.fmin
			num_sources = (self.evaluate_integral(self.bucketsize * b + self.fmin, self.bucketsize * (b + 1) + self.fmin))
			print 'srcs', b, num_sources
			if int(num_sources) != 0:
				self.bucket_srccount[b] = int(round(num_sources)) # store it for later
		print "BUCKETS", self.bucket_srccount
	
	def grab_mean(self):
		rand_bucket = None
		if len(self.bucket_srccount.keys()) == 0:
			if self.used != self.num_sources: # rounding missed a value somewhere
				self.used += 1
				rand_bucket = 0 # assign to most frequent bucket...
			else:
				raise Exception("trying to draw mean but all buckets are empty")
		else:
			# draw a random mean from the distribtion to normalise a source flux to
			rand_bucket = random.choice(self.bucket_srccount.keys())
			if self.bucket_srccount[rand_bucket] == 1:
				del self.bucket_srccount[rand_bucket] # delete key - don't want to attempt to assign flux to this bucket in future
			else:
				self.bucket_srccount[rand_bucket] -= 1
			self.used += 1
		# pull a value at random from the line joining the curve values at the edges of the bucket
		#bucket_left = self.constant * ((self.bucketsize * rand_bucket + self.fmin) ** (self.power))
		#bucket_right = self.constant * ((self.bucketsize * (rand_bucket + 1) + self.fmin) ** self.power)
		bucket_left = self.bucketsize * rand_bucket + self.fmin
		bucket_right = self.bucketsize * (rand_bucket + 1) + self.fmin
		print "c:", self.constant, "bs:", self.bucketsize, "fmin:", self.fmin
		print "rb:", rand_bucket, "l:", bucket_left, "r:", bucket_right
		return random.uniform(bucket_right, bucket_left) # monotonic function, left > right

	def normalise_flux(self, flux):
		# fix the mean of the flux at some desired value - operates direct on array
		mean = sum(flux) / (1.0 * len(flux))
		for i in xrange(len(flux)):
			flux[i] *= (self.grab_mean() / mean)

def write2file(time, flux, fnum, type):
	print "writing",  fnum, type
	fname = str(type) + "_" + str(fnum) + ".data"
	f = open(fname, 'w')
	#print flux
	for i in xrange(len(time)):
		#print time[i], flux[i]
		line = str(time[i]) + "\t" + str(flux[i]) + "\n"
		f.write(line)
	f.close()

# generate the test data using Kitty's script (modified slightly)  and the given counts and time domain
def generateLCData(type, amount, step, gap_percent):
	print "generating", amount, type
	epochs = 300
	for i in xrange(amount):
		time, flux = None, None
		if ttype == 'SNe':
			time, flux = generateSupernovae()
		elif ttype == 'ESE':
			#print "making ese"
			time, flux = generateESE()
		elif ttype == 'IDV':
			time, flux = generateIDV(epochs)
		elif ttype == 'NT':
			time, flux = generateNT(epochs, 1, 0.2)
		min = 1
		max = 10
		new_flux = random.uniform(max ** -2.3, min) ** (1 / -2.3)
		mean = 1.0 * sum(flux) / len(flux)
		for obs_num in xrange(len(flux)):
			pass
			#flux[obs_num] *= new_flux / mean
		write2file(time, flux, i, type)

def usage():
	print "usage: generate_data [-eghinstj] [-e --ESE ese count] [-m --missing data missing percent] [-i --IDV idv count] [-h --help] \
	[-n --NT nontransient count] [-s --SNe supernovae count] [-t epochs] [-j --jump]"

if __name__ == "__main__":
	desired = {}
	step = None
	gap_percent = 0
	total = 0
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hs:i:e:n:m:t:j", ["help", "SNe", "ESE", "IDV", "NT", "missing", "time", "jump"])
	except getopt.GetoptError as (errno, strerror):
		print "input error", strerror
		usage()
		sys.exit(2)
	if len(opts) == 0:
		print "no commands entered"
		usage()
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
		elif opt in ("-s", "--SNe"):
			desired['SNe'] = int(arg)
		elif opt in ("-e" "--ESE"):
			desired['ESE'] = int(arg)
		elif opt in ("-i", "--IDV"):
			desired['IDV'] = int(arg)
		elif opt in ("-n", "--NT"):
			desired['NT'] = int(arg)
		elif opt in ("-m", "--missing"):
			gap_percent = float(arg)
		elif opt in ("s", "--step"):
			step = int(arg)
		print "set default LC length (1000)"
	if step is None:
		step = 1
		print "set default step size (1)"
	#for k in desired.keys():
	#	total += desired[k] # find sum of sources
	#dist = FluxDistributor(1, 2, total)
	#dist.initialise_distribution()
	print total
	for ttype in desired.keys():
		generateLCData(ttype, desired[ttype], step, gap_percent)
	
	for i in xrange(10000):
		pass
		#todo test this cunt
