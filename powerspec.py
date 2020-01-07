##############################################################################
## This file is part of 'smurftestapps'.
## It is subject to the license terms in the LICENSE.txt file found in the 
## top-level directory of this distribution and at: 
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
## No part of 'smurftestapps', including this file, 
## may be copied, modified, propagated, or distributed except according to 
## the terms contained in the LICENSE.txt file.
##############################################################################

# example file read for data

import numpy
import matplotlib.pyplot as plt
import sys
from scipy import signal

if len(sys.argv) < 2:
    fn = '/data/smurf_stream/data.txt'
else:
    fn = sys.argv[1]
dat = numpy.loadtxt(fn)

print(dat.shape)

tm = dat[:,0]
tmd = numpy.diff(tm)
tstep = sum(tmd) / len(tmd)




print("timestep = ", tstep); 

n = 5
fx, pden = signal.welch(dat[:,n], 1.0/tstep, nperseg = 16384)
plt.plot(fx, pden, 'r-')
plt.xscale('log')
plt.yscale('log')
plt.title('%i' % (n))
plt.show()



