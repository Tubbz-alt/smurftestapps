// extracts data from saved data files
// inputs: input_filename, output_filename, first channel, second channel

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
typedef uint32_t uint;


const uint buffsize = 100000; // arbitrary for now.
const uint header_length = 128; // nubmer of bytes in header
const uint header_channel_offset = 4;  // bytes

int main(int argc, char *argv[])
{
  char infilename[256];
  char outfilename[256];
  uint first_channel;
  uint last_channel;
  int fdin, fdout; // File descriptors
  int mode;  // defaults to text output
  char *buffer;
  uint32_t num_channels;  // from header, number of channels in data
  buffer = malloc(buffsize * sizeof(char)); 
  strcpy(infilename, "data.dat");
  strcpy(outfilename, "outfile.dat");
  first_channel = 0;
  last_channel = 0;
  mode = text; // default
  
  if(argc > 1) strcpy(infilename, argv[1]);
  if(argc > 2) strcpy(outfilename, argv[2]);
  if(argc > 3)
    {
      first_channel = strtol(argv[3], NULL, 10);
      last_channel = first_channel;
    }
  if(argc > 4) last_channel = strtol(argv[4], NULL, 10);
  if(!(fdin = open(infilename, O_RDONLY))) return(0);
  if(!(fdout = open(outfilename, O_WRONLY))) return(0);

  read(fdin, buffer, header_length); // read first header (will assume all ar the same
  close(fdin); // ugly way to rewind -must be a better way
  (!(fdin = open(infilename, O_RDONLY))) return(0); // now open again. (really dumb)
  num_channels = (uint32_t) *(buffer + header_channel_offset); // sets read block size
  
  if (fdin) close(fdin);
  if (fdout) close(fdout);
  
}

