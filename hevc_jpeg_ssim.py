#!/usr/bin/python
# Written by Josh Aas, Mozilla Corporation
# License: Do whatever you want with the code.

import os
import sys
import time
import test_utils

def main(argv):
  if len(argv) < 2:
  	print "First arg is a JPEG quality value to test (e.g. '75')."
  	print "Second arg is the path to an image to test (e.g. 'images/Lenna.jpg')."
  	print "Output is four lines: SSIM, HEVC file size, JPEG file size, and HEVC to JPEG file size ratio."
  	print "Output labels have no spaces so that a string split on a line produces the numeric result at index 1."
  	return

  jpeg_q = int(argv[1])
  png = argv[2]

  tmp_file_base = test_utils.tmpdir + os.path.basename(png)

  jpg = tmp_file_base + str(jpeg_q) + ".jpg"
  test_utils.png_to_jpeg(png, jpeg_q, jpg)
  jpeg_file_size = os.path.getsize(jpg)
  jpg_png = jpg + ".png"
  test_utils.jpeg_to_png(jpg, jpg_png)
  jpeg_ssim = test_utils.ssim_float_for_images(png, jpg_png)
  os.remove(jpg)
  os.remove(jpg_png)

  # Calculate SSIM and file size for all HEVC quality levels.
  hevc_ssim_values = []
  hevc_file_sizes = []
  q = 50
  while q > 0:
    hevc = tmp_file_base + str(q) + ".hevc"
    test_utils.png_to_hevc(png, q, hevc)
    hevc_file_size = os.path.getsize(hevc)
    hevc_file_size += 80 # Penalize HEVC bit streams for not having a container like
                         # other formats do. Came up with this number because a
                         # 1x1 pixel webp file is 84 bytes.
    hevc_file_sizes.append(hevc_file_size)
    hevc_png = hevc + ".png"
    test_utils.hevc_to_png(hevc, test_utils.get_png_width(png), test_utils.get_png_height(png), hevc_png)
    hevc_ssim_values.append(test_utils.ssim_float_for_images(png, hevc_png))
    os.remove(hevc)
    os.remove(hevc_png)
    q -= 1

  hevc_file_size = test_utils.interpolate(hevc_ssim_values, jpeg_ssim, hevc_file_sizes)

  ratio = hevc_file_size / jpeg_file_size

  print "SSIM: " + str(jpeg_ssim)[:5]
  print "HEVC_File_Size_(kb): %.1f" % (int(hevc_file_size) / 1024.0)
  print "JPEG_File_Size_(kb): %.1f" % (int(jpeg_file_size) / 1024.0)
  print "HEVC_to_JPEG_File_Size_Ratio: " + str(ratio)[:5]

if __name__ == "__main__":
  main(sys.argv)
