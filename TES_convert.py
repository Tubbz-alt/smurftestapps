# takes 32 X 20 bit TES data, converts to packed 12X64 bit.

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
    return ( 0xffffff & tmp3) # limit to 24 bit

for j in range (0, 16): # should pull from PV
    tesp[j] =j # testing only
    tesn[j] =0 # testing only
    
n = 0   #output word number
m = 0 # input word number
b = 0  # byte in intput word
r = 0 # byte in output word
outx = [0]*12  # 12 output words for 16 input words

    
for j in range(0, 16):
    sub[j] = ( 0xFFFFF  & (tesp[j] - tesn[j]))
  
    
while 1:
    outx[n] = set_byte(outx[n], get_byte(sub[m], b), r) # everythign happens here
    print('m = ', m, 'b = ', b, 'n = ', n, 'r = ', r, 'byte = ', get_byte(sub[m], b))
    b = b + 1
    r = r + 1
    if b == 6:
        b = 0
        m = m + 1
    if r == 8:
        r = 0
        n = n + 1
    if (m == 16) or (n== 12):   #done
        break

