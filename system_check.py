#!/usr/bin/env python3

# checker program

import sys
import os
import epics
import time
import pysmurf
import cryostat_card
from optparse import OptionParser
...
parser = OptionParser()
parser.add_option("-s","--smurf-slot", dest="smurf_slot_id",
                  help="Which smurf slot to configure.  Required input.",
                  type="int", metavar="[1-6]")

parser.add_option("-y","--defaults", dest="defaults_yml",
                  help="Path to defaults.yml file.  If not provided, will default to whatever's hard-coded in the transmitter.",
                  type="str", metavar="PATH")

parser.add_option("-e","--epics-root", dest="epics_root",
                  default='test_epics',
                  help="EPICS root name to instantiate pyrogue server with (e.g. test_epics).  If not provided, will default to whatever's hard-coded in the transmitter.",
                  type="str", metavar="NAME")

parser.add_option("-t","--pyrogue", dest="pyrogue_tarball",
                  help="Path to pyrogue tarball.  If not provided, will default to whatever's hard-coded in the transmitter.",
                  type="str", metavar="PATH")

#parser.add_option("-q", "--quiet",
#                  action="store_false", dest="verbose", default=True,
#                  help="don't print status messages to stdout")

(options, args) = parser.parse_args()

if not options.smurf_slot_id:   # if filename is not given
    parser.error('smurf_slot_id not given')

# optional command line arguments for transmitter
optional_transmitter_opts=' -r %s'%(options.epics_root)
if options.defaults_yml:
    optional_transmitter_opts+=' -y %s'%(options.defaults_yml)
if options.pyrogue_tarball:
    optional_transmitter_opts+=' -p %s'%(options.pyrogue_tarball)

#import rf_test

docstring = """TEST"""

## parameters
start_with_power_cycle=True
rtmeth_interface=False

# Crate
crate_ip='10.0.1.4'
crate_id=3
smurf_slot_id=options.smurf_slot_id
wait_after_deactivate=5 #sec
wait_after_activate=60 #sec

# Parameters for RF testing
rf_fmin = 5010 # minimum test frequency 
rf_fmax = 5990 # maximum test frequency
rf_runs = 7 # number of test runs between frequencies
rf_min_ratio = 20  # minimum OK ration between desired line and other lines 

# EPICs
epics_base = options.epics_root.rstrip()+':'

# Paths
testapps_dir = '/usr/local/controls/Applications/smurf/smurftestapps/'
tmpfile = "/tmp/checkertmp"
config_file= "/usr/local/controls/Applications/smurf/smurf2mce/current/mcetransmit/smurf2mce.cfg"
pidfile = "/tmp/smurfpid"

# Files
transmit_dir="/usr/local/controls/Applications/smurf/smurf2mce/current/mcetransmit/"
config_file= os.path.join(transmit_dir,"smurf2mce.cfg")

# Flags
rf_test_on = False  # assume no rf testing 
receiver_present = False # is there a receiver?  if yes, pulls ip from receiver_ip in smurf2mce.cfg
pyrogue_gui = True # pyrogue gui?

# PCIe
pcie_pv_base = "SIOC:SMRF:ML00:AO" #A "Oh", not A "zero"
pcie_pv_offset = 100 # offset all pvs by this much
rssi_chan = smurf_slot_id-2   # for card #2

# Timing
timestamp0_pv = epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:TimingHeader:timestamp[0]"
mceData_pv = epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:TimingHeader:mceData"

rate_select_pv = epics_base+"AMCc:FpgaTopLevel:AmcCarrierCore:AmcCarrierTiming:EvrV2CoreTriggers:EvrV2ChannelReg[0]:RateSel"
rate_def_pv = "TPG:SMRF:1:FIXEDDIV"

timing_dest_select_pv = epics_base+"AMCc:FpgaTopLevel:AmcCarrierCore:AmcCarrierTiming:EvrV2CoreTriggers:EvrV2ChannelReg[0]:DestSel"

# AMC
load_defaults = True # whether or not to load defaults.yml
set_defaults_pv = epics_base+"AMCc:setDefaults"
global_enable_pv = epics_base+"AMCc:enable"

# Cryostat card
cryostat_card_readpv =  epics_base + "AMCc:FpgaTopLevel:AppTop:AppCore:RtmCryoDet:SpiCryo:read"
cryostat_card_writepv = epics_base + "AMCc:FpgaTopLevel:AppTop:AppCore:RtmCryoDet:SpiCryo:write" 

## end parameters

if len(sys.argv) >1:
    if (sys.argv[1].find('rftest') != -1):
        rf_test_on = True

if rf_test_on:
    print("Will do RF testing - be sure loopback is connected, and cryostat disconnecdted.  WARNING ctrl-C if not connected!!")
else:
    print("No RF testing")

# pvs used in setup
mispv = []
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:SysgenCryo:Base[2]:iqSwapIn")
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:SysgenCryo:Base[2]:iqSwapOut" )
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:SysgenCryo:Base[2]:refPhaseDelay")    
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:SysgenCryo:Base[2]:refPhaseDelayFine")
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:SysgenCryo:Base[2]:toneScale") 
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:SysgenCryo:Base[2]:analysisScale")
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:SysgenCryo:Base[2]:feedbackEnable")  
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:SysgenCryo:Base[2]:feedbackGain")
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:SysgenCryo:Base[2]:lmsGain")
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:SysgenCryo:Base[2]:digitizerFrequencyMHz")
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:SysgenCryo:Base[2]:bandCenterMHz")
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:SysgenCryo:Base[2]:numberSubBands")
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:DaqMuxV2[0]:Bsa[1]")
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:MicrowaveMuxCore[0]:LMK:LmkReg_0x011E")
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:DaqMuxV2[0]:TriggerDaq")
# dac registers
dac_base_pv = epics_base + "AMCc:FpgaTopLevel:AppTop:AppCore:MicrowaveMuxCore[0]:"
dac_nums = [95]
dac_vals = [0x123]

num_misc_pvs = len(mispv)

def cmdrun(a = 'ls'):
    cmdstr = a + " > " + tmpfile
    os.system(cmdstr)
    with open(tmpfile) as f:
        cmdout = f.read()
    return(cmdout)

# ANSI color escape sequences
class Color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Status:
    OK = '[' + Color.OKGREEN + str.center('OK',4) + Color.ENDC + ']'
    FAIL = '[' + Color.FAIL + str.center('FAIL',4) + Color.ENDC + ']'
    WARN = '[' + Color.WARNING + str.center('WARN',4) + Color.ENDC + ']'

def print_success(msg,status=Status.OK):
    rows, columns = os.popen('stty size', 'r').read().split()
    print(msg+' '*(int(columns)-len(msg)-len(status))+status)

os.system("sudo service sioc-smrf-ml00 restart")

if start_with_power_cycle:
    print("Note: Power cycle smurf card to put in known state, wait %d seconds"%(wait_after_deactivate+wait_after_activate))
    os.system("fru_deactivate %s/%d"%(crate_ip,smurf_slot_id))
    print("wait %d seconds"%(wait_after_deactivate))
    time.sleep(wait_after_deactivate)
    print("reactivating card")
    os.system("fru_activate %s/%d"%(crate_ip,smurf_slot_id))
    print("wait %d seconds for firmware load"%(wait_after_activate))
    time.sleep(wait_after_activate)
    print("done power cycling smurf")

for trial in range(0,4):  # make 4 attempts to get smurf working
    print("Note: trial number = ", trial)

    smurf_problem = False 
    # check on pcie card
    a = cmdrun("/sbin/lspci")
    b = a.find("SLAC")
    if (b < 0):
        print_success("ERROR: PCIE card not running, Restart computer as shown below",Status.FAIL)
        print("INSTRUCTION: become root then shutdown now -r")
        exit()
    print_success("PCIE card running")

    #is timing running
    a = cmdrun("screen -list")
    b = a.find("ts01")
    if (b < 0):
        print_success("ERROR: ts01 timing service not running, restarting",Status.FAIL)
        os.system("sudo service sioc-smrf-ts01 restart")
        continue
    else:
        print_success("ts01 timing service is running")

    b = a.find("ml00")
    if (b < 0):
        print_success("ml00 epics service not running",Status.FAIL)
        os.system("sudo service sioc-smrf-ml00 restart")
        continue
    else:
        print_success("ml00 service is running")

    # is pcie gui running?
    for j in range(0,3):
        ps_return = cmdrun("ps aux")
        b = ps_return.find("Pcie_checker.py")
        if(b < 0):
            print_success("Note: PCIE checker not running, will start",Status.FAIL)
            cmdrun(testapps_dir+"run_pcie_checker.sh")
            time.sleep(5) 
        else:
            print_success("pcie checker already running"); 
            break
    if j >= 2:
        print_success("ERROR - FATAL unable to start pcie checker - giving up",Status.FAIL)
        exit()

    # If 
    if receiver_present:
        #check connection to MCE computer.
        with open(config_file, "r") as f:
            for line in f:
                x= line
                if len(x) == 0:
                    print_success("Warning: couldn't find IP address in config file",Status.WARN)
                    break
                b = x.find("receiver_ip")
                if (b >= 0):
                    c = x.split() # split into substrings
                    ip = c[1]  # the ip address
                    print("Note: receiver IP address in smurf2mce.cfg = ", ip)
                    print("Note: check that IP address can be reached")
                    a = cmdrun("ping -c1 " + ip)
                    r = a.find("rtt") #only get this when ping returns
                    if (r < 0):
                        print_success("ERROR: could not ping MCE computer, check connection",Status.FAIL)
                        print("fix networking, then restart this program")
                        exit()
                    else:
                        print_success("able to ping MCE computer")
                    break

    try:
        #Run Smurf,  new copy will stop on old
        print("starting smurf in %sgui mode, - may kill running copy, wait 90 seconds to start"%(['' if pyrogue_gui else 'no'][0]))
        run_smurf_cmd=testapps_dir+"run_smurf.sh -t %s -m %s -c %d -s %d %s %s%s"%(transmit_dir,crate_ip,crate_id,smurf_slot_id,['' if pyrogue_gui else '--nogui'][0],['-e' if rtmeth_interface else ''][0],optional_transmitter_opts)
        print('run_smurf_cmd=%s'%(run_smurf_cmd))
        os.system(run_smurf_cmd)
        time.sleep(45)

        for j in range(0,3):
            ps_return = cmdrun("ps aux")
            b = ps_return.find("pyrogue_server.py")
            if (b < 0):
                print_success("Warning: SMURF still not running - starting",Status.WARN)
                os.system(testapps_dir+"run_smurf.sh")
                print("waiting 45 seconds for smurf to start")
                time.sleep(45)
                print("done waiting of smurf to start")
            else:
                print_success("SMURF is running")
                break  
        if j >= 2:
            print_success("unable to start smurf",Status.FAIL)
            smurf_problem = True

        XX = 0
        if XX:     # This section disabled until epics is fixed.
        # check valid counts increment
            c1 = epics.caget(pcie_pv_base + str(pcie_pv_offset + rssi_chan))
            time.sleep(1)
            c2 = epics.caget(pcie_pv_base + str(pcie_pv_offset + rssi_chan))
            d = c2-c1
            if (d <= 0):
                print_success("ERROR:  RSSI link is not updating delta = "+str(d),Status.FAIL);
                smurf_problem = True
            else:
                print_success("RSSI link updating, delta = " + str(d))
        else:
            print("NOTE: skipping PCIE test becuase EPICS is broken.  Need to modify this script to enable again") 

        # enable register polling
        print("enabling register polling")
        epics.caput(global_enable_pv, True)  # we normally leave this off to reduce dropped frames

        if load_defaults:
            print("ready to set defaults")
            epics.caput(set_defaults_pv, 1)
            print("set defaults done")
            time.sleep(15)
            print("sleep done");

        #check timing setup
        XX = 0
        if XX:  # disabled while epics is broken. 
            a = epics.caget(rate_def_pv)
        else:
            print("NOTE: skipping PCIE test because EPICS is broken.  Need to modify this script to enable again") 
            a = [32,40,48,60,80,96,120,240,480]
        b = epics.caget(rate_select_pv) # which rate are we using
        print("b = ", b)
        print("a[b] = ", a[b])
        rate = 480000.0 / a[b]
        print("rate - ", rate);
        if (b == 0):
            print("Note: Rate not initialized - rate 0 -> 48KHz, setting rate to 4KHz")
            epics.caput(rate_select_pv, 0x6) # select rate
        elif ((rate < 1000) or (rate > 8000)):
            print("Warning: flux ramp and frame rate = ", rate, "Hz probably out of range")
        else:
            print ("OK: Flux ramp and frame rate", rate, "Hz")
        b = epics.caget(timing_dest_select_pv)
        if (b != 0x20000):
            print("Note: mysterious timing destination pv != 0x20000, got " , hex(b), " will fix")
            epics.caput(timing_dest_select_pv, 0x20000) 

        #check incrementing timing counters
        a1 = 0
        a2= 0  #kludge if pv is down. 
        a1 = epics.caget(timestamp0_pv) # high rate incrementing conter from timing
        time.sleep(0.1)
        a2 = epics.caget(timestamp0_pv)
        if ((a1-a2) == 0):
            print_success("Error: timing system fast counter not incrementing. Check timing fiber, but also possibly a SMURF problem",Status.FAIL)
            smurf_problem = True
        else:
            print_success("OK: Timing system counter incrementing")

        a1 = [0]
        a2 = [0]
        a1 = epics.caget(mceData_pv) # syncbox number
        time.sleep(0.1)
        a2 = epics.caget(mceData_pv)  # returns a long array for some strange reason
        b = a1-a2
        mx = max(b)
        mn = min(b)

        if((mx == 0) and (mn ==0)):
            print("Note: MCE syncword is not incrementing - may be disabled by GCP")
        else:
            print("OK: Sync word incrementing")
    except:
        print("some failure, proably smurf problem")
        smurf_problem = True

   
    print("testing PVs")
    for n in range(0, num_misc_pvs):
        try:
            x = epics.caget(mispv[n])
            if (x == None):
                print_success("Could not read "+str(mispv[j]),Status.FAIL)
                smurf_problem = True
                break  # end this loop, 
        except:
            smurf_problem = True
            print_success("Error: " + str(mispv[n]) + " returned error",Status.FAIL)
            break  # break out of loop
        print_success("OK, checking " + str(mispv[n]) + " = " + str(x))
    if (smurf_problem == False):
        #try cryostat card
        try:
            C = cryostat_card.cryostat_card(cryostat_card_readpv, cryostat_card_writepv)
            t = C.read_temperature()
            if ( (t > 5) and (t < 40)):
                print_success("OK:  cryostat card temperature = "+str(t))
            else:
                print_success("ERROR: cryostat card commmunication error, temperature = " + str(t), Status.FAIL)
                input("Fix cryostat card cables, enter 0 to continue, inlucing recheck of cryostat card");
                smurf_problem = True
                continue
        except: 
            print_success("ERROR: can't connect to cryostat card PVs",Status.FAIL)
            smurf_problem = True
#miscelaneous setup stuff (check if in pysmurf)
            
#DAC registers
        if (smurf_problem == False):
            for d in range(0,1): # over dacs
                for n in range(0, len(dac_nums)):
                    pv = dac_base_pv + "DAC["+ str(d) + ']:DacReg['+str(dac_nums[n])+']'
                    tmp = epics.caget(pv)
                    if tmp == dac_vals[n]:
                        print_success("OK: pv" + str(pv) + " = " + str(tmp) + "OK")
                    else:
                        print_success("ERROR, dac pv " + str(pv) + "= " + str(tmp) + "should be" + str(dac_vals[n]) + "will reset card",Status.FAIL) 
                        smurf_problem = True

    if smurf_problem:  # OK go through full restart procedure
        print_success("ERROR: system failed a test above, will reboot / retry",Status.FAIL)
        #kill smurf
        print("pidfile = ", pidfile)
        try:
            f = open(pidfile)
            a = f.read() 
            print("killing process pid = ", a);
            os.system("kill "+a) # killing process
            time.sleep(1) # wait for it to die
        except:
            print_success('Note: no pidfile, this is not an error',Status.WARN)

        # reboot the smurf card
        print("rebooting smurf card, wait %d seconds"%(wait_after_deactivate+wait_after_activate))
        os.system("fru_deactivate %s/%d"%(crate_ip,smurf_slot_id))
        print("wait %d seconds"%(wait_after_deactivate))
        time.sleep(wait_after_deactivate)
        print("reactivating card")
        os.system("fru_activate %s/%d"%(crate_ip,smurf_slot_id))
        print("wait %d seconds for firmware load"%(wait_after_activate))
        time.sleep(wait_after_activate)
        print("done waiting, ready to retry")

    if (smurf_problem==False):
        if (rf_test_on==False):
           print("OK, system OK, no RF testing done, exiting")
           exit()
        #print("Starting RF test")           
        #[freq, diff, ratio] = rf_test.rf_test(rf_fmin, rf_fmax, rf_runs) #run rf testing
        #rmin = min(ratio)
        #if rmin > rf_min_ratio:
        #    print("OK: RF OK (basic functinoal test only)")
        #    print("INSTRUCTION: check flux ramp monitor on scope, should be 4KHz, 50% amlitude")
        #    print("If a spectrum analyzer is attached, a tone comb shoudl be on")
        #    tmp = input("INPUT: enter 1 if flux ramp and tone comb OK to exit test, 0 to retry")
        #    if tmp:
        #        print("OK: system checked out")
        #        exit()
        #    else:
        #        print("ERROR: Flux ramp bad, continue restarting") 
        #        smurf_problem = True
        else:
            print_success("RF not operaging properly, line ratio too small, trying retest",Status.FAIL)
            smurf_problem = True
print_success("ERROR: problem not resolved",Status.FAIL)
print("Reboot smurf server (smurf-server) and try again, soometimes this fixes things")
        
        
