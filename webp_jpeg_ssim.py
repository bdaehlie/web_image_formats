#!/usr/bin/python
# Written by Josh Aas, Mozilla Corporation
# License: Do whatever you want with the code.

import os
import sys
import time
import math
import test_utils

# Returns an SSIM value and a file size
def get_webp_results(in_png, webp_q):
  tmp_file_base = test_utils.path_for_file_in_tmp(in_png)
  webp = tmp_file_base + str(webp_q) + ".webp"
  test_utils.png_to_webp(in_png, webp_q, webp)
  webp_png = webp + ".png"
  test_utils.webp_to_png(webp, webp_png)
  ssim = test_utils.ssim_float_for_images(in_png, webp_png)
  file_size = os.path.getsize(webp)
  os.remove(webp)
  os.remove(webp_png)
  return (ssim, file_size)

def main(argv):
  if len(argv) < 2:
    print "First arg is a JPEG quality value to test (e.g. '75')."
    print "Second arg is the path to an image to test (e.g. 'images/Lenna.jpg')."
    print "Output is four lines: SSIM, WebP file size, JPEG file size, and WebP to JPEG file size ratio."
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
  q = 0
  while q < 101:
    possible_q.append(q)
    q += 1

  low_index = -1
  low_results = (0.0, 0)
  high_index = len(possible_q)
  high_results = (0.0, 0)
  while (high_index - low_index) > 1:
    i = int(math.floor((float(high_index - low_index) / 2.0)) + low_index)
    webp_results = get_webp_results(png, possible_q[i])
    webp_ssim = webp_results[0]
    webp_file_size = webp_results[1]
    if webp_ssim == jpeg_ssim:
      low_index = high_index = i
      low_results = high_results = webp_results
      break;
    if webp_ssim < jpeg_ssim:
      low_index = i
      low_results = webp_results
    if webp_ssim > jpeg_ssim:
      high_index = i
      high_results = webp_results

  # See 'hevc_tecnick_034_situation.txt' for explanation of the
  # following code.
  if low_index == -1:
    if (high_results[0] - jpeg_ssim) < 0.001:
      low_results = high_results
    else:
      sys.stderr.write("Failure: Unsuccessful binary search!\n")
      sys.exit(1)
  if high_index == len(possible_q):
    if (jpeg_ssim - low_results[0]) < 0.001:
      high_results = low_results
    else:
      sys.stderr.write("Failure: Unsuccessful binary search!\n")
      sys.exit(1)

  webp_file_size = test_utils.file_size_interpolate(high_results[0], low_results[0], jpeg_ssim, high_results[1], low_results[1])

  ratio = float(webp_file_size) / float(jpeg_file_size)

  print "SSIM: " + str(jpeg_ssim)[:5]
  print "WebP_File_Size_(kb): %.1f" % (float(webp_file_size) / 1024.0)
  print "JPEG_File_Size_(kb): %.1f" % (float(jpeg_file_size) / 1024.0)
  print "WebP_to_JPEG_File_Size_Ratio: %.2f" % (ratio)

if __name__ == "__main__":
  main(sys.argv)
