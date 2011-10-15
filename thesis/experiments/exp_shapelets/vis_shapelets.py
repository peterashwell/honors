import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
from lightcurve import *

FOUND_DIR = sys.argv[1]

best = {}
best_line = {}
best_SD = {}
SH_INDEX = "shapelet_ids"
sh_file = open('{0}/{1}'.format(FOUND_DIR, SH_INDEX))

for ln, line in enumerate(sh_file):
	if ln % 1000 == 0:
		print "{0}/{1}".format(ln,"total")
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
print best
print best_line
# Plot time series and best shapelet onto '<class>_shapelet.eps'
# 1) Open and read in lc from the source file
for sh_class in best_line.keys():
	lc = file_to_lc(best_line[sh_class][1])
	sh_start = int(best_line[sh_class][2])
	sh_end = int(best_line[sh_class][2]) + int(best_line[sh_class][3])
	print sh_start, sh_end
	
	ts_time = lc.time[:sh_start]
	ts_flux = lc.flux[:sh_start]
	plt.plot(lc.time[:sh_start], lc.flux[:sh_start], 'k', lc.time[sh_end:], lc.flux[sh_end:], 'k', lc.time[sh_start:sh_end], lc.flux[sh_start:sh_end], 'r')
	plt.xlabel('Time (days)')
	plt.ylabel('Flux (mJy, normalised)')
	plt.savefig("figures/" + sh_class + "_shapelet.pdf", format='pdf')
	plt.close()
