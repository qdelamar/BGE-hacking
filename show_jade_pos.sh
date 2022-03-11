#!/bin/bash

if [[ "$1" =~ ^("help"|"h"|"-h"|"--help")$ ]]; then
  echo "Usage: either"
  echo "$0 --single      : shows the data once, or"
  echo "$0 [dt]          : watches the data every dt seconds (default=2s)"
  exit 0
fi

addr_x=0xb79dd8
addr_y=0xb79ddc
addr_z=0xb79de0

bin="bge.exe"

x_hex=$(readmem $bin $addr_x hex32)
y_hex=$(readmem $bin $addr_y hex32)
z_hex=$(readmem $bin $addr_z hex32)

x_flt=$(readmem $bin $addr_x float32)
y_flt=$(readmem $bin $addr_y float32)
z_flt=$(readmem $bin $addr_z float32)

if [[ "$1" =~ ^("--single")$ ]]; then
  echo -e "X @$addr_x\tY @$addr_y\tZ @$addr_z"
  echo -e "0x$x_hex\t0x$y_hex\t0x$z_hex"
  printf "%.7f\t%.7f\t%.7f" "$x_flt" "$y_flt" "$z_flt"
else
  dt=2
  if [ "$#" -eq 1 ]; then
    dt=$1
  fi
  watch -n $dt "$0 --single"
fi
