#!/usr/bin/python
# This script generates lightcurves of different types of transients 
# Transients considered are: 
#    * Radio SNe 
#    * ESEs 
#    * IDVs 
#    * Novae 
#    * XRB
#    * Flare stars 
# Written by Kitty Lo 
# Date: 5 Jan 2011
# Last revised: 23 May 2011 

import random 
from math import * 
import sys, getopt 
import os 
import numpy.random 
import numpy 
import source
print sys.path
import scipy
from scipy import special
from scipy import integrate 
import myutils  

# sigma is in mJy 
def getnoise(sigma): 
  return numpy.random.normal(0,sigma) 

# Generate some xrb light curves 
def generateXRB(fnum, numpoints, footprint, rms): 
   newXRB = source.XRB() 
   newXRB.lc_duration = numpoints 
   newXRB.rms = rms 
   newXRB.flareRate = random.uniform(0.005,0.02) 
 
   newXRB.generate_lc(footprint) 
   timesteps = len(newXRB.time) 
   fname = 'XRB_' + str(fnum) + '.data' 
   f = open(fname, 'w')    

   for i in range(timesteps): 
      writetime = str(newXRB.time[i]) 
      writeflux = str(newXRB.flux[i] + getnoise(rms)) 
      f.write(writetime + "\t" + writeflux + "\n") 
   
# Generate some flare star (RSCVn) light curves 
def generatefStarRSCVn(fnum, numpoints, footprint, rms): 
   newfStar = source.fStar_RSCVn() 
   newfStar.lc_duration = numpoints 
   newfStar.rms = rms 
   newfStar.flareRate = random.uniform(0.01,0.1) 
 
   newfStar.generate_lc(footprint) 
   timesteps = len(newfStar.time) 
   fname = 'fStar_RSCVn_' + str(fnum) + '.data' 
   f = open(fname, 'w')    

   for i in range(timesteps): 
      writetime = str(newfStar.time[i]) 
      writeflux = str(newfStar.flux[i] + getnoise(rms)) 
      f.write(writetime + "\t" + writeflux + "\n") 

# Generate some flare star (dMe) light curves 
def generatefStardMe(fnum, numpoints, footprint, rms): 
   newfStar = source.fStar_dMe() 
   newfStar.lc_duration = numpoints 
   newfStar.rms = rms 
   newfStar.flareRate = random.uniform(1,20) 
 
   newfStar.generate_lc(footprint) 
   timesteps = len(newfStar.time) 
   fname = 'fStar_dMe_' + str(fnum) + '.data' 
   f = open(fname, 'w')    

   for i in range(timesteps): 
      writetime = str(newfStar.time[i]) 
      writeflux = str(newfStar.flux[i] + getnoise(rms)) 
      f.write(writetime + "\t" + writeflux + "\n") 

# Generate an ESE lightcurve based on Fiedler 1994 
def generateESE(fnum, numpoints,footprint,rms): 
   newESE = source.ESE() 
   
   # ESE duration range from 2months to 1.2 years 
   newESE.event_duration = random.randrange(60,300) 
   # Length of the lightcurve 
   newESE.lc_duration = numpoints

   theta_b = random.uniform(1.2,2.5) 
   theta_l = random.uniform(1.2,5) 
   scaling = random.randrange(5,500) 
   newESE.generate_lc(theta_b,theta_l,footprint) 
   timesteps = len(newESE.time) 
   # Write lightcurve to a file 
   startingMJD = 0 
   fname = 'ESE_' + str(fnum) + '.data' 
   f = open(fname, 'w')    

   for i in range(timesteps): 
      writetime = str(newESE.time[i]) 
      writeflux = str(newESE.flux[i]*scaling + getnoise(rms)) 
      f.write(writetime + "\t" + writeflux + "\n") 

# Lightcurve adapted from VAST Memo No. 3 
# Equation is from Weiler (2002)  
def generateSupernovae(fnum, numpoints,footprint,rms): 
   newSNe = source.Supernova() 
   newSNe.lc_duration = numpoints 
   newSNe.generate_lc(footprint) 
   timesteps = len(newSNe.time)  
   galaxy_flux = 0 

   # Write lightcurve to a file 
   startingMJD = 0
   fname = 'SNe_' + str(fnum) + '.data' 
   f = open(fname, 'w') 
   for i in range(0,timesteps): 
      writetime = str(startingMJD + newSNe.time[i])
      writeflux = str(newSNe.flux[i] + galaxy_flux + getnoise(rms)) 
      f.write(writetime + '\t' + writeflux + '\n') 
   
# Generate a lightcurve with only gaussian noise 
def generateNoise(fnum, numpoints,footprint,rms):
   timer=myutils.timestep() 
   timer.set_start_time(0) 
   timer.set_end_time(numpoints) 
   timer.set_increment(1) 
   timer.make_timeseries(footprint) 
   nsteps = timer.nsteps() 
 
   fname = 'Noise_' + str(fnum) + '.data' 
   f = open(fname, 'w') 
   for i in range(nsteps): 
      writetime = str(timer.get_time())
      writeflux = str(getnoise(rms)) 
      f.write(writetime + '\t' + writeflux + '\n') 

# Adapted from VAST memo 2. 
def generateIDV(fnum, numpoints,footprint,rms): 
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

   quiescent_flux = random.uniform(10,100)

   fname = 'IDV_' + str(fnum) + '.data' 
   f = open(fname, 'w') 
   for i in range(n_times): 
      writetime = str(timeInDays[i]) 
      writeflux = str(flux[i]*quiescent_flux)  
      f.write(writetime + '\t' + writeflux + '\n') 
  
# TO DO: Check the parameters used to generate the lightcurves!     
def generateNovae(fnum, numpoints,footprint,rms): 
   newNova = source.Nova() 
   newNova.lc_duration = numpoints 
   newNova.generate_lc(footprint) 
   timesteps = len(newNova.time)  

   # Write lightcurve to a file 
   startingMJD = 0
   fname = 'Nova_' + str(fnum) + '.data' 
   f = open(fname, 'w') 
   for i in range(0,timesteps): 
      writetime = str(startingMJD + newNova.time[i])
      writeflux = str(newNova.flux[i] + getnoise(rms)) 
      f.write(writetime + '\t' + writeflux + '\n') 
     
def generateLightCurve(transientType, fnum, numpoints=400,footprint="wide",rms=1): 
   if transientType == 'SNe': 
      generateSupernovae(fnum, numpoints,footprint,rms) 
   elif transientType == 'ESE': 
      generateESE(fnum, numpoints,footprint,rms)
   elif transientType == 'IDV': 
      generateIDV(fnum, numpoints,footprint,rms) 
   elif transientType == 'Noise': 
      generateNoise(fnum, numpoints,footprint,rms)  
   elif transientType == 'Novae': 
      generateNovae(fnum, numpoints,footprint,rms) 
   elif transientType == 'XRB': 
      generateXRB(fnum, numpoints, footprint,rms) 
   elif transientType == 'fStar_RSCVn': 
      generatefStarRSCVn(fnum, numpoints, footprint,rms) 
   elif transientType == 'fStar_dMe': 
      generatefStardMe(fnum, numpoints, footprint,rms) 
   else:
      print "Transient type not implemented yet! " 

if __name__ == "__main__":
   opts, args = getopt.getopt(sys.argv[1:], "ht:f:n:p:i:")
   for o, a in opts:
       if o == "-t":
           transientType = a 
       elif o == "-f": 
           numfiles = int(a) 
       elif o == "-n": 
           numpoints = int(a) 
       elif o == "-p": 
           footprint = a  
       elif o == "-i": 
           rms = a 
       elif o == "-h": 
           print "Usage: generateLightCurves.py" 
           print "-t Transient type - SNe, Novae, ESE, IDV, Noise, XRB, fStar_RSCVn, fStar_dMe" 
           print "-f Number of files" 
           print "-n Number of days" 
           print "-p Footprint, can be wide, deep, log, patches, monthly" 
           print "-i RMS of noise in mJy" 
           sys.exit(0)    
       else:
           print "Usage: generateLightCurves.py"
           print "-t Transient type - SNe, Novae, ESE, IDV, Noise" 
           print "-f Number of files" 
           print "-n Number of days" 
           print "-p Footprint, can be wide, deep, log, patches, monthly" 
           print "-i RMS of noise in mJy" 
           sys.exit(0)  

   for i in range(1,(numfiles)+1): 
       generateLightCurve(transientType, i, numpoints, footprint,rms)
   
