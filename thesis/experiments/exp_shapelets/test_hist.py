import numpy as np
import matplotlib.pyplot as plt
#--- the two samples ---
samples1 = [1, 1, 1, 3, 2, 5, 1, 10, 10, 8]
samples2 = [6, 6, 6, 1, 2, 3, 9, 12 ] 
samples3 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 11, 12]
 
N = 12 # number of bins
hist1 = np.array([0] * N )
hist2 = np.array([0] * N )
hist3 = np.array([0] * N )
  
#--- create two histogram. Values of 1 go in Bin 0 ---
for x in samples1:
    hist1[x-1] += 1
for x in samples2:
    hist2[x-1] += 1
for x in samples3:
    hist3[x-1] += 1
 
 #--- display the bar-graph ---        
width = 1

p1 = plt.hist( np.arange(0,N)+0.5, hist1, width, color='#9932cc' )
p2 = plt.hist( np.arange(0,N)+0.5, hist2, width, color='#ffa500', bottom=3 )
p3 = plt.bar( np.arange(0,N)+0.5, hist3, width, color='#d2691e', bottom=2 )
plt.legend( (p1[0], p2[0], p3[0]), ( 'hist1', 'hist2', 'hist3' ) )
plt.xlabel( 'Bins' )
plt.ylabel( 'Count' )
#plt.axis([1, 46, 0, 6])
plt.xticks( np.arange( 1,N+1 ) )
plt.axis( [width/2.0, N+width/2.0, 0, max( hist1+hist2+hist3)] )
plt.show()
