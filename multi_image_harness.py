#!/usr/bin/python
# Written by Josh Aas, Mozilla Corporation
# License: Do whatever you want with the code.

import sys
import subprocess

def main(argv):
  if len(argv) < 4:
  	print "First arg is a JPEG quality value to test (e.g. '75')."
  	print "Second arg is the path to a test to run (e.g. './webp_jpeg_ssim.py')."
  	print "All further arguments are file paths to images to test (e.g. 'images/Lenna.jpg')."
  	print "There must be at least one image given."
  	print "Output is four lines: SSIM, WebP file size, JPEG file size, and WebP to JPEG file size ratio."
  	print "This is the arithmetic average of results from all images."
  	print "Output labels have no spaces so that a string split on a line produces the numeric result at index 1."
  	return

  jpeg_q = int(argv[1])
  test_path = argv[2]
  test_images = argv[3:]

  ssim_total = 0.0
  jpeg_file_size_total = 0.0 # This is in KB
  webp_file_size_total = 0.0 # This is in KB
  for i in test_images:
    output = subprocess.Popen(["python", test_path, str(jpeg_q), i], stdout=subprocess.PIPE).communicate()[0]
    lines = output.splitlines(False)
    i = 0
    for line in lines:
      s = line.split()
      if i == 0:
        ssim_total += float(s[1])
      if i == 1:
        webp_file_size_total += float(s[1])
      if i == 2:
        jpeg_file_size_total += float(s[1])
      i += 1

  avg_ssim = ssim_total / float(len(test_images))
  avg_webp_file_size = webp_file_size_total / float(len(test_images))
  avg_jpeg_file_size = jpeg_file_size_total / float(len(test_images))

  ratio = avg_webp_file_size / avg_jpeg_file_size

  print "Avg_SSIM: " + str(avg_ssim)[:5]
  print "Avg_WebP_File_Size_(kb): %.1f" % (avg_webp_file_size)
  print "Avg_JPEG_File_Size_(kb): %.1f" % (avg_jpeg_file_size)
  print "WebP_to_JPEG_File_Size_Ratio: " + str(ratio)[:5]

if __name__ == "__main__":
  main(sys.argv)
