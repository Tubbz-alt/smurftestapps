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

if len(sys.argv) < 2:
    fn = '/data/smurf_stream/testout.txt'
else:
    fn = sys.argv[1]
dat = numpy.loadtxt(fn)

print(dat.shape)

tm = dat[:,0]
for i in range(40,50):
    plt.figure()
    plt.plot(tm, dat[:,i], 'r-')
    plt.title('%i' % (i))
    plt.show()

plt.show()

