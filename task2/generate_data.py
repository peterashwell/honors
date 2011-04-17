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

def write2file(time, flux, fnum, type, filt_pct=0):
	# print "writing",  fnum, type
	fname = None
	if filt_pct == 0:
		fname = str(type) + "_" + str(fnum) + ".data"
	else:
		fname = str(type) + "_" + str(fnum) + "_" + str(int(filt_pct)) + ".data"
	f = open(fname, 'w')
	#print flux
	for i in xrange(len(time)):
		#print time[i], flux[i]
		line = str(time[i]) + "\t" + str(flux[i]) + "\n"
		f.write(line)
	f.close()

def gapify(time, flux, remove_amount, missing_as_gaps):
	if missing_as_gaps:
		# generate a gap size from normal distribution between 1/10 and 1/3 of the total data
		removed = 0
		upper_gap_size = math.floor(1.0 / 3.0 * len(flux)) 
		while removed < remove_amount:
			gap_size = random.randrange(1, upper_gap_size)
			if gap_size > remove_amount - removed:
				gap_size = int(remove_amount - removed)
			removed += gap_size
			gap_start = random.randrange(1, len(flux) - gap_size)
			time = time[:gap_start] + time[gap_start + gap_size:]
			flux = flux[:gap_start] + flux[gap_start + gap_size:]
	else: # randomly remove data
		removed = 0
		while removed < remove_amount:
			index_to_remove = random.randrange(len(flux))
			time = time[:index_to_remove] + time[index_to_remove + 1:]
			flux = flux[:index_to_remove] + flux[index_to_remove + 1:]

			removed += 1
	return (time, flux)

# generate the test data using Kitty's script (modified slightly)  and the given counts and time domain
def generateLCData(type, amount, step, gap_percent, distribute, missing_as_gaps, break_data):
	print "gap_percent:", gap_percent
	print "generating", amount, type
	epochs = 300
	for i in xrange(amount):
		time, flux = None, None
		if ttype == 'SNe':
			time, flux = generateSupernovae(step)
		elif ttype == 'ESE':
			#print "making ese"
			time, flux = generateESE(step)
		elif ttype == 'IDV':
			time, flux = generateIDV(500, step) # TODO specifiy length of IDV
		elif ttype == 'NT':
			time, flux = generateNT(step, 1, 0.2)
		if distribute:
			min = 1
			max = 10
			new_flux = random.uniform(max ** -2.3, min) ** (1 / -2.3)
			mean = 1.0 * sum(flux) / len(flux)
			for obs_num in xrange(len(flux)):
				flux[obs_num] *= new_flux / mean
		time = range(1, len(flux) + 1)
		if gap_percent > 0 and break_data: # report true data as well as split data, for training
			write2file(time, flux, i, type)
		if gap_percent > 0:
			remove_amount = math.floor(len(flux) * gap_percent / 100.0)
			time, flux = gapify(time, flux, remove_amount, missing_as_gaps)
		#for f_num in xrange(len(flux)): # TODO producing gappy data
		#	if random.random() < gap_percent:
		#		flux[f_num] = 'x'
		write2file(time, flux, i, type, gap_percent)

def usage():
	print "usage: generate_data\
				[-deghinstj]\
				[-b] break up missing/original as files\
				[-d ] distribute\
				[-e --ESE ese_amount]\
				[-m --missing missing_percent]\
				[-g ] gappy (not random missing)\
				[-i --IDV idv_amount]\
				[-h --help] \
				[-n --NT nontransient_amount]\
				[-s --SNe supernovae_amount]\
				[-t num_epochs]"

if __name__ == "__main__":
	desired = {} # what we want to get
	step = None # the step size for observations
	gap_percent = 0 # what percentage of data is missing
	distribute = False # distribute data as exponential to -2.3
	missing_as_gaps = False # remove data as chunks, not random
	break_data = False
	try:
		opts, args = getopt.getopt(sys.argv[1:], "dbghs:i:e:n:m:t:", ["distribute", "help", "SNe", "ESE", "IDV", "NT", "missing", "time", "jump"])
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
		if opt in("-d"):
			distribute = True
		if opt in ("-s", "--SNe"):
			desired['SNe'] = int(arg)
		if opt in ("-e" "--ESE"):
			desired['ESE'] = int(arg)
		if opt in ("-i", "--IDV"):
			desired['IDV'] = int(arg)
		if opt in ("-n", "--NT"):
			desired['NT'] = int(arg)
		if opt in ("-m", "--missing"):
			gap_percent = float(arg)
		if opt in ("-g"):
			missing_as_gaps = True
		if opt in ("s", "--step"):
			step = int(arg)
		if opt in ("-b", "--break"):
			break_data = True
		print "set default LC length (1000)"
	if step is None:
		step = 1.0
		# print "set default step size (1)"
	for ttype in desired.keys():
		generateLCData(ttype, desired[ttype], step, gap_percent, distribute, missing_as_gaps, break_data)
