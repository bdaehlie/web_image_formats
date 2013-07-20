#!/usr/bin/python
# Written by Josh Aas, Mozilla Corporation
# License: Do whatever you want with the code.

import os
import sys
import time
import math
import test_utils

# Returns an SSIM value and a file size
def get_hevc_results(in_png, hevc_q):
  tmp_file_base = test_utils.path_for_file_in_tmp(in_png)
  hevc = tmp_file_base + str(hevc_q) + ".hevc"
  hevc_yuv = hevc + ".yuv"
  test_utils.png_to_hevc(in_png, hevc_q, hevc, hevc_yuv)
  hevc_png = hevc + ".png"
  test_utils.hevc_yuv_to_png(hevc_yuv, test_utils.get_png_width(in_png), test_utils.get_png_height(in_png), hevc_png)
  ssim = test_utils.ssim_float_for_images(in_png, hevc_png)
  file_size = os.path.getsize(hevc)
  file_size += 80 # Penalize HEVC bit streams for not having a container like
                  # other formats do. Came up with this number because a
                  # 1x1 pixel hevc file is 84 bytes.
  os.remove(hevc)
  os.remove(hevc_yuv)
  os.remove(hevc_png)
  return (ssim, file_size)

def main(argv):
  if len(argv) < 2:
    print "First arg is a JPEG quality value to test (e.g. '75')."
    print "Second arg is the path to an image to test (e.g. 'images/Lenna.jpg')."
    print "Output is four lines: SSIM, HEVC-P file size, JPEG file size, and HEVC-P to JPEG file size ratio."
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
  q = 50
  while q >= 0.0:
    possible_q.append(q)
    q -= 0.5

  low_index = -1
  low_results = (0.0, 0)
  high_index = len(possible_q)
  high_results = (0.0, 0)
  while (high_index - low_index) > 1:
    i = int(math.floor((float(high_index - low_index) / 2.0)) + low_index)
    hevc_results = get_hevc_results(png, possible_q[i])
    hevc_ssim = hevc_results[0]
    hevc_file_size = hevc_results[1]
    if hevc_ssim == jpeg_ssim:
      low_index = high_index = i
      low_results = high_results = hevc_results
      break;
    if hevc_ssim < jpeg_ssim:
      low_index = i
      low_results = hevc_results
    if hevc_ssim > jpeg_ssim:
      high_index = i
      high_results = hevc_results

  if low_index == -1 or high_index == len(possible_q):
    sys.stderr.write("Failure: Unsuccessful binary search!\n")
    sys.exit(1)

  # Calculate file size via interpolation.
  hevc_file_size = test_utils.file_size_interpolate(high_results[0], low_results[0], jpeg_ssim, high_results[1], low_results[1])

  ratio = float(hevc_file_size) / float(jpeg_file_size)

  print "SSIM: " + str(jpeg_ssim)[:5]
  print "HEVC-P_File_Size_(kb): %.1f" % (float(hevc_file_size) / 1024.0)
  print "JPEG_File_Size_(kb): %.1f" % (float(jpeg_file_size) / 1024.0)
  print "HEVC-P_to_JPEG_File_Size_Ratio: %.2f" % (ratio)

if __name__ == "__main__":
  main(sys.argv)
