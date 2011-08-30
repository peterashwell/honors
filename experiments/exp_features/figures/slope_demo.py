import lomb
import features
from lightcurve import LightCurve
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
files = ['IDV_wide_100.data', 'ESE_wide_100.data']#, 'BG_wide_100.data']
gs = gridspec.GridSpec(1, 2, height_ratios=[1,1])	
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
	
	print "pltnum=", pltnum
	ax = plt.subplot(gs[pltnum])
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
	#ax = fig.add_subplot(gs[pltnum + 2])
	#plt.xlabel('Wavelength (days)')
	#plt.ylabel('Relative intensity')
	#plt.title('{0} Periodogram'.format(c))

	time = numpy.array(time)
	flux = numpy.array(flux)
	# center the flux
	flux = (flux - numpy.mean(flux)) / (1.0 * numpy.std(flux))
	
	best_increase = 0
	best_decrease = 0
	
	final_fp_dec = None
	final_fp_inc = None
	final_sp_dec = None
	final_sp_inc = None
	for fp in xrange(len(flux) - 1):
		for sp in xrange(fp + 1, len(flux)):
			slope = (flux[sp] - flux[fp]) / (time[sp] - time[fp])
			if slope < best_decrease:
				best_decrease = slope
				final_sp_dec = sp
				final_fp_dec = fp
			if slope > best_increase:
				best_increase = slope
				final_sp_inc = sp
				final_fp_inc = fp
	
	lc = LightCurve(time, flux)
	spt = features.slope_pair_trends(lc)
	print "inc"
	print final_sp_inc
	print final_fp_inc
	print "dec"
	print final_sp_dec
	print final_fp_dec
	ax.plot([time[final_sp_inc], time[final_fp_inc]], [flux[final_sp_inc], flux[final_fp_inc]], 'g-x')
	ax.plot([time[final_sp_dec], time[final_fp_dec]], [flux[final_sp_dec], flux[final_fp_dec]], 'b-x')

	textstr = ""
	textstr += '$\mathrm{best\\_increase}=%.2f$\n$\mathrm{best\\_decrease}=%.2f$\n' % (best_increase, best_decrease)
	textstr += '$\mathrm{slope\\_pair\\_trends}=%.2f$' % (spt[0])
	# these are matplotlib.patch.Patch properies
	#textstr += '$\mathrm{flux\\_%s\\_%s}=%.2f$\n' % (str(start), str(end), feature)
	props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

	# place a text box in upper left in axes coords
	halign = 'left'
	hpos = 0.05
	if c == 'ESE':
		halign = 'right'
		hpos = 0.95
	ax.text(hpos, 0.95, textstr, transform=ax.transAxes, fontsize=8,
        verticalalignment='top', horizontalalignment=halign , bbox=props)
out_fname = 'slope_demo.eps'.format(c)
plt.savefig(out_fname, format='eps')
plt.close()
