##############################################################################
## This file is part of 'smurftestapps'.
## It is subject to the license terms in the LICENSE.txt file found in the 
## top-level directory of this distribution and at: 
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
## No part of 'smurftestapps', including this file, 
## may be copied, modified, propagated, or distributed except according to 
## the terms contained in the LICENSE.txt file.
##############################################################################

#channel_test
#used to set valuse to channels

import epics
import time
import pylab as P
import os
import matplotlib.pyplot as plt
import numpy
from scipy import signal

pwelch_ratio = 8;  # to set size of nperseg

epics_base = 'test_epics:'
#epics_base = 'dev_epics:'

base_name =  epics_base + "AMCc:FpgaTopLevel:AppTop:AppCore:StreamReg:StreamData"
user_config = epics_base +"AMCc:FpgaTopLevel:AppTop:AppCore:TimingHeader:userConfig[0]"

infname = "/tmp/data.dat" 
outfname = "/tmp/data.txt"

def set_bit(pv, mask, val):  # sets a bit without changeing others
    print("pv = ", pv)
    old = epics.caget(pv)  # old value
    tmp = old & (0xffffffff - mask) # everything but hte mask value
    new = tmp + (val & mask)
    epics.caput(pv, new)


def increment_vals():
    for j in range(0,528):
        lname = "[" + str(j) + "]"
        pv = base_name+ lname
        epics.caput(pv, j*32)


def zero(nx=527):
    for j in range(0,nx):
        lname = "[" + str(j) + "]"
        pv = base_name+ lname
        epics.caput(pv,0)

def ramp(chan = 0, rate = 1):
    for t in range(0,1000000000):
        lname = "[" + str(chan) + "]"
        raw = t * rate; 
        value = raw & 0xffff
        pv = base_name+ lname
        print(t, raw, value)
        epics.caput(pv, value)
        time.sleep(0.1)



def demo(scale1 = 10000, scale2 = 12000,  w1 = .01, w2 = .012):
    for t in range (0, 100000000):
        v1 = scale1 * P.sin(t*w1)
        v2 = scale2 * P.sin(t*w2)
        pv1 = base_name + "[0]"
        pv2 = base_name + "[1]"
        epics.caput(pv1, v1)
        epics.caput(pv2, v2)
        time.sleep(0.1)


def write_smurf():

    a = P.genfromtxt('smurf_words.txt',dtype=None, delimiter=',')
    xs = a[:,0]
    ys = a[:,1]
    n= 45
    N = 100
    for k in range(N):
        for i in range(45):
            pv1 = base_name + "[0]"
            pv2 = base_name + "[1]"
            epics.caput(pv1, 1000.*xs[i])
            epics.caput(pv2, 1000.*ys[i])
            time.sleep(0.1) 


def start_collect():  # starts data collection
    set_bit(user_config, 0x6, 0x6) # clear and disable file write
    time.sleep(0.1) # to make sure write goes through
    #os.system('alias rm=rm');
    #os.system('rm /tmp/data.*')
    #time.sleep(0.1)
    set_bit(user_config, 0x6, 0x0) # clear bits to start writing
    
    

def stop_collect(): # stops data collection
   set_bit(user_config, 0x4, 0x4) # disables file write, nothing else

# first is first channel nubmer
# last is last channel number
#filt is number of samples to downsample
def extract_data(first=0, last=0, filt=1):
    cmd = "./extractdata "+ infname + " " + outfname + " " +str(first) +" "+ str(last) +" "+ str(filt)
    print("extract command:", cmd);
    os.system(cmd)
    
def take_noise_curves(seconds=10):
    start_collect()
    for j in range (0, seconds):
        print(j," out of ", seconds,  " seconds");
        time.sleep(1)  # kludgy way to do it
    stop_collect() #that should save the file

def plot_data(firstch=0, lastch=0, flt=1):
    extract_data(firstch, lastch, flt) # executes C command
    print("done  extracting")
    dat = numpy.loadtxt(outfname) # loads text data (numpy)
    print("data shape", dat.shape)
    s = dat.shape
    points = s[0] #how many points in teh dataset
    tm = dat[:,0]
    tmd = numpy.diff(tm)
    tstep = sum(tmd) / len(tmd)

    print("min time", min(tm),  "max time", max(tm))
    print(tm[0:10])
    tmp = int(points / pwelch_ratio)
    tmp2 = P.log(tmp) / P.log(2)  # get in powers of to
    tmp3 = int(tmp2)
    np = pow(2,tmp3)
    print("nperseg = ", np)
    print("tstep = ", tstep)
    fx, pden = signal.welch(dat[:,1], 1.0/tstep, nperseg = np)

    for j in range(0, lastch+1-firstch):
        print("plotting", j)
        plt.plot(tm, dat[:,j+1])

    plt.show()
  
    plt.plot(fx, pden, 'r-')
    plt.xscale('log')
    plt.yscale('log')
    plt.show()



