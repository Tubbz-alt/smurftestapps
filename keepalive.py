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
    
