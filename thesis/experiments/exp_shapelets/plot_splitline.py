import utils
import sys
import os
from matplotlib.axes import Subplot
import matplotlib.pyplot as plt
from lightcurve import *
import distances
import numpy

# Produces histograms of the mindist distance measure using
# Shapelets and test light curves in the given directories
NUM_CROSSFOLDS = 10
# Usage plot_splitlines.py <shapelet_lc_dir> <dir_to_test_on>
shapelet_dir = sys.argv[1]
test_dir = sys.argv[2]
out_dir = 'shapelet_analysis/{0}'.format(shapelet_dir.split('/')[-1])
if not os.path.isdir(out_dir):
	os.mkdir(out_dir)
# Load shapelet files one by one and store distances per test class
sh_ts_distances = {}
for cfnum in xrange(1):
	load_dir = '{0}/cf{1}'.format(shapelet_dir, cfnum)
	for shapelet_file in os.listdir(load_dir):
		if shapelet_file == '.DS_Store':
			continue
		print "reading shapelet:", shapelet_file
		shapelet_class = shapelet_file.split('_')[0]
		shapelet_path = '{0}/{1}'.format(load_dir, shapelet_file)
		shapelet_ts = file_to_lc(shapelet_path)
		# Evaluate on the test directory
		min_distances = {} # maps class to min_dist
		test_cf_list = 'crossfold/cf{0}/test'.format(cfnum)
		for test_filename in open(test_cf_list):
			test_filename = test_filename.strip()
			test_path = '{0}/{1}'.format(test_dir, test_filename)
			print "reading test file:", test_path
			test_ts = file_to_lc(test_path)
			test_class = test_filename.split('_')[0]
			distance = distances.mindist(test_ts.flux, shapelet_ts.flux)[0]
			if shapelet_class not in sh_ts_distances.keys():
				new_dict = {test_class : [distance]} # new mapping for this ts class and distance
				sh_ts_distances[shapelet_class] = new_dict
			else:
				if test_class not in sh_ts_distances[shapelet_class].keys():
					sh_ts_distances[shapelet_class][test_class] = [distance]
				else:
					sh_ts_distances[shapelet_class][test_class].append(distance)
		out_dir = "{0}/cf{1}".format(out_dir, cfnum)
		print "creating split line"
		utils.plot_splitline(sh_ts_distances, out_dir)
#sh_classes =  sh_ts_distances.keys()
# Now produce a histogram for this shapelet showing these distances
#fig = plt.figure()
#colors = ['b', 'g', 'r', 'm', 'y']
#bins = [1.0 / 100.0 * i for i in xrange(100)]

# Find the maximum of any distance to squash them with
#max_dist = -1
#for sk in sh_ts_distances.keys():
#	for tsk in sh_ts_distances[sk].keys():
#		this_max = max(sh_ts_distances[sk][tsk])
#		if this_max > max_dist:
#			max_dist = this_max
#print "max dist:", max_dist
#
#NUM_BINS = 200
#BIN_SIZE = 1.0 / NUM_BINS
#BINS = numpy.linspace(0, 1, NUM_BINS)
#HIST_HEIGHT = 1 # Height of each histogram
#
#sh_ts_hist = {}
#sh_left = {}
#sh_right = {}
#for shnum, sh_class in enumerate(sh_ts_distances.keys()):
#	fig = plt.figure()
#	legend = [[], []]
#	for tsnum, ts_class in enumerate(sorted(sh_ts_distances[sh_class].keys())):
#		legend[1].append(ts_class)
#		# First step, just get a separate figure for each (maybe lay out in tex)
#		class_distances = sh_ts_distances[sh_class][ts_class]
#		# Normalise and bin the distances
#		squashed_distances = [d / (1.0 * max_dist) for d in class_distances]
#		#print squashed_distances
#		#print BINS
#		hist = numpy.histogram(squashed_distances, BINS, normed=True)[0]
#		hist = hist / numpy.sum(hist, axis=0)
#		hist = hist.tolist()
#		print "hist:", hist
#		if sh_class == ts_class: # check the std and mean of histogram
#			this_max = max(squashed_distances)
#			left_lim = min(squashed_distances)
#			spread = this_max - left_lim + 0.05 # have at least a small spread
#			sh_left[sh_class] = max(0, left_lim - spread)
#			sh_right[sh_class] = min(1, this_max + spread)
#			print this_max, "dist_max"
#			print left_lim, "dist_min"
#			print spread, "spread"
#			print "distances:"
#		if sh_class not in sh_ts_hist.keys():
#			new_dict = {ts_class : hist}
#			sh_ts_hist[sh_class] = new_dict
#		else:
#			sh_ts_hist[sh_class][ts_class] = hist
#		#print hist
#		#print len(hist)
#		#p = plt.bar(numpy.linspace(0,1,NUM_BINS)[:-1], hist, BIN_SIZE,\
#		#	color=colors[tsnum % len(colors)], bottom = HIST_HEIGHT * tsnum, alpha=1.0)	
#		#plt.xlim([0,1])
#		#legend[0].append(p[0])
#	#frame = plt.gca()
#	#frame.axes.get_yaxis().set_ticklabels(sorted(sh_ts_distances[sh_class].keys()))
#	#frame.axes.get_yaxis().set_ticks([o + 0.5 for o in range(8)])
#	#fig.axis().set_ticklabels([sorted(sh_ts_distances[sh_class])])
#	#plt.legend(legend[0], legend[1])
#	#plt.xlabel('Distance measure (normalised across all shapelets)')
#	#plt.ylabel('Class')
#	#cf_dir = '{0}/cf{1}'.format(out_dir, cfnum)
#	#if not os.path.isdir(cf_dir):
##		os.mkdir(cf_dir)
#	#plt.savefig('{0}/{1}_sm.pdf'.format(cf_dir,sh_class), format='pdf')
#	#plt.close()
#for shnum, sh_class in enumerate(sh_ts_hist.keys()):
#	fig = plt.figure()
#	for tsnum, ts_class in enumerate(sh_ts_hist[sh_class].keys()):
#		hist = sh_ts_hist[sh_class][ts_class]
#		p = plt.bar(numpy.linspace(0,1,NUM_BINS)[:-1], hist, BIN_SIZE,\
#			color=colors[tsnum % len(colors)], bottom = HIST_HEIGHT * tsnum, alpha=1.0)	
#		plt.xlim([0,1])
#		legend[0].append(p[0])
#	frame = plt.gca()
#	frame.axes.get_yaxis().set_ticklabels(sorted(sh_ts_distances[sh_class].keys()))
#	frame.axes.get_yaxis().set_ticks([o + 0.5 for o in range(8)])
#	#fig.axis().set_ticklabels([sorted(sh_ts_distances[sh_class])])
#	#plt.legend(legend[0], legend[1])
#	plt.xlabel('Distance measure (normalised across all shapelets)')
#	plt.ylabel('Class')
#	cf_dir = '{0}/cf{1}'.format(out_dir, cfnum)
#	if not os.path.isdir(cf_dir):
#		os.mkdir(cf_dir)
#	plt.savefig('{0}/{1}_sm.pdf'.format(cf_dir,sh_class), format='pdf')
#	plt.close()
#
#for shnum, sh_class in enumerate(sh_ts_distances.keys()):
#	fig = plt.figure()
#	for tsnum, ts_class in enumerate(sh_ts_distances[sh_class].keys()):
#		#left_lim = max(0, sh_mean[sh_class] - 3 * sh_std[sh_class])
#		#right_lim = min(1, sh_mean[sh_class] + 3 * sh_std[sh_class])
#		
#		class_distances = sh_ts_distances[sh_class][ts_class]
#		squashed_distances = [d / (1.0 * max_dist) for d in class_distances]
#		right_lim = sh_right[sh_class]
#		left_lim = sh_left[sh_class]	
#		#left_lim = max(0, left_lim - spread)
#		#right_lim = min(1, right_lim + spread)
#		# Normalise and bin the distances
#		NUM_BINS = 200
#		BIN_SIZE = (right_lim - left_lim) / NUM_BINS
#		BINS = numpy.linspace(left_lim, right_lim, NUM_BINS)
#		
#		hist = numpy.histogram(squashed_distances, BINS, normed=True)[0].tolist()
#		hist = hist / numpy.sum(hist, axis=0)
#	
#		p = plt.bar(numpy.linspace(left_lim,right_lim,NUM_BINS)[:-1], hist, BIN_SIZE,\
#			color=colors[tsnum % len(colors)], bottom = HIST_HEIGHT * tsnum, alpha=1.0)	
#		
#		plt.xlim([left_lim,right_lim])
#		legend[0].append(p[0])
#	frame = plt.gca()
#	frame.axes.get_yaxis().set_ticklabels(sorted(sh_ts_distances[sh_class].keys()))
#	frame.axes.get_yaxis().set_ticks([o + 0.5 for o in range(8)])
#	#fig.axis().set_ticklabels([sorted(sh_ts_distances[sh_class])])
#	#plt.legend(legend[0], legend[1])
#	plt.xlabel('Distance measure (normalised across all shapelets)')
#	plt.ylabel('Class')
#	cf_dir = '{0}/cf{1}'.format(out_dir, cfnum)
#	if not os.path.isdir(cf_dir):
#		os.mkdir(cf_dir)
#	plt.savefig('{0}/{1}_sm_specific.pdf'.format(cf_dir,sh_class), format='pdf')
#	plt.close()
#
#	
