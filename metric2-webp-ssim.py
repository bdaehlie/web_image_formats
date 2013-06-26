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
  webp_ssim_values = []
  webp_file_sizes = []

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

  # Calculate SSIM and file size for all WebP quality levels.
  i = 0
  while i < 100:
    q = i + 1
    webp = tmp_file_base + str(q) + ".webp"
    test_utils.png_to_webp(png, q, webp)
    webp_file_sizes.append(os.path.getsize(webp))
    webp_png = webp + ".png"
    test_utils.webp_to_png(webp, webp_png)
    webp_ssim_values.append(test_utils.ssim_float_for_images(png, webp_png))
    os.remove(webp)
    os.remove(webp_png)
    i += 1

  # For each quality value we're interested in, calculate the size of a
  # WebP file that is equivalent to the JPEG file via interpolation.
  webp_ssim_equiv_file_sizes = []
  for s in jpeg_ssim_values:
    i = 0
    while i < 100:
      if webp_ssim_values[i] < s:
        if i == 99:
          webp_ssim_equiv_file_sizes.append(webp_file_sizes[99])
          break;
      if webp_ssim_values[i] == s:
        webp_ssim_equiv_file_sizes.append(webp_file_sizes[i])
        break
      if webp_ssim_values[i] > s:
        if i == 0:
          webp_ssim_equiv_file_sizes.append(webp_file_sizes[0])
          break
        webp_diff = webp_ssim_values[i] - webp_ssim_values[i - 1]
        if webp_diff == 0:
          webp_ssim_equiv_file_sizes.append(webp_file_sizes[i])
          break;
        jpeg_diff = s - webp_ssim_values[i - 1]
        percent = jpeg_diff / webp_diff
        webp_fs_diff = webp_file_sizes[i] - webp_file_sizes[i - 1]
        interpolated = (webp_fs_diff * percent) + webp_file_sizes[i - 1]
        # print "JPEG SSIM: " + str(s)
        # print "WebP SSIM larger: " + str(webp_ssim_values[i]) + " WebP SSIM smaller: " + str(webp_ssim_values[i - 1])
        # print "WebP file size larger: " + str(webp_file_sizes[i]) + " WebP file size smaller: " + str(webp_file_sizes[i - 1])
        # print "Interpolated file size: " + str(interpolated)
        webp_ssim_equiv_file_sizes.append(interpolated)
        break;
      i += 1

  percent_improvement = 0
  i = 0
  while i < len(quality_values):
    percent_improvement += webp_ssim_equiv_file_sizes[i] / jpeg_file_sizes[i]
    i += 1

  print "Average percentage size of WebP to JPEG at equiv SSIM: " + str(percent_improvement / len(quality_values))

if __name__ == "__main__":
  main(sys.argv)
