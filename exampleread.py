# example file read for data
import numpy
import matplotlib.pyplot as plt

dat = numpy.loadtxt('/data/smurf_stream/testout.txt');


tm = dat[:,0]
data1 = dat[:,1]
data2 = dat[:,2]

plt.plot(tm, data1, 'r-')

plt.show()

