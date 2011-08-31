import lomb
from operator import itemgetter
import matplotlib.pyplot as plt
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
files = ['Novae_wide_100.data', 'ESE_wide_100.data']#, 'BG_wide_100.data']
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
	plt.xlabel('Wavelength (days)')
	plt.ylabel('Relative intensity')
	plt.title('{0} Periodogram'.format(c))

	time = numpy.array(time)
	flux = numpy.array(flux)
	# center the flux
	flux = (flux - numpy.mean(flux)) / (1.0 * numpy.std(flux))
	result = lomb.fasper(time, flux, 6.0, 0.5)
	FIND_FREQUENCIES = int(result[2])
	print FIND_FREQUENCIES
	# filter out weird frequencies
	spectral_results = filter(lambda elem: elem[0] < 0.55 and elem[0] > (2.0 / len(time)), zip(result[0], result[1]))
	wavelengths = []
	for frequency in sorted(spectral_results, key=itemgetter(1), reverse=True):
		wavelength = int(round(1.0 / frequency[0]))
		# check if wavelength is approximately in array
		include = True
		#for found_wavelength in wavelengths:
		#	if abs(found_wavelength[0] - wavelength) <= 4:
		#		include = False
		#if include:
		if wavelength > 20:
			wavelengths.append([wavelength, frequency[1]])
		#if len(wavelengths) == FIND_FREQUENCIES:
		#	break
	#if len(wavelengths) < FIND_FREQUENCIES:
	#		wavelengths += [0] * (FIND_FREQUENCIES - len(wavelengths))
	#if len(wavelengths) < FIND_FREQUENCIES:
	#	wavelengths += [0] * (FIND_FREQUENCES - len(wavelengths))
	# taken from http://matplotlib.sourceforge.net/users/recipes.html (placing text boxes)
	
	x = [w[0] for w in wavelengths]
	y = [w[1] for w in wavelengths]
	ax.plot(x, y, 'x')

	# these are matplotlib.patch.Patch properies
	#textstr += '$\mathrm{flux\\_%s\\_%s}=%.2f$\n' % (str(start), str(end), feature)
	textstr = ""
	props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

	# place a text box in upper left in axes coords
	halign = 'right'
	hpos = 0.95
	ax.text(hpos, 0.95, textstr, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', horizontalalignment=halign , bbox=props)
out_fname = 'lomb_demo.eps'.format(c)
plt.savefig(out_fname, format='eps')
plt.close()
