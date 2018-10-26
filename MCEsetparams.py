#MCEsetparams.py
# used to write the pv to set up num rows etc in smurf2mce
import epics



def set_num_rows(epics_header = 'test_epics', num_rows = 33):
    epics_pv = epics_header + ':AMCc:FpgaTopLevel:AppTop:AppCore:TimingHeader:userConfig[2]'
    old = epics.caget(epics_pv)
    new = (old & 0xFFFF0000) + ((num_rows & 0xFFFF))
    epics.caput(epics_pv, new)  # write the value back

def set_num_rows_reported(epics_header = 'test_epics', num_rows_reported = 33):
    epics_pv = epics_header +':AMCc:FpgaTopLevel:AppTop:AppCore:TimingHeader:userConfig[2]'
    old = epics.caget(epics_pv)
    new = (old & 0x0000FFFF) + ((num_rows_reported & 0xFFFF) << 16)
    epics.caput(epics_pv, new)  # write the value back

def set_row_len(epics_header = 'test_epics', row_len = 60):
    epics_pv = epics_header +':AMCc:FpgaTopLevel:AppTop:AppCore:TimingHeader:userConfig[4]'
    old = epics.caget(epics_pv)
    new = (old & 0xFFFF0000) + ((row_len & 0xFFFF))
    epics.caput(epics_pv, new)  # write the value back

def set_data_rate(epics_header = 'test_epics', data_rate = 140):
    epics_pv = epics_header +':AMCc:FpgaTopLevel:AppTop:AppCore:TimingHeader:userConfig[4]'
    old = epics.caget(epics_pv)
    new = (old & 0x0000FFFF) + ((data_rate & 0xFFFF)<<16)
    epics.caput(epics_pv, new)  # write the value back
    
    
