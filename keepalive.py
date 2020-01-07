##############################################################################
## This file is part of 'smurftestapps'.
## It is subject to the license terms in the LICENSE.txt file found in the 
## top-level directory of this distribution and at: 
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
## No part of 'smurftestapps', including this file, 
## may be copied, modified, propagated, or distributed except according to 
## the terms contained in the LICENSE.txt file.
##############################################################################

# test routine to keep link open
import time
import datetime
j = 0
while 1:
    j = j + 1
    print(datetime.datetime.now())
    time.sleep(2)
    if  99 == (j%100):
        print("all work and no play makes jack a dull boy")
    
