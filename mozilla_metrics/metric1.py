#!/usr/bin/python
#
# Copyright 2010 Google Inc.
#
# This code is licensed under the same terms as WebM:
#  Software License Agreement:  http://www.webmproject.org/license/software/
#  Additional IP Rights Grant:  http://www.webmproject.org/license/additional/
# -----------------------------------------------------------------------------

import os
import sys
import time

ssim = "/Users/josh/src/image-formats/SSIM/ssim"
cjpeg = "/opt/local/bin/cjpeg -optimize"
djpeg = "/opt/local/bin/djpeg"
cwebp = "/Users/josh/src/image-formats/libwebp-0.3.0/cwebp"
dwebp = "/Users/josh/src/image-formats/libwebp-0.3.0/dwebp"
convert = "/opt/local/bin/convert"

tmpdir = "/tmp/"

# Return a single float value from the ssim program output
def ssim_float_for_images(img1_path, img2_path):
  cmd = "%s %s %s" % (ssim, img1_path, img2_path)
  proc = os.popen(cmd, "r")
  proc.readline() # Throw out the first line of output
  r = float(proc.readline().strip().strip('%'))
  g = float(proc.readline().strip().strip('%'))
  b = float(proc.readline().strip().strip('%'))
  return (((r + g + b) / 3) / 100)

# Returns an SSIM value for a WebP image compared to a PNG
def get_webp_ssim(png_path, quality, webp_path):
  cmd = "%s -quiet -q %d %s -o %s" % (cwebp, quality, png_path, webp_path)
  os.system(cmd)
  webp_png_path = webp_path + ".png"
  cmd = "%s %s -o %s" % (dwebp, webp_path, webp_png_path)
  os.system(cmd)
  result = ssim_float_for_images(png_path, webp_png_path)
  os.remove(webp_png_path)
  return result

# Find the closest WebP ssim match for a given JPEG
def get_webp_ssim_match(j_ssim, png_path, webp_path):
  q = 95
  curr_ssim = get_webp_ssim(png_path, q, webp_path)
  w_ssim = curr_ssim

  delta_q = int(1000 * (j_ssim - curr_ssim))
  if q + delta_q > 100:
    delta_q = 100 - q
  elif q + delta_q < 0:
    delta_q = 1 - q

  test_q = q + delta_q
  while delta_q != 0:
    accept = False
    if test_q > 0 and test_q <= 100:
      curr_ssim = get_webp_ssim(png_path, test_q, webp_path)
      # accept if curr_ssim is in the same side of j_ssim.
      accept = (curr_ssim < j_ssim) ^ (delta_q < 0)

    if accept:
      q = test_q
      w_ssim = curr_ssim
    else:
      delta_q = int(float(delta_q) / 2)

    test_q = q + delta_q

def main(argv):
  png = argv[1]
  filename = os.path.basename(png)
  basename = tmpdir + os.path.splitext(filename)[0]

  jpeg_files = []
  webp_files = []

  quality_values = [50, 55, 60, 65, 70, 75, 80, 85, 90, 95]
  for q in quality_values:
    ppm_file =  basename + str(q) + ".ppm"
    jpg_file =  basename + str(q) + ".jpg"
    webp_file = basename + str(q) + ".webp"
    jpg_ppm =   basename + str(q) + "_jpg.ppm"
    jpg_png =   basename + str(q) + "_jpg.png"

    cmd = "%s %s %s" % (convert, png, ppm_file)
    os.system(cmd)
    cmd = "%s -quality %d -outfile %s %s" % (cjpeg, q, jpg_file, ppm_file)
    os.system(cmd)
    cmd = "%s -outfile %s %s" % (djpeg, jpg_ppm, jpg_file)
    os.system(cmd)
    cmd = "%s %s %s" % (convert, jpg_ppm, jpg_png)
    os.system(cmd)

    j_ssim = ssim_float_for_images(png, jpg_png)

    os.remove(ppm_file)
    os.remove(jpg_ppm)
    os.remove(jpg_png)

    jpeg_files.append(jpg_file)

    get_webp_ssim_match(j_ssim, png, webp_file)
    webp_files.append(webp_file)

  jpeg_total_size = 0;
  for f in jpeg_files:
    jpeg_total_size += os.path.getsize(f)

  webp_total_size = 0;
  for f in webp_files:
    webp_total_size += os.path.getsize(f)

  print "WebP size compared to JPEG: " + str(float(webp_total_size) / float(jpeg_total_size));

  for f in jpeg_files:
    os.remove(f)
  for f in webp_files:
    os.remove(f)

if __name__ == "__main__":
  main(sys.argv)
