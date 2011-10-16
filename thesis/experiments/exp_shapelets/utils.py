import numpy
from itertools import izip
import matplotlib.pyplot as plt
import math

# Produce figures in figures/ and return tex to be embedded in report
# plot, dataset_sample, confusion matrices and 
def primary_plot(params_results, exp_desc, param_name):
	return ""

def dataset_sample(params, param_name, test_set):
	return ""

def cm_array(params, featsetname, param_name):
	return ""

def big_table(featset_results, exp_desc, param_name, params):
	classes = eval(open("config").read())["CLASSES"]
	param_vals = params_resultsets.keys()
	featnames = [params_resultsets[p] for p in param_vals]
	print "params:", param_vals

	return_tex = ""
	return_tex += '\\begin{table}[ht!]\n\t\\centering\n'
	return_tex += '\\footnotesize\n'
	return_tex += '\t\\begin{tabular}{|c|c|%s} \\hline' % ('l|' * len(param_vals))
	return_tex += '\t \\multirow{2}{*}{\\textbf{Feature}} & \\multirow{2}{*}{\\textbf{Class}} \
	& \\multicolumn{%d}{c|}{\\textbf{%s}} \\\\ \\cline{%s} \n' % (len(param_vals), param_name.title(), '{0}-{1}'.format(3, len(param_vals) + 2)) 
	return_tex += '\t  & & {0} \\\\ \\hline'.format(' & '.join(param_vals))
	for featname in featnames:
		return_tex += '\t\t\\multirow{%d}{*}{%s}\n' %(len(classes), featname.replace('_', '-'))
		for class_name in classes:
			return_tex += '& {0}'.format(class_name)
			for pn, param_val in enumerate(param_vals):
				return_tex += ' & {0}'.format(param_vals[param_val][featname][class_name])
			#print precs
			#print recalls
			#print fscores
			#	print pn, param_val
			#print precs[featname], recalls[featname], fscores[featname]
			#	return_tex += '\t\t & %s & %s & %s & %s \\\\\n'\
			#	 % (featname.replace('_', '-'), precs[featname][pn], recalls[featname][pn], fscores[featname][pn]))
			return_tex += ' \\\\\n'
		return_tex += '\\hline'
	return_tex += '\t\\end{tabular}\n'
	return_tex += '\t\\caption{F-Score of classification per class in the %s experiment}\n' % (exp_desc.lower())
	return_tex += '\\end{table}\n'



def process_cm(raw_cm):
	# First, read through and get class set
	cm = []
	classes = []
	for row in raw_cm:
		cm.append([int(o) for o in row[1:]])
		classes.append(row[0])
	class_fn = [0 for i in xrange(len(classes))]
	class_fp = [0 for i in xrange(len(classes))]
	class_tp = [0 for i in xrange(len(classes))]
	class_counts = [0 for i in xrange(len(classes))]
	for i in xrange(len(classes)):
		for j in xrange(len(classes)):
			if i == j:
				class_tp[i] += cm[i][j]
			else:
				class_fp[j] += cm[i][j]
				class_fn[i] += cm[i][j]
			class_counts[i] += cm[i][j]
	microavg_precision = 0
	microavg_recall = 0
	microavg_fscore = 0
	for class_num in xrange(len(classes)):
		if class_tp[class_num] + class_fp[class_num] != 0:
			microavg_precision += class_counts[class_num] * (class_tp[class_num] / \
				(1.0 * class_tp[class_num] + class_fp[class_num]))
		if class_tp[class_num] + class_fn[class_num] != 0:
			microavg_recall += class_counts[class_num] * (class_tp[class_num] / \
				(1.0 * class_tp[class_num] + class_fn[class_num]))
	microavg_precision /= (1.0 * sum(class_counts))
	microavg_recall /= (1.0 * sum(class_counts))
	microavg_fscore = 2 * (microavg_precision * microavg_recall) / (1.0 * microavg_precision + microavg_recall)
	
	# write number of classes
	#result_file.write(str(len(classes)) + '\n')
	
	detailed = []
	# write out the results for each class
	for cn in xrange(len(classes)):
		prec = None
		recall = None
	
		if math.fabs(class_tp[cn] + class_fp[cn]) < 1e-10:
			prec = 0
			#print 'error:, no results for class', classes[cn]
			#continue
		else:
			prec = (1.0 * class_tp[cn] / (class_tp[cn] + class_fp[cn]))
		if math.fabs(class_tp[cn] + class_fn[cn]) < 1e-10:
			recall = 0
		else:
			recall = (1.0 * class_tp[cn] / (class_tp[cn] + class_fn[cn]))
			#print 'error:, no results for class', classes[cn]
			#continue
		
		if math.fabs(prec) < 1e-10 or math.fabs(recall) < 1e-10:
			fscore = 0.0
		else:
			fscore = (2.0 * prec * recall) / (recall + prec)
		detailed.append((classes[cn], prec, recall, fscore))
	
	total = (microavg_precision, microavg_recall, microavg_fscore)
	#for c, row in zip(sorted(classes), cm):
	return (detailed, total)





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
