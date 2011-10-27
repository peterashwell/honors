import matplotlib.pyplot as plt
from lightcurve import *
import os
import random
CLEAN_LC_DIR = "lightcurves/norm_n0.0_a100_m0_s400"
class_files = {}
for file in os.listdir(CLEAN_LC_DIR):
	classname = file.split('_')[0]
	if classname not in class_files.keys():
		class_files[classname] = [file]
	else:
		class_files[classname].append(file)

for c in class_files.keys():
	file = random.choice(class_files[c])
	print file
	# open to lc
	lc = file_to_lc(CLEAN_LC_DIR + "/" + file)
	lc.remove_gaps()
	plt.plot(lc.time, lc.flux)
	plt.xlabel("Time (days)")
	plt.ylabel("Flux (days)")
	plt.savefig("sample_" + c + ".png",format='png')
	plt.close()
