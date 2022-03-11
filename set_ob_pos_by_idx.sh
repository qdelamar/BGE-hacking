#!/bin/bash

#peyj seems to be at idx=0
#jade seems to be at 2/3 depending on loading.. depends on peyj being there or not, and probably other contextual parameters


if [[ "$1" =~ ^("help"|"h"|"-h"|"--help")$ ]] || [ "$#" -ne 4 ]; then
  echo "Usage: $0 idx [x] [y] [z]"
  echo " use a dot '.' to avoid changing a component of the position"
  echo " ex:"
  echo "$0 2 4.2 . 0.2      : will set x=4.2 and z=0.2, letting y unchanged for obj 2"
  echo "$0 0 . -5.6 .       : will set y=-5.6 and let x and z unchanged for obj 0"
  echo "                                                -qdelamar 2020-04"
  exit 0
fi

idx=$1

#be sure to break after the game determines itself the position so that we overwrite it irrevocably:
cmd='sudo gdb -p $(pidof bge.exe) --batch-silent '
cmd="$cmd -ex \"b*0x46358d\""
cmd="$cmd -ex \"c\""

#then set the components of the position:
u=0
if [[ "$2" =~ ^(".")$ ]]; then
 echo "x unchanged"
 u=$(($u+1))
else
  cmd="$cmd -ex \"set *(float*)((*((*((*(*((*((*(0x1458228+0x168))+8*$idx))+0x18)))+4))+0x20))+0x30)=(float)$2\""
fi
if [[ "$3" =~ ^(".")$ ]]; then
 echo "y unchanged"
 u=$(($u+1))
else
  cmd="$cmd -ex \"set *(float*)((*((*((*(*((*((*(0x1458228+0x168))+8*$idx))+0x18)))+4))+0x20))+0x34)=(float)$3\""
fi
if [[ "$4" =~ ^(".")$ ]]; then
 echo "z unchanged"
 u=$(($u+1))
else
  cmd="$cmd -ex \"set *(float*)((*((*((*(*((*((*(0x1458228+0x168))+8*$idx))+0x18)))+4))+0x20))+0x38)=(float)$4\""
fi

cmd="$cmd -ex 'q'"

if [ $u -le 2 ]; then
  eval $cmd
  echo "done"
else
  echo "nothing done"
fi

