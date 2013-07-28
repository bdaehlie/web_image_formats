#!/usr/bin/python
# Written by Josh Aas, Mozilla Corporation
# License: Do whatever you want with the code.

import os
import sys
import time
import math
import test_utils

# Returns an SSIM value and a file size
def get_jxr_results(in_png, jxr_q):
  tmp_file_base = test_utils.path_for_file_in_tmp(in_png)
  jxr = tmp_file_base + str(jxr_q) + ".jxr"
  test_utils.png_to_jxr(in_png, jxr_q, jxr)
  jxr_png = jxr + ".png"
  test_utils.jxr_to_png(jxr, jxr_png)
  ssim = test_utils.ssim_float_for_images(in_png, jxr_png)
  file_size = os.path.getsize(jxr)
  os.remove(jxr)
  os.remove(jxr_png)
  return (ssim, file_size)

def main(argv):
  if len(argv) < 2:
    print "First arg is a JPEG quality value to test (e.g. '75')."
    print "Second arg is the path to an image to test (e.g. 'images/Lenna.png')."
    print "Output is four lines: SSIM, JPEG-XR file size, JPEG file size, and JPEG-XR to JPEG file size ratio."
    print "Output labels have no spaces so that a string split on a line produces the numeric result at index 1."
    return

  jpeg_q = int(argv[1])
  png = argv[2]

  jpeg_results = test_utils.get_jpeg_results(png, jpeg_q)
  jpeg_ssim = jpeg_results[0]
  jpeg_file_size = jpeg_results[1]

  # Possible quality values so we can use an algorithm implementation that
  # only needs to deal with integer array indices.
  possible_q = []
  q = 0.0
  while q < 1.0:
    possible_q.append(q)
    q += 0.01

  low_index = -1
  low_results = (0.0, 0)
  high_index = len(possible_q)
  high_results = (0.0, 0)
  while (high_index - low_index) > 1:
    i = int(math.floor((float(high_index - low_index) / 2.0)) + low_index)
    jxr_results = get_jxr_results(png, possible_q[i])
    jxr_ssim = jxr_results[0]
    jxr_file_size = jxr_results[1]
    if jxr_ssim == jpeg_ssim:
      low_index = high_index = i
      low_results = high_results = jxr_results
      break;
    if jxr_ssim < jpeg_ssim:
      low_index = i
      low_results = jxr_results
    if jxr_ssim > jpeg_ssim:
      high_index = i
      high_results = jxr_results

  if low_index == -1 or high_index == len(possible_q):
    sys.stderr.write("Failure: Unsuccessful binary search!\n")
    sys.exit(1)

  # Calculate file size via interpolation.
  jxr_file_size = test_utils.file_size_interpolate(high_results[0], low_results[0], jpeg_ssim, high_results[1], low_results[1])

  ratio = float(jxr_file_size) / float(jpeg_file_size)

  print "SSIM: " + str(jpeg_ssim)[:5]
  print "JPEG-XR_File_Size_(kb): %.1f" % (float(jxr_file_size) / 1024.0)
  print "JPEG_File_Size_(kb): %.1f" % (float(jpeg_file_size) / 1024.0)
  print "JPEG-XR_to_JPEG_File_Size_Ratio: %.2f" % (ratio)

if __name__ == "__main__":
  main(sys.argv)
