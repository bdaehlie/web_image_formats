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

  webp_ssim = 0.0
  webp_file_size = 0
  q = 100
  while q <= 100:
    webp = tmp_file_base + str(q) + ".webp"
    test_utils.png_to_webp(png, q, webp)
    webp_png = webp + ".png"
    test_utils.webp_to_png(webp, webp_png)
    ssim = test_utils.ssim_float_for_images(png, webp_png)
    file_size = os.path.getsize(webp)
    os.remove(webp)
    os.remove(webp_png)
    if ssim < jpeg_ssim:
      if webp_file_size == 0:
        # We require that the target format be capable of producing an
        # image at equal or greater quality than JPEG image being tested.
        sys.stderr.write("Target format cannot match JPEG quality, aborting!\n")
        sys.exit(1)
      else:
        webp_file_size = test_utils.file_size_interpolate(webp_ssim, ssim, jpeg_ssim, webp_file_size, file_size)
        webp_ssim = jpeg_ssim # The WebP SSIM after interpolation is the same as the JPEG SSIM.
      break
    webp_ssim = ssim
    webp_file_size = file_size
    q -= 1

  ratio = webp_file_size / jpeg_file_size

  print "SSIM: " + str(jpeg_ssim)[:5]
  print "WebP_File_Size_(kb): %.1f" % (int(webp_file_size) / 1024.0)
  print "JPEG_File_Size_(kb): %.1f" % (int(jpeg_file_size) / 1024.0)
  print "WebP_to_JPEG_File_Size_Ratio: " + str(ratio)[:5]

if __name__ == "__main__":
  main(sys.argv)
