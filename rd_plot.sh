#!/bin/bash
set -e

if [ -n "$IMAGE" ]; then
  IMAGE="$IMAGE-"
fi

if [ $# == 0 ]; then
  echo "usage: IMAGE=<prefix> $0 *.out"
  exit 1
fi

if [ -z "$GNUPLOT" -a -n "`type -p gnuplot`" ]; then
  GNUPLOT=`type -p gnuplot`
fi
if [ ! -x "$GNUPLOT" ]; then
  echo "Executable not found GNUPLOT=$GNUPLOT"
  echo "Please install it or set GNUPLOT to point to an installed copy"
  exit 1
fi

CMDS="$CMDS set term png size 1024,768;"
CMDS="$CMDS set log x;"
CMDS="$CMDS set xlabel 'Bits/Pixel';"
CMDS="$CMDS set ylabel 'dB';"
CMDS="$CMDS set key bot right;"

for FILE in "$@"; do
  BASENAME=$(basename $FILE)
  DSSIM="$DSSIM $PREFIX '$FILE' using (\$3*8/\$2):3 with lines title '${BASENAME%.*} (DSSIM)'"
  RGBSSIM="$RGBSSIM $PREFIX '$FILE' using (\$3*8/\$2):4 with lines title '${BASENAME%.*} (RGB-SSIM'"
  PSNRHVS="$PSNRHVS $PREFIX '$FILE' using (\$3*8/\$2):5 with lines title '${BASENAME%.*} (PSNR-HVS-M)'"
  PREFIX=","
done

SUFFIX="dssim.png"
$GNUPLOT -e "$CMDS set output \"$IMAGE$SUFFIX\"; plot $DSSIM;"     2> /dev/null
SUFFIX="rgbssim.png"
$GNUPLOT -e "$CMDS set output \"$IMAGE$SUFFIX\"; plot $RGBSSIM;" 2> /dev/null
SUFFIX="psnrhvsm.png"
$GNUPLOT -e "$CMDS set output \"$IMAGE$SUFFIX\"; plot $PSNRHVSM;"  2> /dev/null

