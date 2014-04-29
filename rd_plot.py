#!/usr/bin/python
# Written by Josh Aas
# Copyright (c) 2013, Mozilla Corporation
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the Mozilla Corporation nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import os
import sys
import subprocess
import shlex

def run_silent(cmd):
  FNULL = open(os.devnull, 'w')
  rv = subprocess.call(shlex.split(cmd), stdout=FNULL, stderr=FNULL)
  if rv != 0:
    sys.stderr.write("Failure from subprocess:\n")
    sys.stderr.write("\t" + cmd + "\n")
    sys.stderr.write("Aborting!\n")
    sys.exit(rv)
  return rv

def main(argv):
  if len(argv) < 3:
    print "Arg 1: Base name for graph files"
    print "Arg 2+: Paths to '*.out' files"
    return

  base_name = argv[1]
  data_files = argv[2:]

  proc = subprocess.Popen("type -p gnuplot", stdout=subprocess.PIPE, shell=True)
  out, err = proc.communicate()
  gnuplot = out.strip()
  if not gnuplot:
    print "gnuplot not found, please install it"
    return

  base_cmds = ("set term png size 1024,768; set log x; set xlabel 'Bits/Pixel'; set key bot right;")

  yssim = "%s -e \"%s set ylabel 'Quality (yssim)'; set output '%s-yssim.png'; plot " % (gnuplot, base_cmds, base_name)
  dssim = "%s -e \"%s set ylabel 'Quality (dssim)'; set output '%s-dssim.png'; plot " % (gnuplot, base_cmds, base_name)
  rgbssim = "%s -e \"%s set ylabel 'Quality (rgbssim)'; set output '%s-rgbssim.png'; plot " % (gnuplot, base_cmds, base_name)
  psnrhvsm = "%s -e \"%s set ylabel 'Quality (psnrhvsm)'; set output '%s-psnrhvsm.png'; plot " % (gnuplot, base_cmds, base_name)

  prefix = ""
  for file in data_files:
    data_label = os.path.splitext(os.path.basename(file))[0]
    yssim += "%s'%s' using ($2*8/$1):3 with lines title '%s'" % (prefix, file, data_label)
    dssim += "%s'%s' using ($2*8/$1):4 with lines title '%s'" % (prefix, file, data_label)
    rgbssim += "%s'%s' using ($2*8/$1):5 with lines title '%s'" % (prefix, file, data_label)
    psnrhvsm += "%s'%s' using ($2*8/$1):6 with lines title '%s'" % (prefix, file, data_label)
    prefix = ", "

  yssim += ";\""
  run_silent(yssim)
  dssim += ";\""
  run_silent(dssim)
  rgbssim += ";\""
  run_silent(rgbssim)
  psnrhvsm += ";\""
  run_silent(psnrhvsm)

if __name__ == "__main__":
  main(sys.argv)
