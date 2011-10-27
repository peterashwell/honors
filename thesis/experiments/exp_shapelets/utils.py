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
			if line[-2] > best[sh_class]:
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
	print "params:", params
	print "featset_score:", featset_fscore
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
	title = "Plot of F-Score versus {0} in the {1} experiment.".format(param_name.lower(), exp_desc.replace('%', '\%').lower())
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
	fig_name = '{0}/{1}_fsplot.eps'.format(FIG_DIR, exp_desc.replace(' ', '-').replace('.',','))
	plt.savefig(fig_name, format='eps')
	plt.close()
	
	fig_path = os.getcwd() + '/' + fig_name
	result_tex = ""
	result_tex += '\\begin{figure}[ht!]\n'
	result_tex += '\t\\centering\n'
	result_tex += '\t\\includegraphics[width=\\textwidth]{%s}\n' % (fig_path)
	result_tex += '\t\caption{%s}\n' %(title)
	result_tex += '\\end{figure}\n'
	return result_tex

NUM_TESTS = 200
HEAD_SPACE = 0.035
PARAMCOL_WIDTH = 0.09
CM_WIDTH = 0.27
LABEL_WIDTH = 0.06

def confmat_page(param_vals, featnames, feat_desc, param_fs_cm):
	print feat_desc
	print featnames
	tex = "\\begin{minipage}[c]{\\textwidth}\n"
	col_width = 0.85 / len(featnames)
	
	tex += "\t\\begin{minipage}[c]{\\textwidth}\n"	
	
	tex += "\t\t\\begin{minipage}[c]{%f\\textwidth}\n" % (PARAMCOL_WIDTH)
	tex += "\t\t\\centering\n"
	tex += "\t\t\tNoise\n"
	tex += "\t\t\\end{minipage}\n"

	tex += "\t\t\\begin{minipage}[c]{%f\\textwidth}\n" % (LABEL_WIDTH)
	tex += "\t\t\\centering\n"
	tex += "\t\t\t\\quad\n"
	tex += "\t\t\\end{minipage}\n"
	
	for fs in sorted(list(featnames))[:3]:
		tex += "\t\t\\begin{minipage}[c]{%f\\textwidth}\n" % (CM_WIDTH)
		tex += "\t\t\\centering\n"
		tex += "\t\t\\small{\n"
		tex += "\t\t\t{0}\n".format(feat_desc[fs][:10].capitalize())
		tex += "\t\t}\n"
		tex += "\t\t\\end{minipage} \\ \\ \n"
	tex += "\\\\ \t\\end{minipage}\n"

	for p in param_vals:
		tex += "\t\\vspace{5pt}\n"
		tex += "\t\\begin{minipage}[c]{\\textwidth}\n"
		tex += "\t\t\\begin{minipage}[c]{%f\\textwidth}\n" % (PARAMCOL_WIDTH)
		tex += "\t\t\t\\centering\n"
		tex += "\t\t\t{0}\n".format(p)
		tex += "\t\t\\end{minipage}\n"
		tex += "\t\\begin{minipage}[c]{%f\\textwidth}\n" % (LABEL_WIDTH)
		tex += "\t\t\\tiny {\n"
		tex += "\t\t\\vspace{-4pt}"
		tex += "\t\t\t\\begin{tabular}{r}\n"
		for classname in sorted(CLASSES): # defined at top
			tex += "\t\t\t\t{0}\\\\ \n".format(classname)
		tex += "\t\t\t\\end{tabular}\n"
		tex += "\t\t}\n"
		tex += "\t\\end{minipage}\n"
		for fs in sorted(list(featnames))[:3]:
			print "fs:", fs
			tex += "\t\t\\begin{minipage}[c]{%f\\textwidth}\n" % (CM_WIDTH)
			tex += "\t\t\t\\centering\n"
			tex += "\t\t\t\\tiny {\n"
			tex += "\t\t\t\t\\begin{tabular}{|c|c|c|c|c|c|c|c|} \hline\n"
			
			# Determine cell colors and appropriate labels
			colored_cm = []
			cm_rows = {}
			for row in param_fs_cm[p][fs]:
				cm_rows[row[0]]= row[1:]
			for rowkey in sorted(CLASSES):
				row = cm_rows[rowkey]
				colored_row = []
				row = cm_rows[rowkey]
				for elem in row:
					elem = elem.strip()
					elem = float(elem) / NUM_TESTS
					cell = None
					if math.fabs(1.0 - elem) < 1e-10:
						cell = '1.0'
					elif math.fabs(0.0 - elem) < 1e-10:
						cell = '0.0'
					else:
						cell = str(elem)[1:4]
					color = "\\cellcolor[rgb]{1.0,%f,%f}" % (1 - float(elem),1 - float(elem))					
					colored_row.append(color + ' ' + cell)
				tex += ' & '.join([str(o) for o in colored_row]) + '\\\\ \\hline\n'
			tex += "\t\t\t\\end{tabular}\n"
			tex += "}\n"
			tex += "\t\t\\end{minipage}\n"
		tex += "\t\\end{minipage}\n"
	tex += "\\end{minipage}\n"
	#print tex
	return tex

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

# Plots the splitline to the desired output directory (relative path)
def plot_splitline(sh_ts_distances, destination):
	if not os.path.isdir(destination):
		print "creating directory:", destination
		os.mkdir(destination)
	
	sh_classes =  sh_ts_distances.keys()
	# Now produce a histogram for this shapelet showing these distances
	fig = plt.figure()
	colors = ['b', 'g', 'r', 'm', 'y']
	bins = [1.0 / 100.0 * i for i in xrange(100)]
	
	# Find the maximum of any distance to squash them with
	max_dist = -1
	for sk in sh_ts_distances.keys():
		for tsk in sh_ts_distances[sk].keys():
			this_max = max(sh_ts_distances[sk][tsk])
			if this_max > max_dist:
				max_dist = this_max
	print "max dist:", max_dist
	
	NUM_BINS = 200
	BIN_SIZE = 1.0 / NUM_BINS
	BINS = numpy.linspace(0, 1, NUM_BINS)
	HIST_HEIGHT = 1 # Height of each histogram
	
	sh_ts_hist = {}
	sh_left = {}
	sh_right = {}
	for shnum, sh_class in enumerate(sh_ts_distances.keys()):
		fig = plt.figure()
		legend = [[], []]
		for tsnum, ts_class in enumerate(sorted(sh_ts_distances[sh_class].keys())):
			legend[1].append(ts_class)
			# First step, just get a separate figure for each (maybe lay out in tex)
			class_distances = sh_ts_distances[sh_class][ts_class]
			# Normalise and bin the distances
			squashed_distances = [d / (1.0 * max_dist) for d in class_distances]
			#print squashed_distances
			#print BINS
			hist = numpy.histogram(squashed_distances, BINS, normed=True)[0]
			hist = hist / numpy.sum(hist, axis=0)
			hist = hist.tolist()
			#print "hist:", hist
			if sh_class == ts_class: # check the std and mean of histogram
				this_max = max(squashed_distances)
				left_lim = min(squashed_distances)
				spread = this_max - left_lim + 0.05 # have at least a small spread
				sh_left[sh_class] = max(0, left_lim - spread)
				sh_right[sh_class] = min(1, this_max + spread)
				#print this_max, "dist_max"
				#print left_lim, "dist_min"
				#print spread, "spread"
				#print "distances:"
			if sh_class not in sh_ts_hist.keys():
				new_dict = {ts_class : hist}
				sh_ts_hist[sh_class] = new_dict
			else:
				sh_ts_hist[sh_class][ts_class] = hist
			#print hist
			#print len(hist)
			#p = plt.bar(numpy.linspace(0,1,NUM_BINS)[:-1], hist, BIN_SIZE,\
			#	color=colors[tsnum % len(colors)], bottom = HIST_HEIGHT * tsnum, alpha=1.0)	
			#plt.xlim([0,1])
			#legend[0].append(p[0])
		#frame = plt.gca()
		#frame.axes.get_yaxis().set_ticklabels(sorted(sh_ts_distances[sh_class].keys()))
		#frame.axes.get_yaxis().set_ticks([o + 0.5 for o in range(8)])
		#fig.axis().set_ticklabels([sorted(sh_ts_distances[sh_class])])
		#plt.legend(legend[0], legend[1])
		#plt.xlabel('Distance measure (normalised across all shapelets)')
		#plt.ylabel('Class')
		#cf_dir = '{0}/cf{1}'.format(out_dir, cfnum)
		#if not os.path.isdir(cf_dir):
	#		os.mkdir(cf_dir)
		#plt.savefig('{0}/{1}_sm.pdf'.format(cf_dir,sh_class), format='pdf')
		#plt.close()
	for shnum, sh_class in enumerate(sh_ts_hist.keys()):
		fig = plt.figure()
		for tsnum, ts_class in enumerate(sh_ts_hist[sh_class].keys()):
			hist = sh_ts_hist[sh_class][ts_class]
			p = plt.bar(numpy.linspace(0,1,NUM_BINS)[:-1], hist, BIN_SIZE,\
				color=colors[tsnum % len(colors)], bottom = HIST_HEIGHT * tsnum, alpha=1.0)	
			plt.xlim([0,1])
			legend[0].append(p[0])
		frame = plt.gca()
		frame.axes.get_yaxis().set_ticklabels(sorted(sh_ts_distances[sh_class].keys()))
		frame.axes.get_yaxis().set_ticks([o + 0.5 for o in range(8)])
		#fig.axis().set_ticklabels([sorted(sh_ts_distances[sh_class])])
		#plt.legend(legend[0], legend[1])
		plt.xlabel('Distance measure (normalised across all shapelets)')
		plt.ylabel('Class')
		plt.savefig('{0}/{1}_sm.pdf'.format(destination,sh_class), format='pdf')
		plt.close()
	
	for shnum, sh_class in enumerate(sh_ts_distances.keys()):
		fig = plt.figure()
		for tsnum, ts_class in enumerate(sh_ts_distances[sh_class].keys()):
			#left_lim = max(0, sh_mean[sh_class] - 3 * sh_std[sh_class])
			#right_lim = min(1, sh_mean[sh_class] + 3 * sh_std[sh_class])
			
			class_distances = sh_ts_distances[sh_class][ts_class]
			squashed_distances = [d / (1.0 * max_dist) for d in class_distances]
			right_lim = sh_right[sh_class]
			left_lim = sh_left[sh_class]	
			#left_lim = max(0, left_lim - spread)
			#right_lim = min(1, right_lim + spread)
			# Normalise and bin the distances
			NUM_BINS = 200
			BIN_SIZE = (right_lim - left_lim) / NUM_BINS
			BINS = numpy.linspace(left_lim, right_lim, NUM_BINS)
			
			hist = numpy.histogram(squashed_distances, BINS, normed=True)[0].tolist()
			hist = hist / numpy.sum(hist, axis=0)
		
			p = plt.bar(numpy.linspace(left_lim,right_lim,NUM_BINS)[:-1], hist, BIN_SIZE,\
				color=colors[tsnum % len(colors)], bottom = HIST_HEIGHT * tsnum, alpha=1.0)	
			
			plt.xlim([left_lim,right_lim])
			legend[0].append(p[0])
		frame = plt.gca()
		frame.axes.get_yaxis().set_ticklabels(sorted(sh_ts_distances[sh_class].keys()))
		frame.axes.get_yaxis().set_ticks([o + 0.5 for o in range(8)])
		#fig.axis().set_ticklabels([sorted(sh_ts_distances[sh_class])])
		#plt.legend(legend[0], legend[1])
		plt.xlabel('Distance measure (normalised across all shapelets)')
		plt.ylabel('Class')
		plt.savefig('{0}/{1}_sm_specific.pdf'.format(destination,sh_class), format='pdf')
		plt.close()	
