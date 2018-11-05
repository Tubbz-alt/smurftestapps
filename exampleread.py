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

