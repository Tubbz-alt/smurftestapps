#!/usr/bin/env python3

# checker program


import sys
import os
import epics
import time
import pysmurf
import cryostat_card
import rf_test

docstring = """ TEST"""

epics_base = 'test_epics:'
testapps_dir = '/usr/local/controls/Applications/smurf/smurftestapps/'

#parameters for RF testing
rf_fmin = 5010 # minimum test frequency 
rf_fmax = 5990 # maximum test frequency
rf_runs = 7 # number of test runs between frequencies
rf_min_ratio = 20  # minimum OK ration between desired line and other lines 

tmpfile = "/tmp/checkertmp"
config_file= "/usr/local/controls/Applications/smurf/smurf2mce/master/mcetransmit/smurf2mce.cfg"
pidfile = "/tmp/smurfpid"
rf_test_on = False  # assume no rf testing 
if len(sys.argv) >1:
    if (sys.argv[1].find('rftest') != -1):
        rf_test_on = True

if rf_test_on:
    print("Will do RF testing - be sure loopback is connected, and cryostat disconnecdted.  WARNING ctrl-C if not connected!!")
else:
    print("No RF testing")


pcie_pv_base = "SIOC:SMRF:ML00:AO" #A "Oh", not A "zero"
pcie_pv_offset = 100 # offset all pvs by this much
rssi_chan = 0   # for card #2

timestamp0_pv = epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:TimingHeader:timestamp[0]"
mceData_pv = epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:TimingHeader:mceData"

rate_select_pv = epics_base+"AMCc:FpgaTopLevel:AmcCarrierCore:AmcCarrierTiming:EvrV2CoreTriggers:EvrV2ChannelReg[0]:RateSel"
rate_def_pv = "TPG:SMRF:1:FIXEDDIV"

set_defaults_pv = epics_base+"AMCc:setDefaults"

cryostat_card_readpv =  epics_base + "AMCc:FpgaTopLevel:AppTop:AppCore:RtmCryoDet:SpiCryo:read"
cryostat_card_writepv = epics_base + "AMCc:FpgaTopLevel:AppTop:AppCore:RtmCryoDet:SpiCryo:write" 

timing_dest_select_pv = epics_base+"AMCc:FpgaTopLevel:AmcCarrierCore:AmcCarrierTiming:EvrV2CoreTriggers:EvrV2ChannelReg[0]:DestSel"

global_enable_pv = epics_base+"AMCc:enable"

# pvs used in setup
mispv = []
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:SysgenCryo:Base[1]:iqSwapIn")
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:SysgenCryo:Base[1]:iqSwapOut" )
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:SysgenCryo:Base[1]:refPhaseDelay")    
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:SysgenCryo:Base[1]:refPhaseDelayFine")
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:SysgenCryo:Base[1]:toneScale") 
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:SysgenCryo:Base[1]:analysisScale")
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:SysgenCryo:Base[1]:feedbackEnable")  
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:SysgenCryo:Base[1]:feedbackGain")
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:SysgenCryo:Base[1]:lmsGain")
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:SysgenCryo:Base[1]:digitizerFrequencyMHz")
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:SysgenCryo:Base[1]:bandCenterMHz")
mispv.append(epics_base+"AMCc:FpgaTopLevel:AppTop:AppCore:SysgenCryo:Base[1]:numberSubBands")
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

print("Note: Power cycle smurf card to put in known state, wait 70 seconds")
os.system("fru_deactivate 10.0.1.30/2")
time.sleep(5)
os.system("fru_activate 10.0.1.30/2")
time.sleep(45)



for trial in range(0,4):  # make 4 attempts to get smurf working
    print("Note: trial number = ", trial)


    smurf_problem = False 
    # check on pcie card
    a = cmdrun("/sbin/lspci")
    b = a.find("SLAC")
    if (b < 0):
        print("ERROR: PCIE card not running, Restart compter as shown below")
        print("INSTRUCTION: become root then shutdown now -r")
        exit()
    print("OK: PCIE card running")

    #is timing running
    a = cmdrun("screen -list")
    b = a.find("ts01")
    if (b < 0):
        print("ERROR: ts01 timign service not running, restarting")
        os.system("sudo service sioc-smrf-ts01 restart")
        continue
    else:
        print("OK: ts01 timing service is running")
    b = a.find("ml00")
    if (b < 0):
        print("ml00 epics service not running")
        os.system("sudo service sioc-smrf-ml00 restart")
        continue
    else:
        print("OK: ml00 service is running")

    # is pcie gui running?
    for j in range(0,3):
        ps_return = cmdrun("ps aux")
        b = ps_return.find("Pcie_checker.py")
        if(b < 0):
            print("Note: PCIE checker not running, will start")
            cmdrun(testapps_dir+"run_pcie_checker.sh")
            time.sleep(5) 
        else:
            print("OK: pcie checker already running"); 
            break
    if j >= 2:
        print("ERROR - FATAL unable to start pcie checker - giving up")
        exit()

    #check connection to MCE computer.
    with open(config_file, "r") as f:
        for line in f:
            x= line
            if len(x) == 0:
                print("Warning: couldn't find IP address in config file")
                break
            b = x.find("receiver_ip")
            if (b >= 0):
                c = x.split() # split into substrings
                ip = c[1]  # the ip address
                print("OK: receiver IP address in smurf2mce.cfg = ", ip)
                print("Note: check that IP address can be reached")
                a = cmdrun("ping -c1 " + ip)
                r = a.find("rtt") #only get this when ping returns
                if (r < 0):
                    print("ERROR: could not ping MCE computer, check connection")
                    print("fix networking, then restart this program")
                    exit()
                else:
                    print("OK, able to ping MCE computer")
                break

    try:
        #Run Smurf,  new copy will stop on old
        print("starting smurf in nogui mode, - may kill running copy, wait 90 seconds to start")
        os.system(testapps_dir+"run_smurf.sh")
        time.sleep(45)
        for j in range(0,3):
            ps_return = cmdrun("ps aux")
            b = ps_return.find("pyrogue_server.py")
            if (b < 0):
                print("Warning: SMURF still not running - starting")
                os.system(testapps_dir+"run_smurf.sh")
                print("waiting 45 seconds for smurf to start")
                time.sleep(45)
                print("done waiting fo smurf to start")
            else:
                print("OK: SMURF is running")
                break  
        if j >= 2:
            print("unable to start smurf")
            smurf_proble = True


        # check valid counts increment
        c1 = epics.caget(pcie_pv_base + str(pcie_pv_offset + rssi_chan))
        time.sleep(1)
        c2 = epics.caget(pcie_pv_base + str(pcie_pv_offset + rssi_chan))
        d = c2-c1
        if (d <= 0):
            print("ERROR:  RSSI link is not updating delta = ",d);
            smurf_problem = True
        else:
            print("OK: RSSI link updating, delta =", d)

        # enabele register polling
        print("enabling register polling")
        epics.caput(global_enable_pv, True)  # we normally leave this off to reduce dropped frames


        epics.caput(set_defaults_pv, 1)
        time.sleep(5)
      
        #check timing setup
        a = epics.caget(rate_def_pv)
        b = epics.caget(rate_select_pv) # which rate are we using
        rate = 480000.0 / a[b]
        if (b == 0):
            print("Note: Rate not initialized - rate 0 -> 48KHz, setting rate to 4KHz")
            epics.caput(rate_select_pv, 0x6) # select rate
        elif ((rate < 1000) or (rate > 8000)):
            print("Warning: flux ramp and frame rate = ", rate, "Hz probably out of range")
        else:
            print ("OK: Flux ramp and frame rate", rate, "Hz")
        b = epics.caget(timing_dest_select_pv)
        if (b != 0x20000):
            print("Note: mysterious timign destionation pv != 0x20000, got " , hex(b), " will fix")
            epics.caput(timing_dest_select_pv, 0x20000) 
        #check incrementing timing counters
        a1 = 0
        a2= 0  #kludge if pv is down. 
        a1 = epics.caget(timestamp0_pv) # high rate incrementing conter from timing
        time.sleep(0.1)
        a2 = epics.caget(timestamp0_pv)
        if ((a1-a2) == 0):
            print("Error: timing system fast counter not incrementing - probably smurf problem")
            smurf_problem = True
        else:
            print("OK: Timing system counter incrementing")

        a1 = [0]
        a2 = [0]
        a1 = epics.caget(mceData_pv) # syncbox number
        time.sleep(0.1)
        a2 = epics.caget(mceData_pv)  # returns a long array for some strange reason
        b = a1-a2
        mx = max(b)
        mn = min(b)

        if((mx == 0) and (mn ==0)):
            print("Note: MCE synword is not incremleenting - may be disabled by GCP")
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
                print("Could not read ", mispv[j])
                smurf_problem = True
                break  # end this loop, 
        except:
            smurf_problem = True
            print("Error: ", mispv[n], " returned error")
            break  # break out of loop
        print("OK, checkign ", mispv[n], " = ", x)
    if (smurf_problem == False):
        #try cryostat card
        try:
            C = cryostat_card.cryostat_card(cryostat_card_readpv, cryostat_card_writepv)
            t = C.read_temperature()
            if ( (t > 5) and (t < 40)):
                print("OK:  cryostat card temperature = ", t)
            else:
                print("ERROR: cryostat card commmunication error, temperature = ", t)
                input("Check cryostat card cables, enter 0 to continue");
                smurf_problem = True
                continue
        except: 
            print("ERROR: can't connect to cryostat card PVs")
            smurf_problem = True
#miscelaneous setup stuff (check if in pysmurf)
            
#DAC registers
        if (smurf_problem == False):
            for d in range(0,1): # over dacs
                for n in range(0, len(dac_nums)):
                    pv = dac_base_pv + "DAC["+ str(d) + ']:DacReg['+str(dac_nums[n])+']'
                    tmp = epics.caget(pv)
                    if tmp == dac_vals[n]:
                        print("OK: pv", pv, " = ", tmp, "OK")
                    else:
                        print("ERROR, dac pv ", pv, "= ", tmp, "should be", dac_vals[n],"will reset card") 
                        smurf_problem = True

    if smurf_problem:  # OK go through full restart procedure
        print("HOUSTON WE HAVE A PROBLEM - trying to fix")
        #kill smurf
        print("pidfile = ", pidfile)
        try:
            f = open(pidfile)
            a = f.read() 
            print("killing process pid = ", a);
            os.system("kill "+a) # killing process
            time.sleep(1) # wait for it to die
        except:
            print('no pidfile')

            # reboot the smurf card
        print("rebooting smurf card")
        os.system("fru_deactivate 10.0.1.30/2")
        print("wait 10 seconds")
        time.sleep(5)
        print("reactiviting card")
        os.system("fru_activate 10.0.1.30/2")
        print("wait 1 minute for firmware load")
        time.sleep(45)
        print("done wating, ready to retry")
    if (smurf_problem==False):
        if (rf_test_on==False):
           print("OK, system OK, no RF testing done, exiting")
           exit()
        print("Starting RF test")
   #     try:
        [freq, diff, ratio] = rf_test.rf_test(rf_fmin, rf_fmax, rf_runs) #run rf testing
    #    except: 
    #        print("ERROR: RF test threw exception - trying restart")
    #        smurf_problem = True
    #        continue
        rmin = min(ratio)
        if rmin > rf_min_ratio:
            print("OK: RF OK (basic functinoal test only)")
            print("INSTRUCTION: check flux ramp monitor on scope, should be 4KHz, 50% amlitude")
            print("If a spectrum analyzer is attached, a tone comb shoudl be on")
            tmp = input("INPUT: enter 1 if flux ramp and tone comb OK to exit test, 0 to retry")
            if tmp:
                print("OK: system checked out")
                exit()
            else:
                print("ERROR: Flux ramp bad, continue restarting") 
                smurf_problem = True
        else:
            print("RF not operaging properly, line ratio too small, trying retest")
            smurf_problem = True
print("ERROR: problem not resolved")
print("Reboot smurf server (smurf-srv03) and try again, soometimes this fixes things")
        
        
