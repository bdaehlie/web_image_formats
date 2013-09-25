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

import sys
import subprocess

def main(argv):
  if len(argv) < 4:
    print "Arg 1: format to test (e.g. 'hevc', 'webp', or 'jxr')."
    print "Arg 2: image quality test to use (e.g. 'yssim', rgbssim', 'iwssim', or 'psnrhvs')"
    print "Arg 3: JPEG quality value to test (e.g. '75')."
    print "All further arguments are file paths to images to test (e.g. 'images/Lenna.png')."
    print "There must be at least one image given."
    print "Output is four lines: quality score, tested format file size, JPEG file size, and tested format to JPEG file size ratio."
    print "This is the arithmetic average of results from all images."
    print "Output labels have no spaces so that a string split on a line produces the numeric result at index 1."
    return

  format_name = argv[1]
  quality_test = argv[2]
  jpeg_q = int(argv[3])
  test_images = argv[4:]

  score_total = 0.0
  jpeg_file_size_total = 0.0 # This is in KB
  tformat_file_size_total = 0.0 # This is in KB
  for i in test_images:
    cmd = ["./compression_test.py", format_name, quality_test, str(jpeg_q), i]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = proc.communicate()
    if proc.returncode != 0:
      sys.stderr.write(err)
      sys.stderr.write("Subprocess returned with failure status, aborting!\n")
      sys.exit(proc.returncode)
    lines = output.splitlines(False)
    try:
      i = 0
      for line in lines:
        s = line.split()
        if i == 0:
          score_total += float(s[1])
        if i == 1:
          tformat_file_size_total += float(s[1])
        if i == 2:
          jpeg_file_size_total += float(s[1])
        i += 1
    except ValueError:
      sys.stderr.write(output)
      sys.stderr.write("Unexpected output from subprocess, aborting!\n")
      sys.exit(1)

  avg_score = score_total / float(len(test_images))
  avg_tformat_file_size = tformat_file_size_total / float(len(test_images))
  avg_jpeg_file_size = jpeg_file_size_total / float(len(test_images))

  ratio = avg_tformat_file_size / avg_jpeg_file_size

  print "avg_%s: %s" % (quality_test, str(avg_score)[:5])
  print "avg_%s_file_size_(kb): %.1f" % (format_name, avg_tformat_file_size)
  print "avg_jpeg_file_size_(kb): %.1f" % (avg_jpeg_file_size)
  print "%s_to_jpeg_file_size_ratio: %.2f" % (format_name, ratio)

if __name__ == "__main__":
  main(sys.argv)
