# Written by Josh Aas, Mozilla Corporation
# License: Do whatever you want with the code.

import os
import subprocess
import sys

# Paths to various programs used by the tests.
ssim = "/Users/josh/src/image-formats/SSIM/ssim"
yuvjpeg = "/Users/josh/src/image-formats/web_image_formats/encoders/yuvjpeg"
convert = "/opt/local/bin/convert"
chevc = "/Users/josh/src/image-formats/jctvc-hm/trunk/bin/TAppEncoderStatic"
cjxr = "/Users/josh/src/image-formats/jxrlib/JxrEncApp"
djxr = "/Users/josh/src/image-formats/jxrlib/JxrDecApp"
yuvwebp = "/Users/josh/src/image-formats/web_image_formats/encoders/yuvwebp"
webpyuv = "/Users/josh/src/image-formats/web_image_formats/decoders/webpyuv"

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

def get_jpeg_results(in_png, quality):
  tmp_file_base = path_for_file_in_tmp(in_png)
  png_yuv = tmp_file_base + str(quality) + ".yuv"
  cmd = "%s %s -sampling-factor 4:2:0 -depth 8 %s" % (convert, in_png, png_yuv)
  run_silent(cmd)
  yuv_jpg = png_yuv + ".jpg"
  cmd = "%s %i %ix%i %s %s" % (yuvjpeg, quality, get_png_width(in_png), get_png_height(in_png), png_yuv, yuv_jpg)
  run_silent(cmd)
  jpeg_file_size = os.path.getsize(yuv_jpg)
  jpg_yuv = yuv_jpg + ".yuv"
  cmd = "%s %s -sampling-factor 4:2:0 -depth 8 %s" % (convert, yuv_jpg, jpg_yuv)
  run_silent(cmd)
  yuv_png = jpg_yuv + ".png"
  cmd = "%s -sampling-factor 4:2:0 -depth 8 -size %ix%i %s %s" % (convert, get_png_width(in_png), get_png_height(in_png), jpg_yuv, yuv_png)
  run_silent(cmd)
  jpeg_ssim = ssim_float_for_images(in_png, yuv_png)
  os.remove(png_yuv)
  os.remove(yuv_jpg)
  os.remove(jpg_yuv)
  os.remove(yuv_png)
  return (jpeg_ssim, jpeg_file_size)

# Returns an SSIM value and a file size
def get_webp_results(in_png, quality):
  tmp_file_base = path_for_file_in_tmp(in_png)
  png_yuv = tmp_file_base + str(quality) + ".yuv"
  cmd = "%s %s -sampling-factor 4:2:0 -depth 8 %s" % (convert, in_png, png_yuv)
  run_silent(cmd)
  yuv_webp = png_yuv + ".webp"
  cmd = "%s %i %ix%i %s %s" % (yuvwebp, quality, get_png_width(in_png), get_png_height(in_png), png_yuv, yuv_webp)
  run_silent(cmd)
  webp_file_size = os.path.getsize(yuv_webp)
  webp_yuv = yuv_webp + ".yuv"
  cmd = "%s %s %s" % (webpyuv, yuv_webp, webp_yuv)
  run_silent(cmd)
  yuv_png = webp_yuv + ".png"
  cmd = "%s -sampling-factor 4:2:0 -depth 8 -size %ix%i %s %s" % (convert, get_png_width(in_png), get_png_height(in_png), webp_yuv, yuv_png)
  run_silent(cmd)
  webp_ssim = ssim_float_for_images(in_png, yuv_png)
  os.remove(png_yuv)
  os.remove(yuv_webp)
  os.remove(webp_yuv)
  os.remove(yuv_png)
  return (webp_ssim, webp_file_size)

# Returns an SSIM value and a file size
def get_hevc_results(in_png, quality):
  tmp_file_base = path_for_file_in_tmp(in_png)
  png_yuv = tmp_file_base + str(quality) + ".yuv"
  cmd = "%s %s -sampling-factor 4:2:0 -depth 8 %s" % (convert, in_png, png_yuv)
  run_silent(cmd)
  yuv_hevc = png_yuv + ".hevc"
  hevc_yuv = yuv_hevc + ".yuv"
  cmd = "%s -c %s -wdt %i -hgt %i --SAOLcuBoundary 1 -q %i -i %s -fr 50 -f 1 -b %s -o %s" % (chevc, hevc_config, get_png_width(in_png), get_png_height(in_png), quality, png_yuv, yuv_hevc, hevc_yuv)
  run_silent(cmd)
  hevc_file_size = os.path.getsize(yuv_hevc)
  hevc_file_size += 80 # Penalize HEVC bit streams for not having a container like
                       # other formats do. Came up with this number because a
                       # 1x1 pixel hevc file is 84 bytes.
  yuv_png = hevc_yuv + ".png"
  cmd = "%s -sampling-factor 4:2:0 -depth 8 -size %ix%i %s %s" % (convert, get_png_width(in_png), get_png_height(in_png), hevc_yuv, yuv_png)
  run_silent(cmd)
  hevc_ssim = ssim_float_for_images(in_png, yuv_png)
  os.remove(png_yuv)
  os.remove(yuv_hevc)
  os.remove(hevc_yuv)
  os.remove(yuv_png)
  return (hevc_ssim, hevc_file_size)
