import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import *
#import maplotlib.mlab as mlab
from scipy import *
import math
import numpy
import matplotlib as mpl
mpl.rc('font', size=8)

dir = 'norm_n0.0_a100_m0_s400'
files = ['IDV_wide_100.data', 'SNe_wide_100.data']#, 'BG_wide_100.data']
gs = gridspec.GridSpec(2, 2)	
fig = plt.figure()
fig.subplots_adjust(hspace=0.4, wspace=0.4)

for pltnum, fname in enumerate(files):	
	lcfile = open('../lightcurves/{0}/{1}'.format(dir, fname))
	time = []
	flux = []
	for line in lcfile:
		line = line.strip().split('\t')
		time.append(float(line[0]))
		flux.append(float(line[1]))
	
	ax = fig.add_subplot(gs[pltnum])
	ax.plot(time, flux, 'r+')
	ticks = [min(time)]
	steps = 3
	stepsize = (max(time) - min(time)) / (steps * 1.0)
	for i in xrange(steps):
		ticks.append(ticks[0] + (i + 1) * stepsize)
	print ticks
	#ax.xaxis.set_ticks(ticks)
	#ax.yaxis.set_ticks([])
	plt.xlabel('Time (days)')
	plt.ylabel('Flux (mJy)')
	c = fname.split('_')[0]
	plt.title('{0} lightcurve'.format(c))
	ax = fig.add_subplot(gs[pltnum + 2])
	plt.xlabel('Flux (mJy)')
	plt.ylabel('{0} Sample count'.format(c))
	plt.title('{0} Flux distribution'.format(c))
	plt.xlim([-1.5, 3.5])
	n, bins, patches = ax.hist(flux, 50, normed=1, \
		facecolor='green', alpha=0.75)
	skewness = skew(flux)
	kurtosis_val = kurtosis(flux)
	stddev = numpy.std(flux)
	count = 0
	for elem in flux:
		if math.fabs(elem) > stddev:
			count += 1
	beyond1std = 1.0 * count / len(flux)
	# add text box with mean, stddev, kurtosis, skew
	# taken from http://matplotlib.sourceforge.net/users/recipes.html (placing text boxes)

	# these are matplotlib.patch.Patch properies
	
	# insert the fucken features
	features = []
	
	stddev = numpy.std(flux)
	mean = numpy.mean(flux)
	
	# center the flux
	for index in range(len(flux)):
		flux[index] = (flux[index] - mean) / stddev
	
	flux_sorted = sorted(flux)
	
	# For each flux percentile in range 20 ... 80
	textstr = ""
	points = []
	for flux_range in [10, 17.5, 25, 32.5, 40]:
		flux_range_pos = int(round((flux_range / 100.0) * len(flux_sorted))) 
		points.append(flux_sorted[-flux_range_pos])
		points.append(flux_sorted[flux_range_pos])
		feature = (flux_sorted[-flux_range_pos] - flux_sorted[flux_range_pos]) * 1.0
		start = flux_range
		end = 100 - flux_range
		textstr += '$\mathrm{flux\\_%s\\_%s}=%.2f$\n' % (str(start), str(end), feature)
	textstr = textstr.rstrip()
	colors = ['b', 'r', 'm', 'c']
	styles = ['solid', 'dashed', 'dashdot', 'dotted']
	for i, c in enumerate(zip(colors, styles)):
		plt.axvline(x=points[2 * i], color=c[0], linestyle=c[1])
		plt.axvline(x=points[2 * i + 1], color=c[0], linestyle=c[1])
	props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

	# place a text box in upper left in axes coords
	halign = 'right'
	hpos = 0.95
	ax.text(hpos, 0.95, textstr, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', horizontalalignment=halign , bbox=props)
out_fname = 'fluxperc_demo.eps'.format(c)
plt.savefig(out_fname, format='eps')
plt.close()
