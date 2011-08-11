import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.backends.backend_pdf import PdfPages
import os
import sys
from lightcurve import *
if len(sys.argv) < 1:
	print "<light curve directory> <desired pdf filename>"
	exit(1)
lc_dir = sys.argv[1]
lc_out = sys.argv[2]
if len(sys.argv) > 3:
	fixed = sys.argv[3]
if fixed == '-f':
	fix_axes = True

# default font is too large for subfigures
mpl.rc('font', size=8)
	
pdf = PdfPages(lc_out + '.pdf')

# space out the subfigures
fig = plt.figure()
fig.subplots_adjust(wspace=0.4, hspace = 0.5)

# rows and cols in subfigure plot
plot_rows = 4
plot_cols = 2

lc_num = 0
for lc_file in os.listdir(lc_dir):
	filename = lc_dir + "/" + lc_file
	print "reading:", filename
	lc = file_to_lc(filename)
	lc.remove_gaps()
	plt.subplot(plot_rows, plot_cols, lc_num % (plot_rows * plot_cols))
	if fix_axes:
		plt.ylim([-1, 10])
	plt.plot(lc.time, lc.flux, 'r+')
	plt.title(filename)
	
	lc_num += 1
	if lc_num % (plot_rows * plot_cols) == 0: # start new page
		# close the plot page to pdf and move onto next one
		plt.savefig(pdf, format='pdf')
		plt.close()
		fig = plt.figure()
		fig.subplots_adjust(wspace=0.4, hspace = 0.5)

if not lc_num % (plot_rows * plot_cols) == 0:
	plt.savefig(pdf, format='pdf')
	plt.close()
pdf.close()	
