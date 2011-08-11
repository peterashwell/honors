import os
import random
import getopt
import matplotlib.pyplot as plt
import re

from plot_utils import *

BASELINE_EXP='norm_n0_a100_m0_s400'
RESULT_DIR = 'results'
PARAM_NAMES = {'a':'Observed data', 'n':'Noise', 'm':'Missing data', 'p':'Power law distribution'}
EXPDESC_FNAME = '../experiment_commands' 
FEATNAME_FNAME = 'features.names'
# process experiment file and produce latex output
exp_file = open(EXPDESC_FNAME)
latex_output = open('results.tex', 'w')

# write the latex preamble
write_preamble(latex_output)

# read each experiment result and produce a report
exp_desc = None
baseline_result = None
baseline_fscores = None
baseline_powlaw_result = None
baseline_powlaw_fscores = None
cur_param = None

# stores data from each experiment's subtrial (in order)
#precs = []
#recalls = []
fscores = []
cms = []
cm_orders = []
param_vals = []
subexp_fnames = [] # names of result files for each subtrial
all_featnames = []

for line in exp_file:
	if line[0] == '#': # new experiment, write out old one
		if exp_desc is not None:
			if param != 'b' \
				and param != 'c' \
				and param != 'p':
				#and param != 'c': # if we have something to wiction({0})'.format(exp_desc))
				# write results table
				write_table(latex_output, exp_desc, PARAM_NAMES[param], \
					param_vals, fscores, exp_desc)
				# now produce a plot with matplotlib for the experiment
				produce_figure(latex_output, exp_desc, param_vals, fscores, PARAM_NAMES[param], baseline_result, baseline_powlaw_result)
				# and sample figures
				produce_expsamp(latex_output, subexp_fnames, param_vals, PARAM_NAMES[param])
				write_cm(latex_output, PARAM_NAMES[param], cms, param_vals, cm_orders, exp_desc)  	
				latex_output.write('\\clearpage\n')
			elif param == 'b':
				latex_output.write('\\section{Baseline}\n')
				write_cm(latex_output, 'Baseline', cms, [True], cm_orders, exp_desc)  	
			elif param == 'p':
				write_cm(latex_output, PARAM_NAMES[param], cms, [True], cm_orders, exp_desc)
				latex_output.write('\\clearpage\n')
		line = line.strip()[1:].split('\t')
		param = line[0]
		exp_desc = line[1]
		
		# empty all records regarding last experiment
		# organise precision, recall and fscore according to featureset
		subexp_fnames = []
		#precs = {}
		#recalls = {}
		fscores = {}
		cms = [] # for all features only
		cm_orders = [] # all features only
		param_vals = []
		featname_file = open(FEATNAME_FNAME)
		for featname in featname_file:
			featname = featname.strip()
			all_featnames.append(featname)
			#precs[featname] = []
			#recalls[featname] = []
			fscores[featname] = {}
		featname_file.close()
			
	else: # routine in experiment
		exp_fname, param_val = systematic_name(line.strip(), param)
		subexp_fnames.append(exp_fname)
		
		featname_file = open(FEATNAME_FNAME)
		for featname in featname_file:
			featname = featname.strip()
			result_fname = '{0}/{1}/{2}.result'.format(RESULT_DIR, featname.strip(), exp_fname)
			result_file = open(result_fname)
			print result_fname
			# store precision recall and fscore as tuple
			#precision = result_file.readline().strip().split('\t')[1]
			#recall = result_file.readline().strip().split('\t')[1]
			#fscore = result_file.readline().strip().split('\t')[1]
			num_classes = int(result_file.readline().strip())
			for cn in xrange(num_classes + 1): # account for 'all' class
				line = result_file.readline().strip().split(',')
				class_name = line[0]
				fscore = str(round(float(line[3]),2))
				if class_name not in fscores[featname].keys():
					fscores[featname][class_name] = [fscore]
				else:
					fscores[featname][class_name].append(fscore)
				#print 'class:', class_name
			#print fscores
			if param == 'b':
				baseline_fscores = fscores
			if param == 'p':
				baseline_powlaw_fscores = fscores
			# record metrics for all feature
			if featname == 'all':
				# if this is a 'baseline' result, store it
				if param == 'b':
					baseline_result = fscore
				if param == 'p':
					powlaw_baseline_result = fscore
				param_vals.append(param_val)
				# extract the confusion matrix
				cm = []
				cm_order = []
				for line in result_file:
					if line.strip() != '':
						line = line.split('\t')
						cm_order.append(line[0])
						cm.append(line[1:])
				cms.append(cm)
				cm_orders.append(cm_order)
			result_file.close()
# done
latex_output.write('\\end{document}')
exp_file.close()
latex_output.close()
