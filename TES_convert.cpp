//////////////////////////////////////////////////////////////////////////////
// This file is part of 'smurftestapps'.
// It is subject to the license terms in the LICENSE.txt file found in the 
// top-level directory of this distribution and at: 
//    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
// No part of 'smurftestapps', including this file, 
// may be copied, modified, propagated, or distributed except according to 
// the terms contained in the LICENSE.txt file.
//////////////////////////////////////////////////////////////////////////////
// TES_convert.ccp
#include <stdio.h>
#include <stdint.h>

typedef uint32_t uint;
uint32_t set_byte(uint32_t dat, uint8_t byte, uint n);
uint8_t get_byte(uint32_t dat, uint n);

int main()
{
  FILE *fp;
  uint32_t indat[12];
  uint32_t outdat[16];
  uint inword=0;
  uint inbyte=0;
  uint outword=0;
  uint outbyte=0;
  uint j;
  fp = fopen("test.dat", "r");
  if (!fp)
    {
      printf("couldn't open file \n");
      return(0);
    }
  for(j = 0; j < 12; j++) fscanf(fp, "%d", indat+j);
  for ( j = 0; j < 16; j++) outdat[j] = 0;  // clear
  while(1)
    {
      outdat[outword] = set_byte(outdat[outword], get_byte(indat[inword], inbyte), outbyte);  // all the work is here
      printf("inw=%8x, inb=,%8x, outw=%8x, outb=%8x, byt = %3x, indat=%8x, outdat=%8x \n", inword, inbyte, outword, outbyte,
	     get_byte(indat[inword], inbyte), indat[inword], outdat[outword]);
      inbyte++;
      outbyte++;
      if (inbyte >= 4)
	{
	  inbyte = 0;
	  inword++;
	}
      if (outbyte >= 3)
	{
	  outbyte = 0;
	  outword++;
	}
      if ((inword >=12) || (outword >= 16)) break;
    }
  for(j = 0; j < 16; j++)
    {
      printf("%d \n", outdat[j] - 0x8fffff);
    }
}

uint8_t get_byte(uint32_t dat, uint n)
{
  return((dat & (0xff << (8*n))) >>(8 * n)); 
}

uint32_t set_byte(uint32_t dat, uint8_t byte, uint n)
{
  uint32_t mask, tmp;
  mask = 0xFFFFFFFF - (0xff << (8 * n));
  tmp = (dat & mask) + (byte << (8*n));
  return(tmp);
}
