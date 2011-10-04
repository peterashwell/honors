import numpy
from itertools import izip
import matplotlib.pyplot as plt
NUM_SEGS = 10
def linear_segmentation(lc):
	# Start with segments all adjoined
	segments = [[i, i+1] for i in xrange(len(lc.time) - 1)]
	# Compute cost in terms of least-squared
	costs = []
	current = segments[0]
	for next in segments[1:]:
		# Compute the cost of the merged segment and store in "costs"
		seg_indices = range(current[1], next[-1] + 1)
		seg_times = [lc.time[i] for i in seg_indices]
		seg_flux = [lc.flux[i] for i in seg_indices]
		coeffs = numpy.polyfit(seg_times, seg_flux, 1)
		costs.append(sum([(coeffs[0] * t  + coeffs[1] - v) ** 2 for t, v in izip(seg_times, seg_flux)]))
		current = next
	while len(segments) > NUM_SEGS:
		min_index = costs.index(min(costs))
		
		lmerge = None
		rmerge = None
		
		# If we are not at leftmost point, recompute cost of merging with left index
		if min_index != 0: # find lmerge
			new_min = segments[min_index - 1][0]
			new_max = segments[min_index][1]
			seg_indices = range(new_min, new_max + 1) # Include the endpoint
			seg_times = [lc.time[i] for i in seg_indices]
			seg_flux = [lc.flux[i] for i in seg_indices]
			coeffs = numpy.polyfit(seg_times, seg_flux, 1)
			lmerge = sum([(coeffs[0] * t + coeffs[1] - v) ** 2 for t, v in izip(seg_times, seg_flux)])
		
		# If we are not at rightmost point, recompute cost of merging with right index
		if min_index != len(costs) - 1:
			# Remove first two cost values and replace with one
			new_min = segments[min_index][0]
			new_max = segments[min_index + 2][1] # The index beyond the one with which we merged
			seg_indices = range(new_min, new_max + 1) # Include the endpoint
			seg_times = [lc.time[i] for i in seg_indices]
			seg_flux = [lc.flux[i] for i in seg_indices]
			coeffs = numpy.polyfit(seg_times, seg_flux, 1)
			rmerge = sum([(coeffs[0] * t + coeffs[1] - v) ** 2 for t, v in izip(seg_times, seg_flux)])
		
		# Now remove the old segments, replacing with one new, longer segment
		new_min = segments[min_index][0]
		new_max = segments[min_index + 1][1]
		segments = segments[:min_index] + [[new_min, new_max]] + segments[min_index + 2:] # One beyond the merge point

		# Handle the cost update cases
		if lmerge is None:
			costs = [rmerge] + costs[2:]
		elif rmerge is None:
			costs = costs[:-2] + [lmerge]
		else:
			costs = costs[:min_index - 1] + [lmerge, rmerge] + costs[min_index + 2:]
	for seg in segments:
		min_index = min(seg)
		max_index = max(seg)
		times = []
		flux = []
		for i in xrange(min_index, max_index + 1):
			times.append(lc.time[i])
			flux.append(lc.flux[i])
	return segments

# TODO fix this the fucking timescales are all wrong, retard
# Replace with a proper haar wavelet transform
def haar_transform(flux):
	# assume list is power of two long
	averages = []
	differences = []
	for index in xrange(0, len(flux), 2):
		if flux[index] == '-' and flux[index + 1] == '-':
			average = '-'
			difference = '-'
		elif flux[index] == '-':
			average = flux[index + 1]
			difference = 0
		elif flux[index + 1] == '-':
			average = flux[index]
			difference = 0
		else:
			average = (flux[index] + flux[index + 1]) / 2.0
			difference = flux[index] - average
		averages.append(average)
		differences.append(difference)
	if len(averages) > 1:
		return haar_transform(averages[:]) + differences
	else:
		return averages + differences
