##############################################################################
## This file is part of 'smurftestapps'.
## It is subject to the license terms in the LICENSE.txt file found in the 
## top-level directory of this distribution and at: 
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
## No part of 'smurftestapps', including this file, 
## may be copied, modified, propagated, or distributed except according to 
## the terms contained in the LICENSE.txt file.
##############################################################################

#puts correct PVs into smurf buffer

import epics

TES_base_pv = ':AMCc:FpgaTopLevel:AppTop:AppCore:RtmCryoDet:RtmSpiMax:TesBiasDacDataRegCh'
HEMT_pv =     ':AMCc:FpgaTopLevel:AppTop:AppCore:RtmCryoDet:RtmSpiMax:HemtBiasDacDataRegCh[33]'#for hemt bias
timing_rate_pv = ':AMCc:FpgaTopLevel:AmcCarrierCore:AmcCarrierTiming:EvrV2CoreTriggers:EvrV2ChannelReg[0]:RateSEl'
rate_list_pv = 'TPG:SMRF:1:FIXEDDIV'  # no test_epics header needed


header_tes_base_pv = ':AMCc:FpgaTopLevel:AppTop:AppCore:TimingHeader:rtmDacConfig'
header_fluxramp_stepsize_pv =  ':AMCc:FpgaTopLevel:AppTop:AppCore:TimingHeader:fluxRampStepSize'
header_fluxramp_stepsize_pv =  ':AMCc:FpgaTopLevel:AppTop:AppCore:TimingHeader:fluxRampResetValue'


timing_base_rate = 4.8e5 # assume fixed

tes_out_bits= 32  # 32 bit
tes_out_words = 12 # 12 output words

tes_in_bits = 20 # 20 bit numbers



def get_bit(inval, bit):
    return((inval & (0x1 << bit)) >> bit) # pretty simple

def set_bit(inval, bit, x):  # x is the number to be set  (use lowest bit)
    return(((~(0x1 << bit)) & inval) + ((x & 0x1)<<bit))  # set bit return



def get_tes_values(epics_base = 'test_epics'):
    val =[0]*18  # includes hemt bias, and unused block
    for j in range(0, 16):
        tesp = epics.caget(epics_base + TES_base_pv + '['+ str(2*j+2) + ']')  # positive dac
        tesn =  epics.caget(epics_base + TES_base_pv + '['+ str(2*j+1) + ']')  # negative dac
        val[j] = tesp - tesn
    val[17] = epics.caget(epics_base + HEMT_pv) # just add hemt pv    
    return(val);

a = get_tes_values()
print(a)
