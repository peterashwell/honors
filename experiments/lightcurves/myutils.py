# This script contains a set of general util functions  
# Written by Kitty Lo 
# On: 20th Jan, 2011

import os 
import sys
import string
import time
from scipy.special import * 
import numpy as np 
import random 

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
   if x >= 20: 
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
        self.now = -1
        self.dt = 1 
        self.timeseries = [] 

    def set_start_time(self, st): 
        self.start_time = st 

    def set_end_time(self, et): 
        self.end_time = et 

    def set_increment(self, inc): 
        self.dt = inc 

    def nsteps(self): 
        return len(self.timeseries) 

    def set_curtime(self, curtime): 
        self.now = curtime 

    def get_time(self): 
        if self.now < 0:
            print "Need to run make_timeseries()"  
            return -1 
        if self.now >= len(self.timeseries): 
            return -1 

        cur_time = self.now 
        self.now = self.now + 1 
        return self.timeseries[cur_time] 

    def make_timeseries(self, footprint): 
        # Clear the current timeseries 
        self.timeseries = [] 
        # First make an array with the required length 
        for i in range(self.start_time, self.end_time): 
           self.timeseries.append(i) 
           
        # Then, based on the footprint, delete selected points 
        if footprint == "wide": 
            pass
        elif footprint == "deep":
            new_timeseries = []  
            for i in [1,2,3,4,17,21]:
                new_timeseries.append(self.timeseries[i-1]) 
            self.timeseries = new_timeseries 
        elif footprint == "log": 
            new_timeseries = [] 
            numpoints = len(self.timeseries) 
            j = 0
            while(numpoints > 128): 
                for i in [1,2,4,8,16,32,64]: 
                    new_timeseries.append(self.timeseries[128*j+i-1]) 
                numpoints = numpoints - 128 
                j = j + 1
            self.timeseries = new_timeseries 
        elif footprint == "patches": 
            new_timeseries = [] 
            numpoints = len(self.timeseries) 
            j = 0 
            while(numpoints > 30): 
                 #Pick a random starting day 
                 startdate = random.randrange(0,27)
                 new_timeseries.append(self.timeseries[j*30+startdate]) 
                 new_timeseries.append(self.timeseries[j*30+startdate+1]) 
                 new_timeseries.append(self.timeseries[j*30+startdate+2]) 
                 numpoints = numpoints - 30 
                 j = j + 1 
            self.timeseries = new_timeseries 
        elif footprint == "monthly": 
            new_timeseries = [] 
            numpoints = len(self.timeseries) 
            j = 0 
            while(numpoints > 30): 
               new_timeseries.append(self.timeseries[j*30]) 
               numpoints = numpoints - 30 
               j = j + 1
            self.timeseries = new_timeseries 
        else: 
            print "Footprint selected has not been implemented" 

        self.now = 0 


























