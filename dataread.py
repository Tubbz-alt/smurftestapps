##############################################################################
## This file is part of 'smurftestapps'.
## It is subject to the license terms in the LICENSE.txt file found in the 
## top-level directory of this distribution and at: 
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
## No part of 'smurftestapps', including this file, 
## may be copied, modified, propagated, or distributed except according to 
## the terms contained in the LICENSE.txt file.
##############################################################################

def bytes_to_32bit(array, start):
    return  array[start] + array[start+1] * 0x100 + array[start+2] * 0x10000 + array[start+3] * 0x1000000



fname = "test.dat"
f = open(fname, "rb")
header_length = 128;
header_wordsize = 1; # bytes
data_length = 528;
data_wordsize = 4;  # words

framesize = header_length * header_wordsize + data_length * data_wordsize


for n  in range(0, 1000000):
    header=  []
    raw = f.read(framesize) # should be bytes
    if (len(raw) < framesize):
        break

    for j in range(0, header_length):
        header.append(raw[j])   # just use single word

    data = []
    for j in range(0, data_length):
        x = header_length + j * data_wordsize
        data.append(bytes_to_32bit(raw, x))

    syncword = bytes_to_32bit(header, 96);
    epics_nanoseconds = bytes_to_32bit(header, 72)
    epics_seconds = bytes_to_32bit(header, 76)
    #print("frame = ", n, "MCEsync = ", syncword , "epics s = ", epics_seconds, "ns=", epics_nanoseconds,  "data(0) = ", data[0])
    if(not(n%1000)):
       print(n)
       

    




