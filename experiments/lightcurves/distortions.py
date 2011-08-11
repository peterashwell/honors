import random
from math import fabs
from math import tan
from math import radians
from math import floor
from math import sqrt
import numpy

from lightcurve import LightCurve

# multipy by random amount and add translation as 'source strength'
def distribute(lc):
	lc = normalise(lc) # normalise first
	flux = lc.flux[:]
	min = 1
	max = 10
	base_brightness = random.uniform(max ** -2.3, min) ** (1 / -2.3)
	new_mean = random.uniform(max ** -2.3, min) ** (1 / -2.3)
	for obs_num in xrange(len(flux)):
		flux[obs_num] = flux[obs_num] * new_mean + base_brightness
	return LightCurve(lc.time[:], flux)

# Make percent of the signal available
def available(lc, percent):
	assert percent > 0 and percent < 100
	#print percent
	#print len(lc.time)
	#print percent / 100.0
	#print floor(len(lc.time) * (percent / 100.0))
	avail_range = int(floor(len(lc.time) * (percent / 100.0)))
	return LightCurve(lc.time[:avail_range], lc.flux[:avail_range])

# Add gaussian noise to the signal to the new signal to noise ratio
def signal_noise(lc, sig_noise_ratio):
	# First compute signal std dev
	lc_len = len(lc.time) * 1.0
	sigma = sqrt(sum([x ** 2 for x in lc.flux]) / lc_len - (sum(lc.flux) / lc_len) ** 2)
	# Add random noise
	noise_amt = sig_noise_ratio * sigma
	return LightCurve(lc.time, [x + numpy.random.normal(0,noise_amt) for x in lc.flux])

# Remove part of the signal as chunks of size 1, 2, 5
def gapify(lc, gap_amt):
	MINIMUM_POINTS = 5
	gap_types = [1, 2, 5]
	gaps = []
	time = lc.time[:]
	flux = lc.flux[:]
	remove_amt = int(floor(len(flux) * gap_amt / 100.0))
	if len(time) - remove_amt < MINIMUM_POINTS:
		remove_amt = len(time) - MINIMUM_POINTS
	removed = 0
	print "finding gaps"
	while removed < remove_amt:
		gap_size = random.choice([1, 2, 5])
		if gap_size > remove_amt - removed:
			gap_size = remove_amt - removed
		removed += gap_size
		gap_start = random.randrange(1, len(flux) - gap_size)
		# work forwards from insertion position (if you run out of space go back)
		position = gap_start
		while position < len(flux) and gap_size > 0:
			if flux[position] != '-':
				flux[position] = '-'
				gap_size -= 1
			position += 1
		# work backwards from insertion position
		position = gap_start
		while position > 0 and gap_size > 0:
			if flux[position] != '-':
				flux[position] = '-'
				gap_size -= 1
			position -= 1

		# old way
		#gaps.append((gap_start, time[gap_start:gap_start + gap_size]))
		#time = time[:gap_start] + time[gap_start + gap_size:]
		#flux = flux[:gap_start] + flux[gap_start + gap_size:]
	#print "done finding gaps"
	#print "rebuilding"
	# reintroduce gaps as '-'
	#old way
	#for gap in reversed(gaps):
	#	start = gap[0]
	#	time = time[:start] + gap[1] + time[start:]
	#	flux = flux[:start] + ['-'] * len(gap[1]) + flux[start:] 
	new_lc = LightCurve(time[:], flux[:])
	#print "done rebuilding"
	return new_lc

# Change the intensity of the curve to have mean of new_mean
def normalise(lc, new_mean=1):
	# Compute mean of the curve
	#print max(lc.flux)
	#print min(lc.flux)
	flux_sum = 0
	flux_mean = numpy.average(lc.flux)
	flux_std = numpy.std(lc.flux)
	# Update the flux measurements
	for i in xrange(len(lc.flux)):
		if flux_std > 1e-10:
			lc.flux[i] = (lc.flux[i] - flux_mean) / flux_std
		else: # very flat signal - dividing should not really change it much
			lc.flux[i] = lc.flux[i] - flux_mean
	return LightCurve(lc.time[:], lc.flux[:])

# In place, take a sample of maxlen of a light curve
def sample(lc, maxlen):
	if len(lc.flux) <= maxlen:
		return lc
	else:
		new_lc = LightCurve()
		sparsity = int(len(lc.flux) / (1.0 * maxlen))
		#print "sparsity:", sparsity
		for i, point in enumerate(lc.flux):
			if i % sparsity == 0:
				new_lc.time.append(lc.time[i])
				new_lc.flux.append(lc.flux[i])
		return new_lc

def all_distortions(lc, noise, available_pct, missing, powlaw):
	if powlaw:
		#print "powlaw"
		lc = distribute(lc)
	else:
		lc = normalise(lc)
	#print "adding noise"
	if noise > 0:
		lc = signal_noise(lc, noise)
	#print "limiting available"
	if available_pct < 100.0:
		lc = available(lc, available_pct)
	#print "removing data"
	if missing > 0:
		lc = gapify(lc, missing)
	#print "done"
	return lc		
