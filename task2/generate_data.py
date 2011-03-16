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
from generateLightCurves import *

def write2file(time, flux, fnum, type):
	fname = str(type) + "_" + str(fnum) + ".data"
	f = open(fname, 'w')
	for i in xrange(len(time)):
		line = str(time[i]) + "\t" + str(flux[i]) + "\n"
		f.write(line)
	f.close()

# generate the test data using Kitty's script (modified slightly)  and the given counts and time domain
def generateLCData(ttype, amount, total_time, gap_percent = 0):
	print ttype, amount
	gap_epochs = int(floor(total_time * gap_percent))
	for i in xrange(amount):
		length = total_time
		time, flux = None, None
		if ttype == 'SNe':
			length = int(floor(random.uniform(10, 50))) # TODO: how long does a supernovae last for typically
			time, flux = generateSupernovae(length)
		elif ttype == 'ESE':
			length = int(floor(random.uniform(10, 50))) # TODO: how long do ese last
			time, flux = generateESE(length)
		elif ttype == 'IDV':
			length = int(floor(random.uniform(10, 50))) # TODO: should IDV be included in this
			time, flux = generateIDV(length)
		else: # if NT or whatever, leave length as default
			pass # sinusoid will be generated below
		nt_time, nt_flux = generateSinusoid(total_time)
		if length != total_time: # if just sinusoid, write to file
			time_offset = int(floor(random.uniform(0, total_time - length)))
			for epoch in xrange(time_offset, length):
				nt_flux[epoch] = flux[epoch]
		if gap_epochs != 0: # TODO how should gaps be inserted
			gapstr = bin(random.getrandbits(gap_epochs))[2:]
			for bit in gapstr:
				if bit == '1':
					nt_flux = 'x' # TODO how to indicate gaps
		write2file(nt_time, nt_flux, i, ttype)	

def usage():
	print "usage: generate_data [-eghinst] [-e --ESE ese_count] [-g --gap gap_percent] [-i --IDV idv_count] [-h --help] \
	[-n --NT nontransient_count] [-s --SNe supernovae_count] [-t epoch_time]"

if __name__ == "__main__":
	desired = {}
	_epochs = None
	gap_percent = 0
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hs:i:e:n:g:t:", ["help", "SNe", "ESE", "IDV", "NT", "gap"])
	except getopt.GetoptError:
		usage()
		sys.exit(2)
	if len(opts) == 0:
		usage()
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
		elif opt == "-t":
			_epochs = arg
		elif opt in ("-s", "--SNe"):
			desired['SNe'] = arg
		elif opt in ("-e" "--ESE"):
			desired['ESE'] = arg
		elif opt in ("-i", "--IDV"):
			desired['IDV'] = arg
		elif opt in ("-n", "--NT"):
			desired['NT'] = arg
		elif opt in ("-g", "--gap"):
			gap_percent = arg
	if _epochs is None:
		_epochs = 1000
		print "set default LC length (1000)"
	for ttype in desired.keys():
		generateLCData(ttype, int(desired[ttype]), int(_epochs), float(gap_percent))
