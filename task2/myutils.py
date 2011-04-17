# This script contains a set of general util functions  
# Written by Kitty Lo 
# On: 20th Jan, 2011

import os 
import sys
import string
import time
from scipy.special import * 
import numpy as np 

def write2file(data, fname): 
	f = open(fname, 'w') 
	for thing in data: 
		 f.write(str(thing) + '\n')

# Find the R^2 error between the data and the non-linear curve fit
# data and fit are arrays 
# R2 = 1 means it is a perfect fit 
# R2 = 0 means the fit is no better than taking the average 
def findR2(data, fit): 
 
	if (len(data) <> len(fit)): 
		print "Error! Size of data array and fit array not equal!" 
		return 
  
	average = sum(data)/len(data) 
	sumofsquares = 0.0
	sumofavg = 0.0 

	for i in range(len(data)): 
		sumofsquares = sumofsquares + (fit[i]-data[i])**2 
		sumofavg = sumofavg + (average-data[i])**2

	return 1.0-(sumofsquares/sumofavg) 
		
# Evaluate the Laguerre polynomial L(-7/6)(x) 
# Uses a series expansion if x <= 10 
# Otherwise, uses an aymptotic formula 
def laguerre_7on6(x): 
	if x >= 15: 
		return (np.power(x,-7./6)+(49./36)*np.power(x,-13./6)+(8281./2592)*np.power(x,-19./6))/gamma(-1./6) 
	series = 0.0
	for m in range(100):
		series += (np.power(-1,m)*np.power(x,m)*float(gamma(7./6+m)))/(gamma(7./6)*(np.power(float(gamma(1+m)),2)))
	return series 

def erf(x):
	 # From http://www.johndcook.com/blog/2009/01/19/stand-alone-error-function-erf/
	 # constants
	 a1 =  0.254829592
	 a2 = -0.284496736
	 a3 =  1.421413741
	 a4 = -1.453152027
	 a5 =  1.061405429
	 p  =  0.3275911

	 # Save the sign of x
	 sign = 1
	 if x < 0:
		  sign = -1
	 x = abs(x)

	 # A & S 7.1.26
	 t = 1.0/(1.0 + p*x)
	 y = 1.0 - (((((a5*t + a4)*t) + a3)*t + a2)*t + a1)*t*exp(-x*x)

	 return sign*y

class timestep(): 
	 
	 def __init__(self): 
		  self.start_time = 0 
		  self.end_time = 365
		  self.now = self.start_time 
		  self.dt = 1 
	 
	 def set_start_time(self, st): 
		  self.start_time = st 

	 def set_end_time(self, et): 
		  self.end_time = et 

	 def set_increment(self, inc): 
		  self.dt = inc 

	 def nsteps(self): 
		  return (self.end_time-self.start_time)/float(self.dt)

	 def get_time(self): 
		  cur_time = self.now 
		  self.now = self.now + self.dt 
		  if cur_time <= self.end_time: 
				return cur_time
		  else: 
				return -1 
				print "Error! Exceeded set maximum time interval" 
