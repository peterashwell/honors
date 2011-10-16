import numpy
from itertools import izip
import matplotlib.pyplot as plt
import matplotlib as mpl
import math
import os
import random
from lightcurve import *
#TODO config this
CONFIG_FILE = "config"
configs = eval(open(CONFIG_FILE).read().strip())
FIG_DIR = configs["FIGURE_DIR"]
LC_DIR = configs["LIGHTCURVE_DIR"]
CLASSES = configs["CLASSES"]

# Extracts the single best shapelet per class from the given directory
# containing a shapelet.ids file
def best_shapelets(shapelet_cf_dir):
	shapelet_id_file = open("{0}/{1}".format(shapelet_cf_dir, "shapelet_ids"))
	best_shapelets = {}
	best = {}
	best_line = {}
	best_SD = {}
	#SH_INDEX = "shapelet_ids"
	#sh_file = open('{0}/{1}'.format(FOUND_DIR, SH_INDEX))

	for ln, line in enumerate(shapelet_id_file):
		#if ln % 1000 == 0:
		#	print "{0}/{1}".format(ln,"total")
		line = line.strip().split(',')
		sh_class = line[1].split('/')[-1].split('_')[0]
		#print sh_class
		update = False
		if sh_class not in best.keys():
			update = True
		else:
			if line[-2] < best[sh_class]:
				update = True
		#elif line[-2] == best[sh_class]:
		#	if line[-1] > best_SD[sh_class]:
		#		update = True
		if update:
			best_line[sh_class] = line
			best[sh_class] = line[-2]
			best_SD[sh_class] = line[-1]
	return best_line
#
# Produce figures in figures/ and return tex to be embedded in report
# plot, dataset_sample, confusion matrices and 
def primary_plot(params, featset_fscore, featnames, featset_desc, exp_desc, param_name, baseline_result):
	mpl.rc('legend', fontsize=10)
	plt.clf()
	# plot baseline TODO use config to set default
	#plt.plot(param_vals, len(param_vals) * [baseline_result]) #, label='Baseline')
	linetypes = ['--', ':']
	markertypes = ['o', 'x', 'd', 's', '^']
	colors = ['r', 'g', 'c', 'm', 'y', 'k']
	
	# plot the parameter values against each featureset
	# ensure the parameter values are correctly correlated
	for lnum, featname in enumerate(featnames):
		linetype = '--'
		if lnum > len(markertypes):
			linetype = ':'
		markertype = markertypes[lnum % len(markertypes)]
		color = colors[lnum % len(colors)]
		linespecs = '{0}{1}{2}'.format(linetype, markertype, color)
		plt.plot(params, featset_fscore[featname], linespecs) #, PARAM_NAMES[param])
	plt.title("F-Score versus {0} in {1}".format(param_name.lower(), exp_desc.replace('%', '\%').lower()))
	plt.xlabel(param_name)
	plt.ylabel("F-Score")
	plt.ylim([0,1])
	# fix subtractive naming in featnames
	#for index, fn in enumerate(featnames):
	#	if 'all' in fn:
	#		pass
	#	else:
	#		featnames[index] = 'all {' + featnames[index] + '}'
	# TODO add all the classification descriptions here
	legends = tuple([featset_desc[featname] for featname in featnames])
	plt.legend(legends, loc='best')
	plt.savefig('{0}/{1}_fsplot.eps'.format(FIG_DIR, exp_desc.replace(' ', '-').replace('.',',')), format='eps')
	plt.close()
	
	#file_handle.write('\\begin{figure}[ht!]\n')
	#file_handle.write('\t\\centering\n')
	#file_handle.write('\t\\includegraphics[width=\\textwidth]{%s}\n' % (FIG_DIR + '/' + \
	#	exp_desc.replace(' ', '-').replace('.',',') + '_fsplot.eps'))
	#file_handle.write('\\end{figure}\n')

MAX_SUBFIG_COLS = 5

def exp_subfigs(exp_fname, param_val):
	print 'exp_fname:', exp_fname
	subfig_count = 0
	width = round(100.0 / MAX_SUBFIG_COLS * 0.88 / 100.0, 3)
	tex_out = ""
	# 2 lines below - new code - minipages
	tex_out += '\\begin{minipage}[b]{0.1\\linewidth}\n'
	tex_out += '\t\\centering\n\t%s\n\\end{minipage}\n' % (param_val)
	print "CLASSES:", CLASSES
	for lc_num, lc_type in enumerate(CLASSES):
		# load random light curve and save plot
		print '{0}/{1}'.format(LC_DIR, exp_fname)

		potential_files = os.listdir('{0}/{1}'.format(LC_DIR, exp_fname))
		potential_files = filter(lambda e: lc_type in e, potential_files)
		lc_fname = random.choice(potential_files)
		lc_fname = '{0}/{1}/{2}'.format(LC_DIR, exp_fname, lc_fname)
		lc = file_to_lc(lc_fname)
		lc.remove_gaps()
		plt.plot(lc.time, lc.flux, 'r+')
		plot_fname = '{0}_sample{1}.eps'.format(exp_fname.replace('.', ','), lc_num)
		frame1 = plt.gca()
		frame1.axes.get_xaxis().set_visible(False)
		frame1.axes.get_yaxis().set_visible(False)
		plt.savefig(FIG_DIR + '/' + plot_fname, format='eps')
		plt.close()

		# now write out corresponding latex
		# new code - minipage
		mp_width = 0.8 / len(CLASSES)
		tex_out += '\\begin{minipage}[c]{%f\\linewidth}\n' % (mp_width)
		tex_out += '\t\\includegraphics[width=\\textwidth]{%s}\n' % (FIG_DIR + '/' + plot_fname)
		tex_out += '\\end{minipage}\n'

		# old code - subfigures
		#tex_out += '\\subfigure[%s] {\n' % (lc_type))
		#tex_out += '\t\\includegraphics[width=%f\\textwidth]{%s}\n' % (width, FIG_DIR + '/' + plot_fname))
		#tex_out += '}\n')

		subfig_count += 1
		if subfig_count % len(CLASSES) == 0 and subfig_count != 0:
			tex_out += '\\\\\n'
	return tex_out

def produce_expsamp(exp_fnames, params, param_name, exp_desc):
	print params
	out_tex = ""
	out_tex += '\\begin{figure}[ht!]\n'
	out_tex += '\\centering\n'
	out_tex += '\\begin{minipage}[b]{0.1\\linewidth}\n'
	out_tex += '\\centering\n\t%s\n\\end{minipage}\n' % (param_name)
	mp_width = 0.8 / len(CLASSES)
	for lct in CLASSES:
		out_tex += '\\begin{minipage}[c]{%f\\linewidth}\n' % (mp_width)
		out_tex += '\\centering\n%s\n\\end{minipage}\n' % (lct)
	out_tex += '\\\\\n'
	for exp_num, exp_fname in enumerate(exp_fnames):
		# old stuff - subfigs
		#out_tex += '\\begin{figure}[ht!]\n')
		#out_tex += '\t\\centering\n')
	
		out_tex += exp_subfigs(exp_fname, params[exp_num])
			
		#old stuff - writes out subfigs
		#out_tex += '\\caption{%s with %s at %s}\n' \
		#	% (exp_fname.replace('_', '-').replace('.',','), param_name, params[exp_num]))
		#out_tex += '\\end{figure}\n')	
	out_tex += '\\caption{Sample lightcurves for the %s experiment}\n' % (exp_desc.lower())
	out_tex += '\\end{figure}\n'
	return out_tex

def cm_array(param_cm, params, exp_desc):
	out_tex = ""
	print param_cm
	# For each parameter, produce a minipage with a heavily fixed array representing the CM

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
