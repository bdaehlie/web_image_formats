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
import time
import test_utils

def main(argv):
  if len(argv) != 3:
    test_utils.print_help()
    return

  jpeg_q = int(argv[1])
  png = argv[2]

  jpeg_results = test_utils.get_jpeg_results(png, jpeg_q)
  jpeg_ssim = jpeg_results[0]
  jpeg_file_size = jpeg_results[1]

  # Possible quality values so we can use an algorithm implementation that
  # only needs to deal with integer array indices.
  possible_q = []
  q = 0
  while q < 101:
    possible_q.append(q)
    q += 1

  webp_file_size = test_utils.find_file_size_for_ssim(test_utils.get_webp_results, png, possible_q, jpeg_ssim)

  ratio = float(webp_file_size) / float(jpeg_file_size)

  print "SSIM: " + str(jpeg_ssim)[:5]
  print "WebP_File_Size_(kb): %.1f" % (float(webp_file_size) / 1024.0)
  print "JPEG_File_Size_(kb): %.1f" % (float(jpeg_file_size) / 1024.0)
  print "WebP_to_JPEG_File_Size_Ratio: %.2f" % (ratio)

if __name__ == "__main__":
  main(sys.argv)
