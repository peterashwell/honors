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
	lcfile = open('{0}/{1}'.format(dir, fname))
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
	plt.ylabel('Sample probability')
	plt.title('Flux distribution')
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
	textstr = '$\mathrm{skew}=%.2f$\n$\mathrm{kurtosis}=%.2f$\n$\mathrm{beyond1std}=%.2f$'%(skewness, kurtosis_val, beyond1std)

	# these are matplotlib.patch.Patch properies
	props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

	# place a text box in upper left in axes coords
	halign = 'left'
	hpos = 0.05
	if c == 'SNe':
		halign = 'right'
		hpos = 0.95
	ax.text(hpos, 0.95, textstr, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', horizontalalignment=halign , bbox=props)
out_fname = 'sample_hist.eps'.format(c)
plt.savefig(out_fname, format='eps')
plt.close()
