import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.backends.backend_pdf import PdfPages
import os

# default font is too large for subfigures
mpl.rc('font', size=8)
	
pdf = PdfPages('lc.pdf')

# space out the subfigures
fig = plt.figure()
fig.subplots_adjust(wspace=0.4, hspace = 0.5)

# rows and cols in subfigure plot
plot_rows = 4
plot_cols = 2

lc_num = 0
for lc_file in os.listdir("lightcurves"):
	filename = "lightcurves/" + lc_file
	print "reading:", filename
	lc_data = open(filename)
	
	time = []
	flux = []
	for line in lc_data:
		line = line.strip().split(',')
		time.append(float(line[0]))
		flux.append(float(line[1]))
	
	plt.subplot(plot_rows, plot_cols, lc_num % (plot_rows * plot_cols))
	plt.plot(time, flux, 'r')
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
