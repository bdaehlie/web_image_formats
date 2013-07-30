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
    print "First arg is the name of a supported format to test (e.g. 'hevc' or 'webp')."
    print "Second arg is a JPEG quality value to test (e.g. '75')."
    print "All further arguments are file paths to images to test (e.g. 'images/Lenna.png')."
    print "There must be at least one image given."
    print "Output is four lines: SSIM, tested format file size, JPEG file size, and tested format to JPEG file size ratio."
    print "This is the arithmetic average of results from all images."
    print "Output labels have no spaces so that a string split on a line produces the numeric result at index 1."
    return

  format_name = argv[1]
  jpeg_q = int(argv[2])
  test_images = argv[3:]

  ssim_total = 0.0
  jpeg_file_size_total = 0.0 # This is in KB
  tformat_file_size_total = 0.0 # This is in KB
  for i in test_images:
    output = subprocess.Popen(["./compression_test.py", format_name, str(jpeg_q), i], stdout=subprocess.PIPE).communicate()[0]
    lines = output.splitlines(False)
    try:
      i = 0
      for line in lines:
        s = line.split()
        if i == 0:
          ssim_total += float(s[1])
        if i == 1:
          tformat_file_size_total += float(s[1])
        if i == 2:
          jpeg_file_size_total += float(s[1])
        i += 1
    except ValueError:
      sys.stderr.write(output)
      sys.stderr.write("Unexpected output from subprocess, aborting!\n")
      sys.exit(1)

  avg_ssim = ssim_total / float(len(test_images))
  avg_tformat_file_size = tformat_file_size_total / float(len(test_images))
  avg_jpeg_file_size = jpeg_file_size_total / float(len(test_images))

  ratio = avg_tformat_file_size / avg_jpeg_file_size

  print "Avg_SSIM: " + str(avg_ssim)[:5]
  print "Avg_Tested_Format_File_Size_(kb): %.1f" % (avg_tformat_file_size)
  print "Avg_JPEG_File_Size_(kb): %.1f" % (avg_jpeg_file_size)
  print "Tested_Format_to_JPEG_File_Size_Ratio: %.2f" % (ratio)

if __name__ == "__main__":
  main(sys.argv)
