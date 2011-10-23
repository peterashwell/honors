import sys
import os
from operator import itemgetter
import matplotlib as mpl
import matplotlib.pyplot as plt
from lightcurve import *

FOUND_DIR = sys.argv[1]

best = {}
best_line = {}
best_SD = {}
SH_INDEX = "shapelet_ids"
shapelet_train_dir = 'lightcurves/norm_n0.0_a100_m0_s400'
NUM_CROSSFOLDS = 10
for cfnum in xrange(NUM_CROSSFOLDS):
	sh_file = open('{0}/cf{1}/{2}'.format(FOUND_DIR, cfnum, SH_INDEX))
	print "reading", sh_file
	records = []
	for ln, line in enumerate(sh_file):
		if ln % 1000 == 0:
			print "{0}/{1}".format(ln,"total")
		line = line.strip().split(',')
		line[4] = float(line[4])
		line[5] = float(line[5])
		records.append(line)	
		#sh_class = line[1].split('/')[-1].split('_')[0]
		#print sh_class
		#update = False
		#if sh_class not in best.keys():
		#	update = True
		#elif line[-2] < best[sh_class]:
		#	update = True
		#elif best[sh_class] == line[-2]:
		#	if line[-1] > best_SD[sh_class]:
		#		update = True	
			#elif line[-2] == best[sh_class]:
			#	if line[-1] > best_SD[sh_class]:
			#		update = True
		#if update:
		#	best_line[sh_class] = line
		#	best[sh_class] = line[-2]
		#	best_SD[sh_class] = line[-1]
	records.sort(key=itemgetter(4))
	print records[:40]
	print best
	print best_line
	# Plot time series and best shapelet onto '<class>_shapelet.eps'
	# 1) Open and read in lc from the source file
	for sh_class in best_line.keys():
		path = shapelet_train_dir + '/' + best_line[sh_class][1].split('/')[-1]
		lc = file_to_lc(path)
		sh_start = int(best_line[sh_class][2])
		sh_end = int(best_line[sh_class][2]) + int(best_line[sh_class][3])
		print sh_start, sh_end
		
		ts_time = lc.time[:sh_start]
		ts_flux = lc.flux[:sh_start]
		plt.plot(lc.time[:sh_start], lc.flux[:sh_start], 'k', lc.time[sh_end:], lc.flux[sh_end:], 'k', lc.time[sh_start:sh_end], lc.flux[sh_start:sh_end], 'r')
		plt.xlabel('Time (days)')
		plt.ylabel('Flux (mJy, normalised)')
		if not os.path.isdir('figures/cf{0}'.format(cfnum)):
			os.mkdir('figures/cf{0}'.format(cfnum))
		plt.savefig('figures/cf{0}/'.format(cfnum) + sh_class + "_shapelet.pdf", format='pdf')
		plt.close()
