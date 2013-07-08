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
  	print "Output is four lines: SSIM, WebP file size, JPEG file size, and WebP to JPEG file size ratio."
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

  # Calculate SSIM and file size for all WebP quality levels.
  webp_ssim_values = []
  webp_file_sizes = []
  q = 0
  while q <= 100:
    webp = tmp_file_base + str(q) + ".webp"
    test_utils.png_to_webp(png, q, webp)
    webp_file_sizes.append(os.path.getsize(webp))
    webp_png = webp + ".png"
    test_utils.webp_to_png(webp, webp_png)
    webp_ssim_values.append(test_utils.ssim_float_for_images(png, webp_png))
    os.remove(webp)
    os.remove(webp_png)
    q += 1

  webp_file_size = test_utils.interpolate(webp_ssim_values, jpeg_ssim, webp_file_sizes)

  ratio = webp_file_size / jpeg_file_size

  print "SSIM: " + str(jpeg_ssim)[:5]
  print "WebP_File_Size_(kb): %.1f" % (int(webp_file_size) / 1024.0)
  print "JPEG_File_Size_(kb): %.1f" % (int(jpeg_file_size) / 1024.0)
  print "WebP_to_JPEG_File_Size_Ratio: " + str(ratio)[:5]

if __name__ == "__main__":
  main(sys.argv)
