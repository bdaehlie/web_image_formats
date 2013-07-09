# Written by Josh Aas, Mozilla Corporation
# License: Do whatever you want with the code.

import os
import subprocess
import sys

# Paths to various programs used by the tests.
ssim = "/Users/josh/src/image-formats/SSIM/ssim"
cjpeg = "/opt/local/bin/cjpeg -optimize"
djpeg = "/opt/local/bin/djpeg"
cwebp = "/Users/josh/src/image-formats/libwebp-0.3.0/cwebp"
dwebp = "/Users/josh/src/image-formats/libwebp-0.3.0/dwebp"
convert = "/opt/local/bin/convert"
chevc = "/Users/josh/src/image-formats/jctvc-hm/trunk/bin/TAppEncoderStatic"
dhevc = "/Users/josh/src/image-formats/jctvc-hm/trunk/bin/TAppDecoderStatic"
cjxr = "/Users/josh/src/image-formats/jxrlib/JxrEncApp"
djxr = "/Users/josh/src/image-formats/jxrlib/JxrDecApp"
png2y4m = "/Users/josh/src/image-formats/daala/tools/png2y4m"
y4m2png = "/Users/josh/src/image-formats/daala/tools/y4m2png"
ffmpeg = "/opt/local/bin/ffmpeg"

# HEVC config file
hevc_config = "/Users/josh/src/image-formats/jctvc-hm/trunk/cfg/encoder_randomaccess_main.cfg"

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
  ssim_p = (ssim_value - ssim_low) / (ssim_high - ssim_low)
  return (((file_size_high - file_size_low) * ssim_p) + file_size_low)

# This takes two lists, a and b, which must be of equal length.
# Lists can be integers or floats, and they don't have to match.
# Lists must contain values in ascending order, duplicates allowed.
# This also take a value in the same terms as the values in list a.
# This will interpolate a point in terms of list b based on where
# the a value falls in list a.
def lists_interpolate(list_a, a_value, list_b):
  if (len(list_a) != len(list_b)) or (len(list_a) < 1):
    print "Unacceptable lists passed to interpolate function!"
  i = 0
  while i < len(list_a):
    if list_a[i] == a_value:
      return list_b[i]
    if list_a[i] > a_value:
      if i == 0:
        return list_b[0]
      h = i - 1
      a_diff = list_a[i] - list_a[h]
      if a_diff == 0:
        return list_b[i]
      a_val_diff = a_value - list_a[h]
      percent = a_val_diff / a_diff
      b_diff = list_b[i] - list_b[h]
      return ((b_diff * percent) + list_b[h])
    i += 1
  return list_b[-1]

def get_png_width(png_path):
  cmd = "identify -format \"%%w\" %s" % (png_path)
  proc = os.popen(cmd, "r")
  return int(proc.readline().strip())

def get_png_height(png_path):
  cmd = "identify -format \"%%h\" %s" % (png_path)
  proc = os.popen(cmd, "r")
  return int(proc.readline().strip())

def png_to_hevc(in_png, quality, out_hevc):
  png_y4m = path_for_file_in_tmp(in_png) + ".y4m"
  cmd = "%s %s -o %s" % (png2y4m, in_png, png_y4m)
  run_silent(cmd)
  y4m_yuv = png_y4m + ".yuv"
  cmd = "%s -y -i %s %s" % (ffmpeg, png_y4m, y4m_yuv)
  run_silent(cmd)
  cmd = "%s -c %s -wdt %i -hgt %i -aq 1 --SAOLcuBoundary 1 -q %i -i %s -fr 50 -f 500 -b %s" % (chevc, hevc_config, get_png_width(in_png), get_png_height(in_png), quality, y4m_yuv, out_hevc)
  run_silent(cmd)
  os.remove(png_y4m)
  os.remove(y4m_yuv)

# HEVC files are just bitstreams with no meta-data.
# This means we need to have dimensions passed in.
def hevc_to_png(in_hevc, width, height, out_png):
  hevc_yuv = path_for_file_in_tmp(in_hevc) + ".yuv"
  cmd = "%s -b %s -o %s" % (dhevc, in_hevc, hevc_yuv)
  run_silent(cmd)
  yuv_y4m = hevc_yuv + ".y4m"
  cmd = "%s -y -s %ix%i -i %s %s" % (ffmpeg, width, height, hevc_yuv, yuv_y4m)
  run_silent(cmd)
  cmd = "%s %s -o %s" % (y4m2png, yuv_y4m, out_png)
  run_silent(cmd)
  os.remove(hevc_yuv)
  os.remove(yuv_y4m)

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
