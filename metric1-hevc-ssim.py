#!/usr/bin/python
#
# Copyright 2010 Google Inc.
#
# This code is licensed under the same terms as WebM:
#  Software License Agreement:  http://www.webmproject.org/license/software/
#  Additional IP Rights Grant:  http://www.webmproject.org/license/additional/
# -----------------------------------------------------------------------------
# Modified by Josh Aas, Mozilla Corporation

import os
import sys
import time
import test_utils

def main(argv):
  png = argv[1]
  tmp_file_base = test_utils.tmpdir + os.path.basename(png)

  # Quality values we're interested in. This is essentially an optimization
  # to avoid working on every one.
  quality_values = [50, 55, 60, 65, 70, 75, 80, 85, 90, 95]

  # These lists will have one entry per quality value we're testing.
  jpeg_ssim_values = []
  jpeg_file_sizes = []

  # Each list will be 100 entries long, one for each quality option.
  hevc_ssim_values = []
  hevc_file_sizes = []

  # Calculate SSIM and file size for all JPEG quality levels.
  for q in quality_values:
    jpg = tmp_file_base + str(q) + ".jpg"
    test_utils.png_to_jpeg(png, q, jpg)
    jpeg_file_sizes.append(os.path.getsize(jpg))
    jpg_png = jpg + ".png"
    test_utils.jpeg_to_png(jpg, jpg_png)
    jpeg_ssim_values.append(test_utils.ssim_float_for_images(png, jpg_png))
    os.remove(jpg)
    os.remove(jpg_png)

  # Calculate SSIM and file size for all hevc quality levels.
  i = 0
  while i < 100:
    q = i + 1
    hevc = tmp_file_base + str(q) + ".hevc"
    test_utils.png_to_hevc(png, q, hevc)
    #XXX To-do: Penalize hevc files for just being bitstreams with not containers
    hevc_file_sizes.append(os.path.getsize(hevc))
    hevc_png = hevc + ".png"
    test_utils.hevc_to_png(hevc, hevc_png)
    hevc_ssim_values.append(test_utils.ssim_float_for_images(png, hevc_png))
    os.remove(hevc)
    os.remove(hevc_png)
    i += 1

  # For each quality value we're interested in, calculate the size of a
  # hevc file that is equivalent to the JPEG file via interpolation.
  hevc_ssim_equiv_file_sizes = []
  for s in jpeg_ssim_values:
    interpolated = test_utils.interpolate(hevc_ssim_values, s, hevc_file_sizes)
    hevc_ssim_equiv_file_sizes.append(interpolated)

  jpeg_total_size = 0
  for fs in jpeg_file_sizes:
    jpeg_total_size += fs

  hevc_total_size = 0
  for fs in hevc_ssim_equiv_file_sizes:
    hevc_total_size += fs

  print "File size change from JPEG to hevc at equivalent SSIM: " + str(float(hevc_total_size) / float(jpeg_total_size))[:5]

if __name__ == "__main__":
  main(sys.argv)
