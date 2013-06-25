# Written by Josh Aas (Mozilla Corporation)
# License: Do whatever you want with this code, I don't care.

import os

# Paths to various programs used by the tests.
ssim = "/Users/josh/src/image-formats/SSIM/ssim"
cjpeg = "/opt/local/bin/cjpeg -optimize"
djpeg = "/opt/local/bin/djpeg"
cwebp = "/Users/josh/src/image-formats/libwebp-0.3.0/cwebp"
dwebp = "/Users/josh/src/image-formats/libwebp-0.3.0/dwebp"
convert = "/opt/local/bin/convert"

# Path to tmp dir to be used by the tests.
tmpdir = "/tmp/"

# Return a single float value from the ssim program output.
def ssim_float_for_images(img1_path, img2_path):
  cmd = "%s %s %s" % (ssim, img1_path, img2_path)
  proc = os.popen(cmd, "r")
  proc.readline() # Throw out the first line of output
  r = float(proc.readline().strip().strip('%'))
  g = float(proc.readline().strip().strip('%'))
  b = float(proc.readline().strip().strip('%'))
  return (((r + g + b) / 3) / 100)

# Converts a file path to the path that represents
# the same file in the tmp dir.
def path_for_file_in_tmp(in_path):
  return tmpdir + os.path.basename(in_path)

def png_to_webp(in_png, quality, out_webp):
  cmd = "%s -quiet -q %d %s -o %s" % (cwebp, quality, in_png, out_webp)
  os.system(cmd)

def webp_to_png(in_webp, out_png):
  cmd = "%s %s -o %s" % (dwebp, in_webp, out_png)
  os.system(cmd)

def png_to_jpeg(in_png, quality, out_jpeg):
  png_ppm = path_for_file_in_tmp(in_png) + ".ppm"
  cmd = "%s %s %s" % (convert, in_png, png_ppm)
  os.system(cmd)
  cmd = "%s -quality %d -outfile %s %s" % (cjpeg, quality, out_jpeg, png_ppm)
  os.system(cmd)
  os.remove(png_ppm)

def jpeg_to_png(in_jpeg, out_png):
  jpg_ppm = in_jpeg + ".ppm"
  cmd = "%s -outfile %s %s" % (djpeg, jpg_ppm, in_jpeg)
  os.system(cmd)
  cmd = "%s %s %s" % (convert, jpg_ppm, out_png)
  os.system(cmd)
  os.remove(jpg_ppm)
