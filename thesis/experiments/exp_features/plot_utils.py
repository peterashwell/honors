import getopt
import os
import random
from lightcurve import *

LC_TYPES = []
classes_desc_file = open('classes.desc')
for line in classes_desc_file:
	print line
	line = line.strip()
	LC_TYPES.append(line)
print 'lct:', LC_TYPES
LC_DIR = 'lightcurves'
FIG_DIR = '/users/peter/honors/thesis/experiments/exp_features/temp_figures'

def systematic_name(options, param):
	param_val = None
	options = options.strip()
	# produce systematic name for experiment conditions
	noise = 0
	available_pct = 100
	missing = 0
	max_size = 400
	opts, args = getopt.getopt(options.split(' '), "dun:a:m:")
	exp_fname = ''
	for opt, arg in opts:
		if opt == '-u':
			exp_fname += 'norm'
		if opt == '-d':
			exp_fname += 'powlaw'
		if opt == '-n':
			if param == 'n':
				param_val = arg
			noise = arg
		if opt == '-a':
			available_pct = arg
			if param == 'a':
				param_val = arg
		if opt == '-m':
			missing = arg		
			if param == 'm':
				param_val = arg
	exp_fname += '_n' + str(noise)
	exp_fname += '_a' + str(available_pct)
	exp_fname += '_m' + str(missing)
	exp_fname += '_s' + str(max_size)
	return (exp_fname, param_val)

PREAMBLE_FNAME = 'preamble_default.txt'
def write_preamble(file_handle):
	preamble_file = open(PREAMBLE_FNAME)
	file_handle.write(preamble_file.read())
	preamble_file.close()

TABLE_FNAME = 'table.template'
FEATNAME_FNAME = 'features.names'

def write_table(file_handle, exp_name, param_name, \
param_vals, fscores, exp_desc):
	file_handle.write('\\section{%s}' % (exp_name.replace('%', '\\%')))
	file_handle.write('\\begin{table}[ht!]\n\t\\centering\n')
	file_handle.write('\\footnotesize\n')
	featname_file = open(FEATNAME_FNAME)
	featnames = []
	for featname in featname_file:
		featnames.append(featname.strip())
	classes = fscores[featname.strip()].keys() # TODO fix this hard coding
	print "pv:", param_vals
	file_handle.write('\t\\begin{tabular}{|c|c|%s} \\hline' % ('l|' * len(param_vals)))
	file_handle.write('\t \\multirow{2}{*}{\\textbf{Feature}} & \\multirow{2}{*}{\\textbf{Class}} \
	& \\multicolumn{%d}{c|}{\\textbf{%s}} \\\\ \\cline{%s} \n' % (len(param_vals), param_name.title(), '{0}-{1}'.format(3, len(param_vals) + 2))) 
	file_handle.write('\t  & & {0} \\\\ \\hline'.format(' & '.join(param_vals)))
	for featname in featnames:
		file_handle.write('\t\t\\multirow{%d}{*}{%s}\n' %(len(classes), featname.replace('_', '-')))
		
		classes.remove('all')
		classes.append('all')
		for class_name in classes:
			file_handle.write('& {0}'.format(class_name))
			for pn, param_val in enumerate(param_vals):
				file_handle.write(' & {0}'.format(fscores[featname][class_name][pn]))
			#print precs
			#print recalls
			#print fscores
			#	print pn, param_val
			#print precs[featname], recalls[featname], fscores[featname]
			#	file_handle.write('\t\t & %s & %s & %s & %s \\\\\n'\
			#	 % (featname.replace('_', '-'), precs[featname][pn], recalls[featname][pn], fscores[featname][pn]))
			file_handle.write(' \\\\\n')
		file_handle.write('\\hline')
	file_handle.write('\t\\end{tabular}\n')
	file_handle.write('\t\\caption{F-Score of classification per class in the %s experiment}\n' % (exp_desc.lower()))
	file_handle.write('\\end{table}\n')

import matplotlib.pyplot as plt
import matplotlib as mpl

def produce_figure(file_handle, exp_desc, param_vals, fscores, param_name, baseline_result, baseline_powlaw_result):
	mpl.rc('legend', fontsize=10)
	featnames = []
	featname_file = open(FEATNAME_FNAME)
	for featname in featname_file:
		featnames.append(featname.strip())
	plt.clf()
	# plot baseline
	plt.plot(param_vals, len(param_vals) * [baseline_result]) #, label='Baseline')
	linetypes = ['--', ':']
	markertypes = ['o', 'x', 'd', 's', '^']
	colors = ['r', 'g', 'c', 'm', 'y', 'k']
	for lnum, featname in enumerate(featnames):
		#print fscores[featname]
		linetype = '--'
		if lnum > len(markertypes):
			linetype = ':'
		markertype = markertypes[lnum % len(markertypes)]
		color = colors[lnum % len(colors)]
		linespecs = '{0}{1}{2}'.format(linetype, markertype, color)
		plt.plot(param_vals, fscores[featname]['all'], linespecs) #, PARAM_NAMES[param])
	plt.title("F-Score versus {0} in {1}".format(param_name.lower(), exp_desc.replace('%', '\%').lower()))
	plt.xlabel(param_name)
	plt.ylabel("F-Score")
	plt.ylim([0,1])
	# fix subtractive naming in featnames
	for index, fn in enumerate(featnames):
		if 'all' in fn:
			pass
		else:
			featnames[index] = 'all - {' + featnames[index] + '}'
	legends = tuple(['Baseline'] + featnames)
	plt.legend(legends, loc='best')
	plt.savefig('{0}/{1}_fsplot.eps'.format(FIG_DIR, exp_desc.replace(' ', '-').replace('.',',')), format='eps')
	plt.close()
	
	file_handle.write('\\begin{figure}[ht!]\n')
	file_handle.write('\t\\centering\n')
	file_handle.write('\t\\includegraphics[width=\\textwidth]{%s}\n' % (FIG_DIR + '/' + \
		exp_desc.replace(' ', '-').replace('.',',') + '_fsplot.eps'))
	file_handle.write('\\end{figure}\n')

def write_cm(file_handle, param_name, cms, param_vals, cm_orders, exp_desc):
	MAX_CM_COLS = 30
	LET_A_ASCII = 97
	cols_per_cm = len(cms[0])
	cm_width = round((MAX_CM_COLS  * 0.90 / cols_per_cm) / 100.0, 2)
	file_handle.write('\\begin{figure}[ht!]\n')
	file_handle.write('\t\\centering\n')
	for cm, param_val, cm_order in zip(cms, param_vals, cm_orders):
		file_handle.write('\ttiny{\\subfigure[%s at %s] {\n'\
			 % (param_name, param_val))
	
		file_handle.write('\t\\begin{tabular}{|%s|} \hline\n' % ('l|' + 'l' * len(cm)))
		file_handle.write('\t\t & %s\\\\ \hline\n' % (' & '.join([chr(i + LET_A_ASCII) for i in xrange(len(cm_order))])))
		file_handle.write('%s \\\\ \hline\n' \
			% ('\\\\\n'.join(\
				[chr(num + LET_A_ASCII) + ') ' + cm_order[num][:3] + ' & ' + ' & '.join(li) for num, li in enumerate(cm)])))
		file_handle.write('\t\\end{tabular}\n')
		file_handle.write('}}\n')
	file_handle.write('\\caption{Confusion matrices for the %s experiment}\n' % (exp_desc.lower()))
	file_handle.write('\\end{figure}\n')

MAX_SUBFIG_COLS = 5
def exp_subfigs(file_handle, exp_fname, param_val):
	print 'exp_fname:', exp_fname
	subfig_count = 0
	width = round(100.0 / MAX_SUBFIG_COLS * 0.88 / 100.0, 3)
	
	# 2 lines below - new code - minipages
	file_handle.write('\\begin{minipage}[b]{0.1\\linewidth}\n')
	file_handle.write('\t\\centering\n\t%s\n\\end{minipage}\n' % (param_val))
	for lc_num, lc_type in enumerate(LC_TYPES):
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
		mp_width = 0.8 / len(LC_TYPES)
		file_handle.write('\\begin{minipage}[c]{%f\\linewidth}\n' % (mp_width))
		file_handle.write('\t\\includegraphics[width=\\textwidth]{%s}\n' % (FIG_DIR + '/' + plot_fname))
		file_handle.write('\\end{minipage}\n')

		# old code - subfigures
		#file_handle.write('\\subfigure[%s] {\n' % (lc_type))
		#file_handle.write('\t\\includegraphics[width=%f\\textwidth]{%s}\n' % (width, FIG_DIR + '/' + plot_fname))
		#file_handle.write('}\n')

		subfig_count += 1
		if subfig_count % len(LC_TYPES) == 0 and subfig_count != 0:
			file_handle.write('\\\\\n')

def produce_expsamp(file_handle, exp_fnames, params, param_name, exp_desc):
	print 'exp_fnames', exp_fnames
	file_handle.write('\\begin{figure}[ht!]\n')
	file_handle.write('\\centering\n')
	file_handle.write('\\begin{minipage}[b]{0.1\\linewidth}\n')
	file_handle.write('\\centering\n\t%s\n\\end{minipage}\n' % (param_name))
	mp_width = 0.8 / len(LC_TYPES)
	for lct in LC_TYPES:
		file_handle.write('\\begin{minipage}[c]{%f\\linewidth}\n' % (mp_width))
		file_handle.write('\\centering\n%s\n\\end{minipage}\n' % (lct))
	file_handle.write('\\\\\n')
	for exp_num, exp_fname in enumerate(exp_fnames):
		# old stuff - subfigs
		#file_handle.write('\\begin{figure}[ht!]\n')
		#file_handle.write('\t\\centering\n')
	
		exp_subfigs(file_handle, exp_fname, params[exp_num])
			
		#old stuff - writes out subfigs
		#file_handle.write('\\caption{%s with %s at %s}\n' \
		#	% (exp_fname.replace('_', '-').replace('.',','), param_name, params[exp_num]))
		#file_handle.write('\\end{figure}\n')	
	file_handle.write('\\caption{Sample lightcurves for the %s experiment}\n' % (exp_desc.lower()))
	file_handle.write('\\end{figure}\n')
