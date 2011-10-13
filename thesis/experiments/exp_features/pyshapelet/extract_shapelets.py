import sys
import os
import shapelet_utils
import psyco
import time
psyco.full()

TS_DELIM = '\t' # Delimeter of time series file
NUM_SHAPELETS = 40 # Default number of shapelets to try
MIN_LENGTH = 10 # Minimum shapelet length (in days)
MAX_LENGTH = 100 # Maximum shapelet length (in days)

MAX_PER_CLASS = 5 # Max number of shapelets per each class
if len(sys.argv) <= 1:
	print "usage: python extract_shapelets.py <in> <out> <num_shapelets> <min_len> <max_len>"
	print "<in> is directory of light curves to extract shapelets from"
	print "<out> is directory to store shapelets in (as time series)"
	print "<num_shaplets> number of shapelets to find"
	print "<min_len> and <max_len> min and max length of shapelets"
in_dir = sys.argv[1] # directory of light curves to extract shapelets
out_dir = sys.argv[2] # directory to store shapelets in (as time series)
if len(sys.argv) > 3:
	NUM_SHAPELETS = sys.argv[3]
	MIN_LENGTH = sys.argv[4]
	MAX_LENGTH = sys.argv[5]

# 1) Load training light curves into memory as a list of [list, list] objects
dataset = []
classes = set()
train_fnames = os.listdir(in_dir)
ts_classes = {}
class_tses = {}
ts_filenames = {}
print len(train_fnames)
for tf in train_fnames:
	classname = tf.split('_')[0]
	if classname not in classes:
		classes.add(classname)
	ts_file = open("{0}/{1}".format(in_dir, tf))
	tstime = []
	tsflux = []
	for line in ts_file:
		line = line.strip().split(TS_DELIM)
		assert len(line) == 2 # If TS_DELIM has changed...
		tstime.append(float(line[0]))
		tsflux.append(float(line[1]))
	ts = (tuple(tstime), tuple(tsflux))
	dataset.append(ts)
	ts_classes[ts] = classname
	ts_filenames[ts] = tf
	if classname in class_tses.keys():
		class_tses[classname].append(ts)
	else:
		class_tses[classname] = [ts]
print "read {0} training light curves".format(len(dataset))
print [len(class_tses[cn]) for cn in class_tses.keys()]
#print classes
#print dataset
# 2) Find shapelets that best separate training set
#		- Uses distance measure imported from shapelet_utils
#		- Uses information gain for dataset imported from shapelet_utils

# Iterate over all subsequences in dataset, keeping track of best <num_shapelet> shapelets
class_shapelets = {} # Shapelets with keys as source class codes
infgain = {} # mapping of shapelets element n to its information gain
THRESHOLD = 10 # test threshold
class_labels = []
for c in class_tses.keys():
	class_labels += len(class_tses[c]) * [c]
DATASET_ENTROPY = shapelet_utils.entropy(class_labels, class_tses.keys())
print "DATASET_ENTROPY:", DATASET_ENTROPY
start_time = time.time()
for upto, ts in enumerate(dataset):
	# Extract shapelets and their information gain from time series ts
	if upto % 1 == 0:
		print "{0}/{1} processed".format(upto, len(dataset))
	ts_class = ts_classes[ts]
	for slen in xrange(MIN_LENGTH, MAX_LENGTH + 1, 10):
		print "\tslen {0}/{1}".format(slen - MIN_LENGTH, MAX_LENGTH + 1 - MIN_LENGTH)
		ts_length = len(ts[0]) # ok because no missing data
		for start_pos in xrange(0, len(ts[0]) - slen + 1):
			print "\t\tstart_pos {0}/{1}".format(start_pos, len(ts[0]) - slen + 1)
			print "elapsed time:", time.time() - start_time
			shapelet = (ts, start_pos, slen)
			#shapelet_time = ts[0][start_pos : start_pos + slen]
			#shapelet_flux = ts[1][start_pos : start_pos + slen]
			#shapelet = (tuple(shapelet_time), tuple(shapelet_flux))
			ig = shapelet_utils.information_gain(dataset, shapelet, ts_classes,\
			   ts_class, len(class_tses[ts_class]), DATASET_ENTROPY, ts_filenames)
			print ts_class, "information gain:", ig
			#infgain[shapelet] = ig
			#class_shapelets[ts_class] = shapelet
