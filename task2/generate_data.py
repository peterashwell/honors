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
from models import *

def write2file(time, flux, fnum, type):
	fname = str(type) + "_" + str(fnum) + ".data"
	f = open(fname, 'w')
	#print flux
	for i in xrange(len(time)):
		#print time[i], flux[i]
		line = str(time[i]) + "\t" + str(flux[i]) + "\n"
		f.write(line)
	f.close()

# generate the test data using Kitty's script (modified slightly)  and the given counts and time domain
def generateLCData(ttype, amount, epochs, step, gap_percent):
	for i in xrange(amount):
		event_length = None
		time, flux = None, None
		if ttype == 'SNe':
			#print "making sne"
			event_length = int(floor(random.uniform(200, 500))) # TODO: how long does a supernovae last (weeks to months)
			time, flux = generateSupernovae(event_length)
		elif ttype == 'ESE':
			#print "making ese"
			event_length = int(floor(random.uniform(200, 500))) # TODO: how long do ese last
			time, flux = generateESE(event_length)
		elif ttype == 'IDV':
			time, flux = generateIDV(event_length)
		elif ttype == 'NT':
			pass # An underlying NT is generated for every j
		# generate a noise curve and superimpose an event on it if we want one
		nt_time, nt_flux = generateNT(epochs, 1, 0.2) # TODO: suitable mean for non interesting sources 
		if event_length is not None:
			event_start = int(floor(random.uniform(0, epochs - event_length)))
			for epoch in xrange(event_start, event_length):
				nt_flux[epoch] = flux[epoch] # copy the event onto the uninteresting source curve
		# calculate the number of missing data points from the desired missing percentage
		gap_epochs = int(floor(epochs * gap_percent * 0.01))
		#if gap_epochs != 0:
		#	gapstr = bin(random.getrandbits(gap_epochs))[2:]
		#	for bitnum in xrange(len(gapstr)):
		#		if gapstr[bitnum] == '1':
		#			nt_flux[bitnum] = 'x' # how to handle gaps
		if step != 1:
			nt_time = range(int(floor(1.0 * epochs / step)), step)
			sampled_ts = [nt_flux[epoch] for epoch in nt_time]
			nt_flux = sampled_ts
		# finally, apply the power law distribution to the flux array
		
		write2file(nt_time, nt_flux, i, ttype)

def usage():
	print "usage: generate_data [-eghinstj] [-e --ESE ese count] [-m --missing data missing percent] [-i --IDV idv count] [-h --help] \
	[-n --NT nontransient count] [-s --SNe supernovae count] [-t epochs] [-j --jump]"

if __name__ == "__main__":
	desired = {}
	epochs = None
	step = None
	gap_percent = 0
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
		elif opt == "-t":
			epochs = int(arg)
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
	if epochs is None:
		epochs = 1000
		print "set default LC length (1000)"
	if step is None:
		step = 1
		print "set default step size (1)"
	for ttype in desired.keys():
		generateLCData(ttype, desired[ttype], epochs, step, gap_percent)
		
