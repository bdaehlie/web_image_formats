# Written by Josh Aas, Mozilla Corporation
# License: Do whatever you want with the code.

import os
import subprocess
import sys

# Paths to various programs used by the tests.
ssim = "/Users/josh/src/image-formats/SSIM/ssim"
cjpeg = "/opt/local/bin/cjpeg -optimize"
djpeg = "/opt/local/bin/djpeg"
cwebp = "/Users/josh/src/image-formats/libwebp-0.3.1/examples/cwebp"
dwebp = "/Users/josh/src/image-formats/libwebp-0.3.1/examples/dwebp"
convert = "/opt/local/bin/convert"
chevc = "/Users/josh/src/image-formats/jctvc-hm/trunk/bin/TAppEncoderStatic"
cjxr = "/Users/josh/src/image-formats/jxrlib/JxrEncApp"
djxr = "/Users/josh/src/image-formats/jxrlib/JxrDecApp"

# HEVC config file
hevc_config = "/Users/josh/src/image-formats/jctvc-hm/trunk/cfg/encoder_intra_main.cfg"

# Path to tmp dir to be used by the tests.
tmpdir = "/tmp/"

# Run a subprocess with silent non-error output
def run_silent(cmd):
  FNULL = open(os.devnull, 'w')
  rv = subprocess.call(cmd.split(), stdout=FNULL, stderr=subprocess.STDOUT)
  if rv != 0:
    sys.stderr.write("Failure from subprocess, aborting!\n")
    sys.exit(rv)
  return rv

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
  return tmpdir + str(os.getpid()) + os.path.basename(in_path)

def png_to_webp(in_png, quality, out_webp):
  cmd = "%s -quiet -q %d %s -o %s" % (cwebp, quality, in_png, out_webp)
  run_silent(cmd)

def webp_to_png(in_webp, out_png):
  cmd = "%s %s -o %s" % (dwebp, in_webp, out_png)
  run_silent(cmd)

def png_to_jpeg(in_png, quality, out_jpeg):
  png_ppm = path_for_file_in_tmp(in_png) + ".ppm"
  cmd = "%s %s %s" % (convert, in_png, png_ppm)
  run_silent(cmd)
  cmd = "%s -quality %d -outfile %s %s" % (cjpeg, quality, out_jpeg, png_ppm)
  run_silent(cmd)
  os.remove(png_ppm)

def jpeg_to_png(in_jpeg, out_png):
  jpg_ppm = path_for_file_in_tmp(in_jpeg) + ".ppm"
  cmd = "%s -outfile %s %s" % (djpeg, jpg_ppm, in_jpeg)
  run_silent(cmd)
  cmd = "%s %s %s" % (convert, jpg_ppm, out_png)
  run_silent(cmd)
  os.remove(jpg_ppm)

# Returns file size at particular SSIM via interpolation.
def file_size_interpolate(ssim_high, ssim_low, ssim_value, file_size_high, file_size_low):
  ssim_p = 1.0
  if ssim_high != ssim_low:
    ssim_p = (ssim_value - ssim_low) / (ssim_high - ssim_low)
  return (((file_size_high - file_size_low) * ssim_p) + file_size_low)

def get_png_width(png_path):
  cmd = "identify -format \"%%w\" %s" % (png_path)
  proc = os.popen(cmd, "r")
  return int(proc.readline().strip())

def get_png_height(png_path):
  cmd = "identify -format \"%%h\" %s" % (png_path)
  proc = os.popen(cmd, "r")
  return int(proc.readline().strip())

def png_to_hevc(in_png, quality, out_hevc, out_hevc_yuv):
  png_width = get_png_width(in_png)
  png_height = get_png_height(in_png)
  png_yuv = path_for_file_in_tmp(in_png) + ".yuv"
  cmd = "%s %s -size %ix%i -depth 8 -colorspace sRGB -sampling-factor 4:2:0 %s" % (convert, in_png, png_width, png_height, png_yuv)
  run_silent(cmd)
  cmd = "%s -c %s -wdt %i -hgt %i -aq 1 --SAOLcuBoundary 1 -q %i -i %s -fr 50 -f 1 -b %s -o %s" % (chevc, hevc_config, png_width, png_height, quality, png_yuv, out_hevc, out_hevc_yuv)
  run_silent(cmd)
  os.remove(png_yuv)

def hevc_yuv_to_png(in_hevc_yuv, width, height, out_png):
  cmd = "%s -size %ix%i -depth 8 -colorspace sRGB -sampling-factor 4:2:0 %s %s" % (convert, width, height, in_hevc_yuv, out_png)
  run_silent(cmd)

def jxr_to_png(in_jxr, out_png):
  jxr_bmp = path_for_file_in_tmp(in_jxr) + ".bmp"
  cmd = "%s -i %s -o %s" % (djxr, in_jxr, jxr_bmp)
  run_silent(cmd)
  cmd = "%s %s %s" % (convert, jxr_bmp, out_png)
  run_silent(cmd)
  os.remove(jxr_bmp)

def png_to_jxr(in_png, quality, out_jxr):
  png_bmp = path_for_file_in_tmp(in_png) + ".bmp"
  cmd = "%s %s %s" % (convert, in_png, png_bmp)
  run_silent(cmd)
  cmd = "%s -i %s -o %s -q %f" % (cjxr, png_bmp, out_jxr, quality)
  run_silent(cmd)
  os.remove(png_bmp)

def get_jpeg_results(in_png, jpeg_q):
  tmp_file_base = path_for_file_in_tmp(in_png)
  jpg = tmp_file_base + str(jpeg_q) + ".jpg"
  png_to_jpeg(in_png, jpeg_q, jpg)
  jpeg_file_size = os.path.getsize(jpg)
  jpg_png = jpg + ".png"
  jpeg_to_png(jpg, jpg_png)
  jpeg_ssim = ssim_float_for_images(in_png, jpg_png)
  os.remove(jpg)
  os.remove(jpg_png)
  return (jpeg_ssim, jpeg_file_size)
