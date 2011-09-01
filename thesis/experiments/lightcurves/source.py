# Source class and related functions for VAST simulation
# Modified by Kitty Lo 
# On 18 Jan 2010 

from math import *
import myutils 
import random 
import numpy as np 
from scipy import integrate 

class ESE():
    def __init__(self):
        self.type = 'ese'
        self.theta_s = 1
        self.time = []
        self.angle = []
        self.flux = []
	self.event_duration = 60 # duration of the event in days 
        self.lc_duration = 365

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
#        fn = (erf(B) - erf(A))/(2.0*sqrt(2))
#        fn = (1 - erf(C))/(2.0*sqrt(2))
#        fn = (1 + erf(D))/(2.0*sqrt(2))

        return fn

    def generate_lc(self, theta_b=1.4, theta_l=5, footprint="wide"):
        #nsteps = 518400   # 2 * 30 * 24 * 60 * 60 / 10 (10 seconds)
        timer = myutils.timestep() 
        timer.set_start_time(0) 
        timer.set_end_time(self.event_duration) 
        timer.set_increment(1) 
        timer.make_timeseries(footprint) 
        nsteps = int(floor(timer.nsteps())) 
        xmin = -10 
        xmax = 10 

        dx = (xmax - xmin)/float(nsteps)
        d = xmin

        tmin = 0
        tmax = self.event_duration  
        #dt = (tmax - tmin)/float(nsteps)

        for i in range(nsteps):
            t = timer.get_time() 
            amp = self.caustic(d, theta_b, theta_l)
            self.angle.append(d)
            self.time.append(t)
            self.flux.append(amp)
            d += dx

        # Fill the rest of the lightcurve with noise 
        timer.set_end_time(self.lc_duration) 
        timer.make_timeseries(footprint)  

        # Go to the last recorded time array position 
        timer.set_curtime(nsteps)       
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
        self.lc_duration = 365
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

    def generate_lc(self, footprint): 
        timer = myutils.timestep() 
        timer.set_start_time(0) 
        timer.set_end_time(self.lc_duration) 
        timer.set_increment(1) 
        timer.make_timeseries(footprint) 
        nsteps = int(floor(timer.nsteps()))  

        for i in range(nsteps):
            t = timer.get_time() 
            self.time.append(t)
            if t == 0: 
                self.flux.append(0)
            else: 
                self.flux.append(self.fy(t))

class Nova(): 
    def __init__(self):
        self.type = 'nova'
        self.time = []
        self.flux = []
        self.lc_duration = 365

    def generate_lc(self, footprint): 
        # Constants 
        h = 6.62e-34 # Planck's constant 
        k = 1.38e-23 # Boltzman's constant
        v = 14000000 # Freq in Hz 
        Te = 10000 # Temperature in K 
        M = random.randrange(10,50)*1e-5*2e30
        c = 3e8 # Speed of light 
        d = random.randrange(50,1500)*3e16 # in metres
        v2 = random.uniform(1,10)*10**random.randrange(7,9)# metres per sec 
        v1 = v2*random.uniform(0.1,0.5) # metres per sec

        # define the functions we will use 
        F = (1/2.33e-24)**2*exp(-h*v/(k*Te))*(M/(4*pi))**2*(5.4e-39*Te**-0.5*1.38*Te**0.16*(v/1e9)**-0.11)
        G = lambda r,a: (1/a**2)*(sqrt(r**2-a**2)/r**2 + (1/a)*acos(a/r))
        Bv = (2*h*v**3/c**2)/(exp(h*v/(k*Te))-1)
        tau1 = lambda r1, r2, a: (F/Bv)*(G(r2,a)-G(r1,a))/(r2-r1)**2
        tau2 = lambda r1, r2, a: (F/Bv)*G(r2,a)/(r2-r1)**2

        timer = myutils.timestep() 
        timer.set_start_time(0) 
        timer.set_end_time(self.lc_duration) 
        timer.set_increment(1) 
        timer.make_timeseries(footprint) 
        nsteps = int(floor(timer.nsteps()))  

        for i in range(nsteps):
            t = timer.get_time() 
            self.time.append(t)
            if t == 0: 
                self.flux.append(0)
            else: 
                tsecs = 60*60*24*t 
                r1 = v1*tsecs
                r2 = v2*tsecs
                Sv1 = lambda a: (2*pi*Bv/d**2)*a*(1-exp(-1*tau1(r1,r2,a)))
                Sv2 = lambda a: (2*pi*Bv/d**2)*a*(1-exp(-1*tau2(r1,r2,a)))
                S1, S1err = integrate.quad(Sv1, 0, r1)
                S2, S2err = integrate.quad(Sv2, r1, r2)
                #print "Time: " + str(t) + " Flux" + str((S1+S2)/10e-29) 
                self.flux.append((S1+S2)/10e-29) # change to mJy 

class XRB(): 
    def __init__(self):
        self.type = 'xrb'
        self.time = []
        self.flux = []
        self.lc_duration = 365
        self.rms = 1. 
        # Number of flares starting per day 
        # 1/rate = average number of days between flares 
        self.flareRate = 0.01 
        self.flares = [] 

    def one_flare(self,t,A,tau1,tau2,starttime=0): 
        if t < starttime: 
           return 0 
        
        t_s = t-starttime 
        k = exp(2*sqrt(tau1/tau2))          
        I = A*k*exp(-tau1/t_s -t_s/tau2)
        return I 

    def makeFlares(self, t): 
        I = 0 
        for eachflare in self.flares: 
            A = eachflare[0] 
            tau1 = eachflare[1] 
            tau2 = eachflare[2] 
            starttime = eachflare[3] 
            I = I + self.one_flare(t,A,tau1,tau2,starttime) 
        return I 
 
    def generate_lc(self, footprint="wide"): 
        timer = myutils.timestep() 
        timer.set_start_time(0) 
        timer.set_end_time(self.lc_duration) 
        timer.set_increment(1) 
        timer.make_timeseries(footprint) 
        nsteps = int(floor(timer.nsteps())) 
       
        # set up the parameters for flares 
        numdays = 0 
        while numdays < nsteps: 
            starttime = numdays + np.random.exponential(1/self.flareRate)
            A = np.random.pareto(1)+5*float(self.rms)
            tau1 = random.uniform(0.5,5) 
            tau2 = random.uniform(10,60) 
            self.flares.append([A,tau1,tau2,starttime])  
            numdays = starttime 

        for i in range(nsteps):
            t = timer.get_time() 
            self.time.append(t)
            if t == 0: 
                self.flux.append(0)
            else: 
                self.flux.append(self.makeFlares(t))
        
class fStar_RSCVn(): 
    def __init__(self):
        self.type = 'fStar_RSCVn'
        self.time = []
        self.flux = []
        self.lc_duration = 365
        self.rms = 1. 
        self.flareRate = 0.01 
        self.flares = [] 

    def one_flare(self,t,A,tau1,tau2,starttime=0): 
        if t < starttime: 
           return 0 
        
        t_s = t-starttime 
        k = exp(2*sqrt(tau1/tau2))          
        I = A*k*exp(-tau1/t_s -t_s/tau2)
        return I 

    def flareForest(self,t,A,smallflares,starttime=0):
        t_s = t-starttime   
        flarewidth = 0.5
        
        I = A*exp(-(starttime)**2/(2*flarewidth**2))
        for eachFlare in smallflares: 
            flareA = eachFlare[0] 
            flaret = eachFlare[1]
            I = I + flareA*exp(-(t_s+flaret)**2/(2*flarewidth**2))
        return I 
    
    def twoFlares(self,t,A1,A2,t1,t2,deltat,starttime=0): 
        t_s = t-starttime 
        I = A1*exp(-(t_s)**2/(2*t1**2))
        I = I + A2*exp(-(t_s+deltat)**2/(2*t2**2))
        return I 
  
    def makeFlares(self, t): 
        I = 0 
        for eachflare in self.flares:
            if eachflare[0] == 1:  
               A = eachflare[1] 
               tau1 = eachflare[2] 
               tau2 = eachflare[3] 
               starttime = eachflare[4] 
               I = I + self.one_flare(t,A,tau1,tau2,starttime) 
            if eachflare[0] == 2: 
               A = eachflare[1]
               numflares = eachflare[2]
               starttime = eachflare[3] 
               I = I + self.flareForest(t,A,numflares,starttime) 
            if eachflare[0] == 3: 
               A1 = eachflare[1]               
               A2 = eachflare[2]               
               t1 = eachflare[3]               
               t2 = eachflare[4]
               deltat = eachflare[5]
               starttime = eachflare[6]
               I = I + self.twoFlares(t,A1,A2,t1,t2,deltat,starttime)                
        return I 
 
    def generate_lc(self, footprint="wide"): 
        timer = myutils.timestep() 
        timer.set_start_time(0) 
        timer.set_end_time(self.lc_duration) 
        timer.set_increment(1) 
        timer.make_timeseries(footprint) 
        nsteps = int(floor(timer.nsteps())) 
       
        # set up the parameters for flares 
        numdays = 0 
        while numdays < nsteps: 
            randtime = np.random.exponential(1/self.flareRate)
            starttime = numdays + randtime 
            flareType = random.randint(1,3) 
            # Fast rise exponential decay type flare 
            if flareType == 1: 
               A = np.random.pareto(1)+5*float(self.rms)
               tau1 = random.uniform(0.5,2) 
               tau2 = random.uniform(10,40) 
               self.flares.append([1,A,tau1,tau2,starttime])  

            # Flare forest 
            if flareType == 2: 
               A = np.random.pareto(1)+5*float(self.rms) 
               numflares = random.randint(4,10) 
               smallflares = [] 
               for i in range(numflares): 
                  sflareA = A/random.randint(2,10)
                  sflaret = i*randtime/10 
                  smallflares.append([sflareA,sflaret])  
               self.flares.append([2,A,smallflares,starttime]) 
            
            # one flare in another broad flare 
            if flareType == 3: 
               A1 = np.random.pareto(1)+5*float(self.rms) 
               A2 = A1/random.uniform(2,4)
               t2 = randtime/random.uniform(4,8) 
               t1 = randtime/random.uniform(10,15)
               deltat = randtime/random.uniform(1,10)
               self.flares.append([3,A1,A2,t1,t2,deltat,starttime]) 

            numdays = starttime 

        for i in range(nsteps):
            t = timer.get_time() 
            self.time.append(t)
            if t == 0: 
                self.flux.append(0)
            else: 
                self.flux.append(self.makeFlares(t))
        
class fStar_dMe(): 
    def __init__(self):
        self.type = 'fStar_dMe'
        self.time = []
        self.flux = []
        self.lc_duration = 365
        self.rms = 1. 
        self.flareRate = 0.01 
        self.flares = [] 

    def one_flare(self,t,A,tau1,tau2,starttime=0): 
        if t < starttime: 
           return 0 
        
        t_s = t-starttime 
        k = exp(2*sqrt(tau1/tau2))          
        I = A*k*exp(-tau1/t_s -t_s/tau2)
        return I 
    
    def twoFlares(self,t,A1,A2,t1,t2,deltat,starttime=0): 
        t_s = t-starttime 
        I = A1*exp(-(t_s)**2/(2*t1**2))
        I = I + A2*exp(-(t_s+deltat)**2/(2*t2**2))
        return I 
  
    def makeFlares(self, t): 
        I = 0 
        for eachflare in self.flares:
            if eachflare[0] == 1:  
               A = eachflare[1] 
               tau1 = eachflare[2] 
               tau2 = eachflare[3] 
               starttime = eachflare[4] 
               I = I + self.one_flare(t,A,tau1,tau2,starttime) 
            if eachflare[0] == 2: 
               A1 = eachflare[1]               
               A2 = eachflare[2]               
               t1 = eachflare[3]               
               t2 = eachflare[4]
               deltat = eachflare[5]
               starttime = eachflare[6]
               I = I + self.twoFlares(t,A1,A2,t1,t2,deltat,starttime)                
        return I 
 
    def generate_lc(self, footprint="wide"): 
        timer = myutils.timestep() 
        timer.set_start_time(0) 
        timer.set_end_time(self.lc_duration) 
        timer.set_increment(1) 
        timer.make_timeseries(footprint) 
        nsteps = int(floor(timer.nsteps())) 
       
        # set up the parameters for flares 
        numdays = 0 
        while numdays < nsteps: 
            randtime = np.random.exponential(1/self.flareRate)
            print randtime 
            starttime = numdays + randtime 
            flareType = random.randint(1,2) 
            # Fast rise exponential decay type flare 
            if flareType == 1: 
               A = np.random.pareto(1)+10*float(self.rms)
               tau1 = random.uniform(0.0001,0.001) 
               tau2 = random.uniform(0.01,0.025) 
               self.flares.append([1,A,tau1,tau2,starttime])  
            
            # one flare in another broad flare 
            if flareType == 2: 
               A1 = np.random.pareto(1)+10*float(self.rms) 
               A2 = A1/random.uniform(2,4)
               t2 = random.uniform(0.005,0.02) 
               t1 = random.uniform(0.005,0.02)
               deltat = randtime/random.uniform(1,10)
               self.flares.append([2,A1,A2,t1,t2,deltat,starttime]) 

            numdays = starttime 

        for i in range(nsteps):
            t = timer.get_time() 
            self.time.append(t)
            if t == 0: 
                self.flux.append(0)
            else: 
                self.flux.append(self.makeFlares(t))
        
