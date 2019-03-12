#!/bin/bash

PARAMS=""

while (( "$#" )); do
  case "$1" in
    -t|--transmitdir)
      TRANSMITDIR=$2
      shift 2
      ;;
    -m|--shm)
      SHELFMANAGER="-m $2"
      shift 2
      ;;
    -c|--crateid)
      CRATEID="-c $2"
      shift 2
      ;;
    -s|--smurfslot)
      SMURFSLOT="-s $2"
      shift 2
      ;;
    -r|--epics-root)
      EPICS_ROOT="-r $2"
      shift 2
      ;;
    -p|--pyrogue)
      PYROGUE="-t $2"
      shift 2
      ;;
    -y|--defaults)
      DEFAULTS_YML="-y $2"
      shift 2
      ;;
    --nogui)
      NOGUI="--nogui"
      shift 1
      ;;
    -e)
      INTERFACE="-e"
      shift 1
      ;;
    --) # end argument parsing
      shift
      break
      ;;
    -*|--*=) # unsupported flags
      echo "Error: Unsupported flag $1" >&2
      exit 1
      ;;
    *) # preserve positional arguments
      PARAMS="$PARAMS $1"
      shift
      ;;
  esac
done

if [ -z "$TRANSMITDIR" ]
  then
    echo "ERROR: Must provide a path to the transmitter directory."
    echo "INSTRUCTION: Provide path to transmitter directory with -t option."
    echo "             e.g. $0 -t /usr/local/controls/Applications/smurf/smurf2mce/current/mcetransmit"
    exit
fi

cd $TRANSMITDIR
#nohup ./smurf_run.sh $SHELFMANAGER $CRATEID $SMURFSLOT $NOGUI > /dev/null &
echo ./smurf_run.sh $SHELFMANAGER $CRATEID $SMURFSLOT $NOGUI $INTERFACE $PYROGUE $DEFAULTS_YML $EPICS_ROOT
./smurf_run.sh $SHELFMANAGER $CRATEID $SMURFSLOT $NOGUI $INTERFACE $PYROGUE $DEFAULTS_YML $EPICS_ROOT
