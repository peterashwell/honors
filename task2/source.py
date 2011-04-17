# Source class and related functions for VAST simulation
# Written by Tara Murphy 
# Modified by Kitty Lo 
# On 18 Jan 2010 

from math import *
import myutils 
import random 

class ESEs():
	def __init__(self):
		self.rate = 0.017  # sources in a year
		
class ESE():
	def __init__(self):
		self.type = 'ese'
		self.theta_s = 1
		self.time = []
		self.angle = []
		self.flux = []

	def caustic(self, d, theta_b, theta_l):
		theta_l *= self.theta_s
		theta_b *= theta_l
		c = sqrt(8 * log(2))
		theta_scat = sqrt(1 + theta_b**2)

		A = c*(d - theta_l/2.0) / theta_scat / sqrt(2)
		B = c*(d + theta_l/2.0) / theta_scat / sqrt(2)
		C = c*(theta_l/2.0 - d) / sqrt(2)
		D = c*(-theta_l/2.0 - d) / sqrt(2)

		fn = (myutils.erf(B) - myutils.erf(A) - myutils.erf(C) + myutils.erf(D) + 2)/2.0
#		fn = (erf(B) - erf(A))/(2.0*sqrt(2))
#		fn = (1 - erf(C))/(2.0*sqrt(2))
#		fn = (1 + erf(D))/(2.0*sqrt(2))

		return fn

	def generate_lc(self, timestep=1.0, theta_b=1.4, theta_l=5): # TODO confirm timestep in seconds
		self.event_duration = int(floor(random.randrange(50, 350) / timestep)) 
		#nsteps = 518400   # 2 * 30 * 24 * 60 * 60 / 10 (10 seconds)
		timer = myutils.timestep() 
		timer.set_start_time(0) 
		timer.set_end_time(self.event_duration) 
		timer.set_increment(timestep) 
		nsteps = int(floor(timer.nsteps())) 
		xmin = -10 
		xmax = 10 

		dx = (xmax - xmin)/float(nsteps)
		d = xmin

		tmin = 0
		tmax = self.event_duration  
		
		#dt = (tmax - tmin)/float(nsteps)
		t = timer.get_time() 

		for ij in range(nsteps):
			amp = self.caustic(d, theta_b, theta_l)
			self.angle.append(d)
			self.time.append(t)
			self.flux.append(amp)
			d += dx
			t = timer.get_time() 

		# Fill the rest of the lightcurve with noise 
		timer.set_end_time(self.event_duration) 
		
		t = timer.get_time() 
		while(t > 0): 
			self.time.append(t) 
			self.flux.append(1) 
			t = timer.get_time() 

class Supernova(): 
	def __init__(self):
		self.type = 'sne'
		self.time = []
		self.flux = []
		# Lightcurve parameters 
		# Frequency nu 
		self.nu = 1.34 
		# standard deviation of the map in mJy 
		self.std = 0.1 
		# unabsorbed flux density 
		self.k1 = random.uniform(0,10) * 10 ** (random.randrange(2,5)) 
		# Spectral index alpha 
		self.alpha = random.uniform(-1.4, -0.6) 
		# Evolution index beta
		self.beta = random.uniform(-2,-0.7) 
		# Uniform optical depth K_2 
		self.k2 = random.uniform(0,10) * 10 ** (random.randrange(1,7)) 
		# Non-uniform optical depth K_3
		self.k3 = 0 
		# Thermal optical depth K_4 
		self.k4 = 0 
		self.delta = self.alpha - self.beta - 3
		self.delta2 = 5*self.delta/3.0 

	def fy(self,t): 
		# t is log10 of the time in days since explosion 
		#   tmt0 = 10 ** t 
		tmt0 = t # change t so it's just in days, not log(days) 
		# tau = CSM homogenous 
		tau = self.k2 * ((self.nu/5.0)**(-2.1)) * pow(tmt0,self.delta)
		# tau2 = distant 
		tau2 = self.k3 * ((self.nu/5.0)**(-2.1)) * pow(tmt0,self.delta2) 
		# tau3 = CSM clumps 
		tau3 = self.k4 * ((self.nu/5.0)**(-2.1)) 
		flux  = self.k2 *((self.nu/5.0)**self.alpha) * pow(tmt0,self.beta) * (exp(-1.0*(tau+tau3)))
		return flux

	def generate_lc(self, timestep=1.0): # TODO timestep in seconds 
		self.event_duration = int(floor(random.randrange(100, 350) / timestep)) # TODO confirm this
		timer = myutils.timestep() 
		timer.set_start_time(0) 
		timer.set_end_time(self.event_duration) 
		timer.set_increment(timestep) 
		nsteps = int(floor(timer.nsteps()))	 
		t = timer.get_time() 

		for i in range(nsteps+1):
			self.time.append(t)
			if t == 0:
				self.flux.append(0)
			else: 
				self.flux.append(self.fy(t))
			t = timer.get_time()  
