##############################################################################
## This file is part of 'smurftestapps'.
## It is subject to the license terms in the LICENSE.txt file found in the 
## top-level directory of this distribution and at: 
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
## No part of 'smurftestapps', including this file, 
## may be copied, modified, propagated, or distributed except according to 
## the terms contained in the LICENSE.txt file.
##############################################################################

# takes 16 X 24 bit TES data, converts to packed 12x32 bit.
import epics

tesp = [0]*16
tesn = [0]*16
sub = [0]* 16  # subtracted data arrys

def get_byte(dat, n):
    tmp = 0xff << (8 * n)  # make mask
    tmp2 =(tmp & dat) >> (8 * n)
    return(0xffffff & tmp2)

def set_byte(dat, val, n):
    tmp = 0xff << (8 * n)
    tmp2 = 0xffffffff - tmp # inverted
    tmp3 = ((dat & tmp2) + (val << (8 * n)))
    return ( 0xffffffff & tmp3) # limit to 32 bit


input_pv_block = ':AMCc:FpgaTopLevel:AppTop:AppCore:RtmCryoDet:RtmSpiMax:TesBiasDacDataRegCh' # pvs to output for timing stream
out_pv_block = ':AMCc:FpgaTopLevel:AppTop:AppCore:TimingHeader:rtmDacConfig' # pvs to output for timing stream

def TES_to_header(epics_base = 'test_epics'):

    for j in range (0, 16): # get from PVs
        tesp[j] = epics.caget(epics_base + input_pv_block + '['+ str(2*j+2) + ']')  # positive dac
        tesn[j] =  epics.caget(epics_base + input_pv_block + '['+ str(2*j+1) + ']')  # negative dac
    n = 0   #output word number
    m = 0 # input word number
    b = 0  # byte in intput word
    r = 0 # byte in output word
    outx = [0]*12  # 12 output words for 16 input words

    for j in range(0, 16):
        sub[j] = ( 0xFFFFFF  & ((tesp[j] - tesn[j])))

    while 1:
        outx[n] = set_byte(outx[n], get_byte(sub[m], b), r) # everythign happens here
        print('m = ', m, 'b = ', b, 'n = ', n, 'r = ', r, 'byte = ', get_byte(sub[m], b),'in = ', hex(sub[m]),'out = ',  hex(outx[n]))
        b = b + 1
        r = r + 1
        if b == 3:
            b = 0
            m = m + 1
        if r == 4:
            r = 0
            n = n + 1
        if (m == 16) or (n== 12):   #done
            break

        for n in range(0, 12):
            epics.caput(epics_base + output_pv_block + '[' + str(n) + ']', outx[n+1])  # write pvs to timing stream



                            
