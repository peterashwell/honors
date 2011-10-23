from lightcurve import file_to_lc
import random
import sys
import os
import matplotlib.pyplot as plt
import distances
distance_function = distances.mindist

NUM_CROSSFOLDS = 10

SHAPELET_DIR = sys.argv[1]
TEST_DIR = sys.argv[2]
LC_DIR = 'lightcurves'

SHAPELET_SOURCE_DIR = 'lightcurves/norm_n0.0_a100_m0_s400'
DIST_VIS_DIR = 'md_visualisations/{0}'.format(TEST_DIR)
SH_INDEX = 'shapelet_ids'


from matplotlib.font_manager import fontManager, FontProperties
font= FontProperties(size='x-small');


print "TRAIN:", SHAPELET_DIR, "APPLY:", TEST_DIR
if not os.path.isdir(DIST_VIS_DIR):
	os.mkdir(DIST_VIS_DIR)

cf_tex = open('md_visualisations/template.tex').read()
for cfnum in xrange(1):
	print "cf:", cfnum
	cf_tex += '\section{crossfold %d}\n' % (cfnum)
	sh_file = open('{0}/cf{1}/{2}'.format(SHAPELET_DIR, cfnum, SH_INDEX))
	# first find the best shapelets
	best = {}
	best_line = {}
	best_SD = {}
	# TODO make this use a directory instead
	for ln, line in enumerate(sh_file):
		if ln % 1000 == 0:
			pass
			#print "{0}/{1}".format(ln,"total")
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
	# Plot time series and best shapelet onto '<class>_shapelet.eps'
	# 1) Open and read in lc from the source file
	
	testing_dir = LC_DIR + '/' + TEST_DIR
	# sample 3 for each file type
	class_tests = {}
	for fname in os.listdir(testing_dir):
		fclass = fname.split('_')[0]
		if fclass not in class_tests.keys():
			class_tests[fclass] = [fname]
		else:
			class_tests[fclass].append(fname)
	
	for classname in class_tests.keys():
		for fname in random.sample(class_tests[classname], 3):
			test_lc = file_to_lc(LC_DIR + '/' + TEST_DIR + '/' + fname)
			test_time = test_lc.time
			test_flux = test_lc.flux
			test_class = fname.split('/')[-1].split('_')[0]
			new_time, new_flux = ([], [])
			for i in xrange(len(test_flux)):
				if test_flux[i] != '-':
					new_time.append(test_time[i])
					new_flux.append(test_flux[i])
			plt.plot(new_time, new_flux, 'xk')
			colors = ['r', 'b', 'g', 'c', 'm', 'y']
			styles = ['-', '-.']
			print "test class:", test_class
			legtext = 'Original TS (class {0})'.format(test_class)
			legends = [legtext]
			for sh_num, sh_class in enumerate(best_line.keys()):
				# Find the distance function to random lightcurve in test dir and plot
				path = SHAPELET_SOURCE_DIR + '/' + best_line[sh_class][1].split('/')[-1]
				lc = file_to_lc(path)
				sh_start = int(best_line[sh_class][2])
				sh_end = int(best_line[sh_class][2]) + int(best_line[sh_class][3])
				#print sh_start, sh_end
				print "loading shapelet from:", path
				sh_time = lc.time[sh_start:sh_end]
				sh_flux = lc.flux[sh_start:sh_end]
				print "finding minimum distance for",sh_class,"shapelet to",test_class,"time series"
				md, pos = distance_function(test_flux, sh_flux)
				print "pos:", pos
				color = colors[sh_num % len(colors)]
				if sh_num >= len(colors):
					style = styles[1]
				else:
					style = styles[0]
	
				colsty = color + style
			
				plt.plot(test_time[pos:pos + int(best_line[sh_class][3])], sh_flux, colsty)
				legends.append('{0} shapelet - MD {1}'.format(sh_class, md))
				
			plot_fname = '{0}/{2}.pdf'.format(DIST_VIS_DIR, cfnum, fname.replace('.',','))
			plt.legend(legends, loc='best', prop=font)
			plt.savefig(plot_fname, format='pdf')
			cf_tex += '\\begin{figure} \\includegraphics[width=\\textwidth] \
				{%s.pdf} \\end{figure}\n' % (fname.replace('.', ','))
			plt.close()		
			plt.xlabel('Time (days)')
			plt.ylabel('Flux (mJy, normalised)')
			cf_tex += '\clearpage\n'
cf_tex += '\end{document}'
out_cf_tex = open('md_visualisations/{0}/shapelets.tex'.format(TEST_DIR), 'w')
out_cf_tex.write(cf_tex)
out_cf_tex.close()
