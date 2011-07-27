# This script generates lightcurves of different types of transients 
# Transients considered are: 
#    * Radio SNe 
#    * ESEs 
#    * IDVs 
#    * Novae 
# Written by Kitty Lo 
# Date: 5 Jan 2010 
# Last revised: 24 Feb 2010 

import random 
from math import * 
import sys
import os 
import numpy.random 
import numpy 
import source
import scipy.special 
import myutils  
import scipy
from scipy import integrate 

# sigma is in mJy 
def getnoise(sigma): 
  return numpy.random.normal(0,sigma) 

# Generate an ESE lightcurve based on Fiedler 1994 
def generateESE(fnum): 
   newESE = source.ESE() 

   # ESE duration range from 2months to 1.2 years 
   newESE.event_duration = random.randrange(60,300) 
   # Length of the lightcurve 
   newESE.lc_duration = 400

   theta_b = random.uniform(1.2,2.5) 
   theta_l = random.uniform(1.2,5) 
   scaling = random.randrange(5,500) 
   newESE.generate_lc(theta_b,theta_l) 
   timesteps = len(newESE.time) 
   # Write lightcurve to a file 
   startingMJD = 0 
   fname = 'ESE_' + str(fnum) + '.data' 
   f = open(fname, 'w')    

   for i in range(timesteps): 
      writetime = str(newESE.time[i]) 
      writeflux = str(newESE.flux[i]*scaling + getnoise(1)) 
      f.write(writetime + "," + writeflux + "\n") 
   
def generateFlare(fnum):
   # Length of flare
   flare_duration = random.randrange(30, 400)
   
   # Fraction of flare changing from 0
   onset_fraction = random.random() * 0.20 + 0.15
   onset_duration = int(floor(flare_duration * onset_fraction))
   
   # Compute the flux for the onset point with a logistic curve
   onset_flux = []
   for onset_point in xrange(onset_duration):
      # Shifted smoothes the logistic curve rise a bit
      shifted = onset_point * (40.0 / onset_duration) - 20
      onset_flux.append(1.0 / (1.0 + exp(-0.5 * shifted)))
   decline_flux = reversed(onset_flux)
   intensity = random.randrange(10, 1000)
   flare_intensity = random.randrange(50, 500)
   flux = []
   flux += [(onset_point * flare_intensity) + intensity for onset_point in onset_flux]
   flux += [flare_intensity + intensity for i in xrange(flare_duration - 2 * onset_duration)]
   flux += [(decline_point * flare_intensity) + intensity for decline_point in decline_flux]   
   fname = 'Flare_' + str(fnum) + '.data' 
   f = open(fname, 'w')    

   timesteps = len(flux)
   for i in range(timesteps): 
      writetime = str(i)
      writeflux = str(flux[i] + getnoise(1))	

      f.write(writetime + "," + writeflux + "\n") 

# Lightcurve adapted from VAST Memo No. 3 
# Equation is from Weiler (2002)  
def generateSupernovae(fnum): 
   newSNe = source.Supernova() 
   newSNe.lc_duration = 400 
   newSNe.generate_lc() 
   timesteps = len(newSNe.time) 
   galaxy_flux = random.randrange(5,500) 
   galaxy_flux = 0 
   noise = 1 

   # Write lightcurve to a file 
   startingMJD = 0
   fname = 'SNe_' + str(fnum) + '.data' 
   f = open(fname, 'w') 
   for i in range(0,timesteps): 
      writetime = str(startingMJD + newSNe.time[i])
      writeflux = str(newSNe.flux[i] + galaxy_flux + getnoise(noise)) 
      f.write(writetime + ',' + writeflux + '\n') 
   
# Generate a lightcurve with only gaussian noise 
def generateNoise(fnum): 
   numpoints = 400
   flux = random.randrange(1000)
   fname = 'Noise_' + str(fnum) + '.data' 
   f = open(fname, 'w') 
   for i in range(1, numpoints + 1): 
      writetime = str(i) 
      writeflux = str(getnoise(1) + flux) 
      f.write(writetime + ',' + writeflux + '\n') 

# Adapted from VAST memo 2. 
def generateIDV(fnum): 
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
   n_times = 1000
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

   fname = 'IDV_' + str(fnum) + '.data' 
   f = open(fname, 'w') 
   for i in range(n_times): 
      writetime = str(timeInDays[i]) 
      writeflux = str(flux[i])  
      f.write(writetime + ',' + writeflux + '\n') 
  
# TO DO: Check the parameters used to generate the lightcurves!     
def generateNovae(fnum): 
   h = 6.62e-34 # Planck's constant 
   k = 1.38e-23 # Boltzman's constant
   v = 14000000 # Freq in Hz 
   Te = 10000 # Temperature in K 
   M = random.randrange(10,50)*1e-5*2e30  
   c = 3e8 # Speed of light 
   d = random.randrange(50,1500)*3e16 # in metres
   v2 = random.uniform(1,10)*10**random.randrange(7,9)# metres per sec 
   v1 = v2*random.uniform(0.1,0.5) # metres per sec

   print "File number: " + str(fnum) 
   print "d: " + str(d) 
   print "v1: " + str(v1) 
   print "v2: " + str(v2) 
   
   # define the functions we will use 
   F = (1/2.33e-24)**2*exp(-h*v/(k*Te))*(M/(4*pi))**2*(5.4e-39*Te**-0.5*1.38*Te**0.16*(v/1e9)**-0.11)
   G = lambda r,a: (1/a**2)*(sqrt(r**2-a**2)/r**2 + (1/a)*acos(a/r)) 
   Bv = (2*h*v**3/c**2)/(exp(h*v/(k*Te))-1)
   tau1 = lambda r1, r2, a: (F/Bv)*(G(r2,a)-G(r1,a))/(r2-r1)**2 
   tau2 = lambda r1, r2, a: (F/Bv)*G(r2,a)/(r2-r1)**2 

   # set r1, r2
   flux = []
   for days in range(1,10000): 
      t = 60*60*24*days 
      r1 = v1*t 
      r2 = v2*t 
      Sv1 = lambda a: (2*pi*Bv/d**2)*a*(1-exp(-1*tau1(r1,r2,a)))
      Sv2 = lambda a: (2*pi*Bv/d**2)*a*(1-exp(-1*tau2(r1,r2,a)))

      S1, S1err = integrate.quad(Sv1, 0, r1) 
      S2, S2err = integrate.quad(Sv2, r1, r2) 

   flux.append((S1+S2)/10e-26) # change to Jy 

   fname = 'Novae_' + str(fnum) + '.data' 
   f = open(fname, 'w') 
   for i in range(1,10000): 
      writetime = str(i) 
      writeflux = str(flux[i-1]+getnoise(0.001))  
      f.write(writetime + ',' + writeflux + '\n') 
  
def generateLightCurve(transientType, fnum): 
   if transientType == 'SNe': 
      generateSupernovae(fnum) 
   elif transientType == 'ESE': 
      generateESE(fnum)
   elif transientType == 'IDV': 
      generateIDV(fnum) 
   elif transientType == 'Noise': 
      generateNoise(fnum)  
   elif transientType == 'Novae': 
      generateNovae(fnum) 
   elif transientType == 'Flare':
      generateFlare(fnum)
   else:
      print "Transient type not implemented yet! " 


if __name__ == "__main__":
   transientType = sys.argv[1] 
   numfiles = int(sys.argv[2])
   for i in range(1,numfiles+1): 
      generateLightCurve(transientType, i)
   
