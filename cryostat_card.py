##############################################################################
## This file is part of 'smurftestapps'.
## It is subject to the license terms in the LICENSE.txt file found in the 
## top-level directory of this distribution and at: 
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
## No part of 'smurftestapps', including this file, 
## may be copied, modified, propagated, or distributed except according to 
## the terms contained in the LICENSE.txt file.
##############################################################################

#crytest

import epics
import time

class cryostat_card():
  def __init__(self, readpv_in, writepv_in):
    self.readpv = readpv_in
    self.writepv = writepv_in
    self.relay_address = 0x2
    self.hemt_bias_address = 0x3
    self.a50K_bias_address = 0x4
    self.temperature_address = 0x5
    self.cycle_count_address = 0x6  # used for testing
    self.ps_en_address = 0x7 # PS enable (HEMT: bit 0, 50k: bit 1)
    self.ac_dc_status_address = 0x8 # AC/DC mode status (bit 0: FRN_RLY, bit 1: FRP_RLY)
    self.adc_scale = 3.3/(1024.0 * 5);
    self.temperature_scale = 1/.028; # was 100
    self.temperature_offset =.25;
    self.bias_scale = 1.0
    self.max_retries = 5;  #number of re-tries waiting for response
    self.retry = 0 # counts nubmer of retries
    self.busy_retry = 0  # counts number of retries due to relay busy status

  def do_read(self, address):
    epics.caput(self.writepv, cmd_make(1, address, 0)) #need double write to make sure buffer is updated
    for self.retry in range(0, self.max_retries):
      epics.caput(self.writepv, cmd_make(1, address, 0))
      data = epics.caget(self.readpv)
      addrrb = cmd_address(data)
      if (addrrb == address):
        return(data)
    return(0)

    return (epics.caget(self.readpv))

  def write_relays(self, relay):  # relay is the bit partern to set
    epics.caput(self.writepv, cmd_make(0, self.relay_address, relay))

  def read_relays(self):
    for self.busy_retry in range(0, self.max_retries):
      data = self.do_read(self.relay_address)
      if ~(data & 0x80000):  # check that not moving
        return(data & 0x7FFFF)
        time.sleep(0.1) # wait for relays to move
    return(80000) # busy flag still set

  def read_hemt_bias(self):
    data = self.do_read(self.hemt_bias_address)
    return((data& 0xFFFFF) * self.bias_scale * self.adc_scale)

  def read_50k_bias(self):
    data = self.do_read(self.a50K_bias_address)
    return((data& 0xFFFFF) * self.bias_scale * self.adc_scale)

  def read_temperature(self):
    data = self.do_read(self.temperature_address)
    volts = (data & 0xFFFFF) * self.adc_scale
    return((volts - self.temperature_offset) * self.temperature_scale)

  def read_cycle_count(self):
    data = self.do_read(self.count_address)
    return( cmd_data(data))  # do we have the right addres

  def write_ps_en(self, enables):
    epics.caput(self.writepv, cmd_make(0, self.ps_en_address, enables))

  def read_ps_en(self):
    data = self.do_read(self.ps_en_address)
    return(cmd_data(data))

  def read_ac_dc_status(self):
    data = self.do_read(self.ac_dc_status_address)
    return(cmd_data(data))

# low level data conversion

def cmd_read(data):  # checks for a read bit set in data
   return( (data & 0x80000000) != 0)

def cmd_address(data): # returns address data
   return((data & 0x7FFF0000) >> 20)

def cmd_data(data):  # returns data
   return(data & 0xFFFFF)

def cmd_make(read, address, data):
   return((read << 31) | ((address << 20) & 0x7FFF00000) | (data & 0xFFFFF))


def test():
  readpv = 'test_epics:AMCc:FpgaTopLevel:AppTop:AppCore:RtmCryoDet:SpiCryo:read'
  writepv = 'test_epics:AMCc:FpgaTopLevel:AppTop:AppCore:RtmCryoDet:SpiCryo:write'

  c = cryostat_card(readpv, writepv)
  n = 0
  error_count = 0;
  while 1:
    n = n + 1
    if (n % 2):
      relay_set = 0xF;
     # print 'SET'
    else:
      relay_set = 0xF;
    #  print 'RESET'
    #c.write_relays(relay_set)  # disable relay write
    time.sleep(0.2)
    relay  = c.read_relays()
    hemt_bias = c.read_hemt_bias()
    bias_50K = c.read_50k_bias()
    temperature = c.read_temperature()
    hemt_bias_s = str(hemt_bias)[0:6]
    bias_50K_s = str(bias_50K)[0:6]
    temperature_s = str(temperature)[0:6]

    if (relay_set != relay):
      error_count = error_count + 1;

    print('set= ', hex(relay_set), 'rb= ', hex(relay), 'h_bias=', hemt_bias_s, '50K bias = ', bias_50K_s, 'degC =', temperature_s,'ec=', error_count,'rtry=', c.retry, c.busy_retry )


