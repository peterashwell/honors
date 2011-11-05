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
PLOT_WIDTH = 0.9
def primary_plot(params, featset_fscore, featset_error, featnames, featset_desc, exp_desc, param_name, baseline_result):
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
		plt_color = colors[lnum % len(colors)]
		linespecs = '{0}{1}{2}'.format(linetype, markertype, plt_color)
		#print "marker:", markertype
		print "format:", linespecs
		#plt.plot(params, featset_fscore[featname], linespecs)#\
#			marker=markertype, color=plt_color, linestyle=linetype) #, PARAM_NAMES[param])
		e = plt.errorbar(params, featset_fscore[featname], featset_error[featname], fmt=linespecs, label=featset_desc[featname])
		for b in e[1]:
			    b.set_clip_on(False)
		print "params:", params
		print "fscores:", featset_fscore[featname]
	title = "Plot of F-Score versus {0} in the {1} experiment.".format(param_name.lower(), exp_desc.replace('%', '\%').lower())
	frame = plt.gca()
	if 'observed data' == param_name.lower():
		print "flipping x axis:"
		plt.xlim([10,100])
		frame.axes.invert_xaxis()
	if 'noise' == param_name.lower():
		plt.xlim([0,3.0])
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
	#legends = [featset_desc[featname] for featname in featnames]
	plt.legend(loc='best')
	fig_name = '{0}/{1}{2}_fsplot.eps'.format(FIG_DIR, exp_desc.replace(' ', '-').replace('.',','),\
		'-'.join([obj[2:] for obj in featnames]).replace(' ','-'))
	print "saving to:", fig_name
	plt.savefig(fig_name, format='eps')
	plt.close()
	
	fig_path = os.getcwd() + '/' + fig_name
	result_tex = ""
	#result_tex += '\\begin{figure}[ht!]\n'
	#result_tex += '\t\\label{fig:%s}\n' % (exp_desc.replace(' ', '-').replace('.',','))         
	result_tex += '\t\\centering\n'
	result_tex += '\t\\includegraphics[width=%f\\textwidth]{%s}\n' % (PLOT_WIDTH,fig_path)
	#result_tex += '\t\caption{%s}\n' %(title)
	#result_tex += '\\end{figure}\n'
	#result_tex += '\\newpage\n'
	return result_tex

NUM_TESTS = 200
HEAD_SPACE = 0.035
PARAMCOL_WIDTH = 0.05 # width of parameter column
CM_WIDTH = 0.28
LABEL_WIDTH = 0.09
YLABEL_WIDTH = 0.06 # width of "ACTUAL" label on side
XLABEL_HEIGHT = 10 # points
PARAMNAME_SPACER = 0.05

def confmat_page(param_vals, featnames, feat_desc, param_fs_cm, paramname, exp_desc):
	#print feat_desc
	#print featnames
	# First make the cells square (lol hacked)
	tex = "\\setlength{\\tabcolsep}{1.4pt}\n\\setlength{\\extrarowheight}{6.0pt}\n"
	#tex += "\\begin{figure}[ht!]\n"
	#tex += "\\label{fig:%s}\n" % (paramname.replace(' ','-') + '-' + '-'.join(featnames))
	tex += "\\begin{minipage}[c]{\\textwidth} \\centering \n" # TOP BOX
	tex += "\t\\begin{minipage}[c]{\\textwidth} \\centering \n" # STORES X LABEL
	tex += "\t\t\\begin{minipage}[c]{%f\\textwidth} \\centering \n" % (YLABEL_WIDTH + PARAMNAME_SPACER)
	tex += "\t\t\t\t\t\t\\quad\n"
	tex += "\t\t\\end{minipage}\n" # END XLABEL SPACER
	tex += "\t\t\\begin{minipage}[c]{%f\\textwidth} \\centering \n" % (1.0 - YLABEL_WIDTH - 0.01 - PARAMNAME_SPACER)
	tex += "\t\t\t\\large{Predicted}\n"
	tex += "\t\t\t\\vspace{%f pt}\n" % (XLABEL_HEIGHT)
	tex += "\t\t\\end{minipage}\n" # END Y LABEL
	tex += "\t\\end{minipage}\n" # END XLABEL BOX
	tex += "\t\\begin{minipage}[c]{\\textwidth} \\centering \n" # BEGIN MAIN BOX
	tex += "\t\t\\begin{minipage}[c]{%f\\textwidth} \\centering \n" % (YLABEL_WIDTH) # BEGIN YLABEL BOX 
	tex += "\t\t\t\\begin{sideways}\large{Actual}\\end{sideways}\n"
	tex += "\t\t\\end{minipage}\n"
	tex += "\t\t\\begin{minipage}[c]{%f\\textwidth} \\centering \n" % (1.0 - YLABEL_WIDTH - 0.01) # CM BOX
	# CM STUFF STARTS HERE
	tex += "\t\t\t\\begin{minipage}[c]{\\textwidth} \\centering \n"
	col_width = 0.85 / len(featnames)
	
	tex += "\t\t\t\t\\begin{minipage}[c]{\\textwidth}\n"	
	
	tex += "\t\t\t\t\t\\begin{minipage}[c]{%f\\textwidth}\n" % (PARAMCOL_WIDTH + LABEL_WIDTH)
	tex += "\t\t\t %s \n" % (paramname)
	tex += "\t\t\t\t\t\\end{minipage}\n"

	for fs in sorted(list(featnames))[:3]:
		tex += "\t\t\t\t\t\\begin{minipage}[c]{%f\\textwidth}\n" % (CM_WIDTH)
		tex += "\t\t\t\t\t\t\\centering\n"
		tex += "\t\t\t\t\t\t\\small{\n"
		fd = feat_desc[fs]
		fd_formatted = ' - '.join(["\\emph{" + (o.strip()) + "}" for o in fd.split('-')])
		tex += "\t\t\t\t\t\t{0}\n".format(fd_formatted)
		tex += "\t\t\t\t\t\t}\n"
		tex += "\t\t\t\t\t\\end{minipage}\n"
	tex += "\t\t\t\t\\end{minipage}\n"
	first_row = True # so we don't overadd rows to legend
	for p in param_vals:
		tex += "\t\t\t\t\\vspace{5pt}\n"
		tex += "\t\t\t\t\\begin{minipage}[c]{\\textwidth}\n"
		tex += "\t\t\t\t\t\\begin{minipage}[c]{%f\\textwidth}\n" % (PARAMCOL_WIDTH)
		tex += "\t\t\t\t\t\t\\centering\n"
		tex += "\t\t\t\t\t\t{0}\n".format(p)
		tex += "\t\t\t\t\t\\end{minipage}\n"
		tex += "\t\t\t\t\t\\begin{minipage}[c]{%f\\textwidth}\n" % (LABEL_WIDTH)
		tex += "\t\t\t\t\t\t\\tiny {\n"
		tex += "\t\t\t\t\t\t\\vspace{-4pt}"
		tex += "\t\t\t\t\t\t\\begin{tabular}{lr}\n"
		if first_row:
			tex += "\t\t\t\t\t\t & \\\\ \n"
		for rownum, classname in enumerate(sorted(CLASSES)): # defined at top
			tex += "\t\t\t\t\t\t{1} & {0}\\\\ \n".format(chr(ord('A') + rownum), classname)
		tex += "\t\t\t\t\t\t\\end{tabular}\n"
		tex += "\t\t\t\t\t\t}\n"
		tex += "\t\t\t\t\t\\end{minipage}\n"
		for fs in sorted(list(featnames))[:3]:
			print "fs:", fs
			tex += "\t\t\t\t\t\\begin{minipage}[c]{%f\\textwidth}\n" % (CM_WIDTH)
			tex += "\t\t\t\t\t\t\\centering\n"
			tex += "\t\t\t\t\t\t\\tiny {\n"
			tex += "\t\t\t\t\t\t\\begin{tabular}{|c|c|c|c|c|c|c|c|}\n"
			if first_row:
				tex += "\t\t\t\t\t\t" + " & ".join(["\\multicolumn{1}{c}{" + chr(ord('A') + o) + "}" for o in range(8)]) + '\\\\ \n'
			tex += "\\hline\n"
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
					color = "\\cellcolor[rgb]{1.0,%f,%f}" % (1 - float(elem),1 - float(elem))					
					if math.fabs(1.0 - elem) < 1e-10:
						cell = '1.0'
					elif math.fabs(0.0 - elem) < 1e-10:
						cell = '\\verb#  #'
					else:
						cell = str(elem)[1:4]
					colored_row.append(color + ' ' + cell)
				tex += ' & '.join([str(o) for o in colored_row]) + '\\\\ \\hline\n'
			tex += "\t\t\t\t\t\t\\end{tabular}\n"
			tex += "\t\t\t\t\t}\n"
			tex += "\t\t\t\t\t\\end{minipage}\n"
		tex += "\t\t\t\t\\end{minipage}\n"
		first_row = False # stop adding legend
	tex += "\t\t\t\\end{minipage}\n"
	tex += "\t\t\\end{minipage}\n" # END YLABEL BOX
	tex += "\t\\end{minipage}\n" # END TOP BOX
	tex += "\\end{minipage}\n" # END TOP BOX
	#tex += "\\caption{%s}\n" % ("Confusion matrices for the {0} experiment".format(exp_desc))
	#tex += "\\end{figure}\n"
	# Unsquare the cells so your tables aren't all screwed up
	tex += "\\setlength{\\tabcolsep}{6pt}\n\\setlength{\\extrarowheight}{0pt}\n"
	tex += "\\newpage\n"
	#print tex
	return tex

MAX_SUBFIG_COLS = 5
SAMPLE_DIR = '/Users/peter/honors/thesis/experiments/exp_shapelets/figures/samples'
def exp_subfigs(exp_fname, param_val, mp_width):
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
		plt.savefig(SAMPLE_DIR + '/' + plot_fname, format='eps')
		plt.close()

		# now write out corresponding latex
		# new code - minipage
		tex_out += '\\begin{minipage}[c]{%f\\linewidth}\n' % (mp_width)
		tex_out += '\t\\includegraphics[width=\\textwidth]{%s}\n' % (SAMPLE_DIR + '/' + plot_fname)
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
	#out_tex += '\\begin{figure}[ht!]\n'
	#out_tex += '\\centering\n'
	out_tex += '\\begin{minipage}[c]{\\textwidth}\n'
	out_tex += '\\begin{minipage}[b]{0.1\\linewidth}\n'
	out_tex += '\\centering\n\t%s\n\\end{minipage}\n' % (param_name)
	mp_width = 0.85 / len(CLASSES)
	for lct in CLASSES:
		out_tex += '\\begin{minipage}[c]{%f\\linewidth}\n' % (mp_width)
		out_tex += '\\centering\n%s\n\\end{minipage}\n' % (lct)
	out_tex += '\\\\\n'
	for exp_num, exp_fname in enumerate(exp_fnames):
		# old stuff - subfigs
		#out_tex += '\\begin{figure}[ht!]\n')
		#out_tex += '\t\\centering\n')
	
		out_tex += exp_subfigs(exp_fname, params[exp_num], mp_width)
			
		#old stuff - writes out subfigs
		#out_tex += '\\caption{%s with %s at %s}\n' \
		#	% (exp_fname.replace('_', '-').replace('.',','), param_name, params[exp_num]))
		#out_tex += '\\end{figure}\n')	
	#out_tex += '\\caption{Sample lightcurves for the %s experiment}\n' % (exp_desc.lower())
	out_tex += '\\end{minipage}\n'
	#out_tex += '\\end{figure}\n'
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
		this_prec = 0
		this_recall = 0
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
	
	plt.rcParams.update({'font.size': 16})
	NUM_BINS = 50
	#BIN_SIZE = 1.0 / NUM_BINS
	#print "BIN SIZE:", BIN_SIZE
	#BINS = numpy.linspace(0, 1, NUM_BINS)
	HIST_HEIGHT = 1 # Height of each histogram
	sh_max = {}
	for shnum, sh_class in enumerate(sh_ts_distances.keys()):
		# Compute the maximum distance for this shapelet across all classes
		# Want to squash the diagonals correctly for the split line
		SHAPELET_MAX_DIST = -1
		for test_class in sh_ts_distances[sh_class].keys():
			m = max(sh_ts_distances[sh_class][test_class])
			if m > SHAPELET_MAX_DIST:
				SHAPELET_MAX_DIST = m
		sh_max[sh_class] = SHAPELET_MAX_DIST

	for shnum, sh_class in enumerate(sorted(sh_ts_distances.keys())):
		print "ts_distances:"
		print sh_ts_distances[sh_class]
		#fig = plt.figure()
		for tsnum, ts_class in enumerate(sorted(sh_ts_distances[sh_class].keys())):
			lbound = 0
			rbound = sh_max[sh_class]
			binsize = (rbound - lbound) / NUM_BINS
			BINS = numpy.linspace(lbound, rbound, NUM_BINS)
			BINS = numpy.append(BINS,rbound)
			BINS = numpy.insert(BINS,lbound, 0) # fill polygon correctly
			distances = sh_ts_distances[sh_class][ts_class]
			#print "distances:"
			#print distances
			hist = (numpy.histogram(distances, NUM_BINS, (lbound, rbound))[0])
			#print "raw histogram:"
			#print hist
			hist = hist / (1.0 * numpy.sum(hist, axis=0)) * 2 # for extra clarity
			
			print "HIST (before adding):"
			print hist
			
			hist = numpy.append(hist, 0)
			hist = numpy.insert(hist,0,0) # fill polygon correctly
			print "after:"
			print hist
			#print "shapelet:", sh_class
			#print "ts_class:", ts_class
			#print "histogram:"
			#print hist
			#print HIST_HEIGHT * tsnum + 1
			#print len(hist)
			hist += HIST_HEIGHT * tsnum # to get the right height
			barcol = 'r'
			if ts_class == sh_class:
				barcol = 'g'
			p = plt.fill(BINS,hist,barcol,alpha=0.5)	
			plt.xlim([lbound,rbound])
			plt.ylim([0,9])
			print "BINS:"
			print BINS
			print "HIST:"
			print hist
		frame = plt.gca()
		#frame.axes.axis["right"].set_visible(False)
		#frame.axes.axis["top"].set_visible(False)
		frame.axes.get_yaxis().set_ticklabels(sorted(sh_ts_distances[sh_class].keys()))
		frame.axes.get_yaxis().set_ticks([o + 0.5 for o in range(8)])
		plt.xlabel('Distance measure')
		plt.ylabel('Class')
		print "saving figure to:", '{0}/{1}_sm.pdf'.format(destination, sh_class)
		plt.savefig('{0}/{1}_sm.pdf'.format(destination,sh_class), format='pdf')
		plt.close()
	


#	for shnum, sh_class in enumerate(sh_ts_distances.keys()):
#		print "building specific histogram for class:", sh_class
#		fig = plt.figure()
#		for tsnum, ts_class in enumerate(sh_ts_distances[sh_class].keys()):
#			class_distances = sh_ts_distances[sh_class][ts_class]
#			squashed_distances = [d / (1.0 * sh_max[sh_class]) for d in class_distances]
#			right_lim = sh_right[sh_class]
#			left_lim = sh_left[sh_class]
#			NUM_BINS = 200
#			print "right lim:", right_lim
#			print "left lim:", left_lim
#			BIN_SIZE = (right_lim - left_lim) / NUM_BINS
#			BINS = numpy.linspace(left_lim, right_lim, NUM_BINS)
#			
#			hist = numpy.histogram(squashed_distances, BINS, normed=True)[0].tolist()
#			print "marker 1a"	
#			hist = hist / numpy.sum(hist, axis=0)
#			print "marker 1b"
#			p = plt.bar(numpy.linspace(left_lim,right_lim,NUM_BINS)[:-1], hist, BIN_SIZE,\
#				color=COLOURS[tsnum % len(COLOURS)], bottom = HIST_HEIGHT * tsnum, alpha=1.0)	
#			
#			plt.xlim([left_lim,right_lim])
#		frame = plt.gca()
#		frame.axes.get_yaxis().set_ticklabels(sorted(sh_ts_distances[sh_class].keys()))
#		frame.axes.get_yaxis().set_ticks([o + 0.5 for o in range(8)])
#		plt.xlabel('Distance measure (normalised across all shapelets)')
#		plt.ylabel('Class')
#		plt.savefig('{0}/{1}_sm_specific.pdf'.format(destination,sh_class), format='pdf')
#		plt.close()	
