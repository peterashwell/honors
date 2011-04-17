# This script generates lightcurves of different types of transients 
# Transients considered are: 
#	 * Radio SNe 
#	 * ESEs 
#	 * IDVs 
# Written by Kitty Lo 
# Date: 5 Jan 2010 
# Last revised: 13 Feb 2010 
# Modified by Peter Ashwell 15 Mar 2011 to make LC functions reusable in my code
#	 * Removed all file writing and set return types

import random 
from math import * 
import sys
import os 
import numpy 
import numpy.random
import source
import scipy.special 
import myutils  
import scipy

# sigma is in mJy 
def getnoise(sigma): 
	return numpy.random.normal(0, sigma) 

def generateNT(total_time, mean, sigma, timestep=1): # TODO add timestep
	return (range(total_time), [mean + getnoise(sigma) for e in xrange(total_time)])

# Produce a sudden peak
def generateFlare(background=1e-5, timestep=1.0):
	event_duration = random.randrange(30, 200)
	num_points = int(floor(event_duration / timestep))
	time = range(num_points)
	flare_intensity = background * random.randrange(50, 1000) # TODO flare is 50 to 1000 hotter than bg
	flux = generateNT(num_points, flare_intensity, background / 3.0)
	return time, flux

# Generate an ESE lightcurve based on Fiedler 1994 
def generateESE(timestep=1.0, startingMJD=0):
	newESE = source.ESE() 

	theta_b = random.uniform(1.2,2.5) 
	theta_l = random.uniform(1.2,5) 
	
	newESE.generate_lc(timestep, theta_b,theta_l) 
	timesteps = len(newESE.time) 
	# Write lightcurve to a file 
	sigma = 0.3 # TODO what noise level should this have?
	for i in xrange(timesteps):
		newESE.time[i] += startingMJD
		newESE.flux[i] += getnoise(sigma) 
	return (newESE.time, newESE.flux)

# Lightcurve adapted from VAST Memo No. 3 
# Equation is from Weiler (2002)  
def generateSupernovae(timestep=1.0, startingMJD=0): 
	newSNe = source.Supernova() 
	newSNe.generate_lc(timestep)
	
	timesteps = len(newSNe.time) 
	galaxy_flux = random.randrange(5,500) # TODO normalise flux with this 
	noise = 1 

	# return light curve object, modified with additional parameters
	for i in xrange(timesteps):
		newSNe.time[i] += startingMJD
		newSNe.flux[i] += getnoise(noise) + galaxy_flux # TODO what is this
	return (newSNe.time, newSNe.flux)
	 
# Adapted from VAST memo 2. 
def generateIDV(total_time=500, timestep=1.0, startingMJD=0):
	n_times = int(floor(total_time / timestep))
	# Randomly sampled variables 
	viss = random.uniform(3,5)*1e4 # velocity of ISS [m/s] 
	sm = 10**random.uniform(-5,-2)*3.09e19 # integrated scattering index [m^-17/3]
	z = random.uniform(100,1000)*3.09e16 # distance of scattering screen from Earth [m] 

	# Fixed variables 
	s0 = 6.4e7 # [m] 
	lmbda = 0.21 # wavelength [m] 
	r_e = 2.82e-15 # radius of an electron [m] 
	theta0 = 0.001/3600*pi/180
	k = 2*pi/lmbda # wavenumber [1/m]  
	scale = 2.0*(pi**2)*(r_e**2)*(lmbda**2)*sm*scipy.special.gamma(7./6)*(z**2)/((2*pi/lmbda)**2)/((z**2*theta0**2)**(7./6)) 
	x = scipy.linspace(0,10,n_times)
	timeInDays = (x*2*z*theta0/viss)/(24*3600)	
 
	y = scipy.linspace(0,0,n_times)  
	for i in range(n_times):
		y[i] = myutils.laguerre_7on6(float(pow(x[i],2)))
	y2 = scipy.linspace(0,0,n_times*2-1)
	y2[0:n_times-1] = y[0:n_times-1]  
	temp = y[::-1] 
	for i in range(n_times-1): 
		y2[i+n_times] = temp[i] 
	 
	cphases = scipy.zeros(n_times,complex) 
	for i in range(n_times):
		phases = random.uniform(0,1)*2*pi  
		cphases[i] = complex(cos(phases), sin(phases)) 
	fy = scipy.fft(y2)
	abs_fy = numpy.sqrt(numpy.abs(fy))
	
	new_y = scipy.zeros(n_times*2-1, complex) 
	for i in range(n_times): 
		new_y[i] = abs_fy[i]*cphases[i]  
	temp = scipy.conj(cphases)[::-1] 
	for i in range(n_times-1): 
		new_y[i+n_times] = abs_fy[i+n_times]*temp[i] 
	new_y[0] = 0 

	flux = 1.0 + scale*(scipy.real(scipy.ifft(new_y)))
	return (timeInDays, flux)
