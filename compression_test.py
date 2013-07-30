#!/usr/bin/python
# Written by Josh Aas
# Copyright (c) 2013, Mozilla Corporation
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the Mozilla Corporation nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import os
import subprocess
import sys
import math

# Paths to various programs used by the tests.
yuvjpeg = "./encoders/yuvjpeg"
jpegyuv = "./decoders/jpegyuv"
yuvwebp = "./encoders/yuvwebp"
webpyuv = "./decoders/webpyuv"
convert = "/opt/local/bin/convert"
ssim = "/Users/josh/src/image-formats/SSIM/ssim"
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

def find_file_size_for_ssim(results_function, png, quality_list, jpg_ssim):
  low_index = -1
  low_results = (0.0, 0)
  high_index = len(quality_list)
  high_results = (0.0, 0)
  while (high_index - low_index) > 1:
    i = int(math.floor((float(high_index - low_index) / 2.0)) + low_index)
    results = results_function(png, quality_list[i])
    webp_ssim = results[0]
    webp_file_size = results[1]
    if webp_ssim == jpg_ssim:
      low_index = high_index = i
      low_results = high_results = results
      break
    if webp_ssim < jpg_ssim:
      low_index = i
      low_results = results
    if webp_ssim > jpg_ssim:
      high_index = i
      high_results = results
  if low_index == -1 or high_index == len(quality_list):
    sys.stderr.write("Failure: Unsuccessful binary search!\n")
    sys.exit(1)
  return file_size_interpolate(high_results[0], low_results[0], jpg_ssim, high_results[1], low_results[1])

def png_to_yuv(in_png, out_yuv):
  cmd = "%s %s -sampling-factor 4:2:0 -depth 8 %s" % (convert, in_png, out_yuv)
  run_silent(cmd)

def yuv_to_png(in_yuv, width, height, out_png):
  cmd = "%s -sampling-factor 4:2:0 -depth 8 -size %ix%i %s %s" % (convert, width, height, in_yuv, out_png)
  run_silent(cmd)

def get_jpeg_results(in_png, quality):
  png_yuv = path_for_file_in_tmp(in_png) + str(quality) + ".yuv"
  png_to_yuv(in_png, png_yuv)
  yuv_jpg = png_yuv + ".jpg"
  cmd = "%s %i %ix%i %s %s" % (yuvjpeg, quality, get_png_width(in_png), get_png_height(in_png), png_yuv, yuv_jpg)
  run_silent(cmd)
  jpeg_file_size = os.path.getsize(yuv_jpg)
  jpg_yuv = yuv_jpg + ".yuv"
  cmd = "%s %s %s" % (jpegyuv, yuv_jpg, jpg_yuv)
  run_silent(cmd)
  yuv_png = jpg_yuv + ".png"
  yuv_to_png(jpg_yuv, get_png_width(in_png), get_png_height(in_png), yuv_png)
  jpeg_ssim = ssim_float_for_images(in_png, yuv_png)
  os.remove(png_yuv)
  os.remove(yuv_jpg)
  os.remove(jpg_yuv)
  os.remove(yuv_png)
  return (jpeg_ssim, jpeg_file_size)

# Returns an SSIM value and a file size
def get_webp_results(in_png, quality):
  png_yuv = path_for_file_in_tmp(in_png) + str(quality) + ".yuv"
  png_to_yuv(in_png, png_yuv)
  yuv_webp = png_yuv + ".webp"
  cmd = "%s %i %ix%i %s %s" % (yuvwebp, quality, get_png_width(in_png), get_png_height(in_png), png_yuv, yuv_webp)
  run_silent(cmd)
  webp_file_size = os.path.getsize(yuv_webp)
  webp_yuv = yuv_webp + ".yuv"
  cmd = "%s %s %s" % (webpyuv, yuv_webp, webp_yuv)
  run_silent(cmd)
  yuv_png = webp_yuv + ".png"
  yuv_to_png(webp_yuv, get_png_width(in_png), get_png_height(in_png), yuv_png)
  webp_ssim = ssim_float_for_images(in_png, yuv_png)
  os.remove(png_yuv)
  os.remove(yuv_webp)
  os.remove(webp_yuv)
  os.remove(yuv_png)
  return (webp_ssim, webp_file_size)

# Returns an SSIM value and a file size
def get_hevc_results(in_png, quality):
  png_yuv = path_for_file_in_tmp(in_png) + str(quality) + ".yuv"
  png_to_yuv(in_png, png_yuv)
  yuv_hevc = png_yuv + ".hevc"
  hevc_yuv = yuv_hevc + ".yuv"
  cmd = "%s -c %s -wdt %i -hgt %i --SAOLcuBoundary 1 -q %i -i %s -fr 50 -f 1 -b %s -o %s" % (chevc, hevc_config, get_png_width(in_png), get_png_height(in_png), quality, png_yuv, yuv_hevc, hevc_yuv)
  run_silent(cmd)
  hevc_file_size = os.path.getsize(yuv_hevc)
  hevc_file_size += 80 # Penalize HEVC bit streams for not having a container like
                       # other formats do. Came up with this number because a
                       # 1x1 pixel hevc file is 84 bytes.
  yuv_png = hevc_yuv + ".png"
  yuv_to_png(hevc_yuv, get_png_width(in_png), get_png_height(in_png), yuv_png)
  hevc_ssim = ssim_float_for_images(in_png, yuv_png)
  os.remove(png_yuv)
  os.remove(yuv_hevc)
  os.remove(hevc_yuv)
  os.remove(yuv_png)
  return (hevc_ssim, hevc_file_size)

#TODO: Make this use YUV input like everything else
def get_jxr_results(in_png, quality):
  png_bmp = path_for_file_in_tmp(in_png) + str(quality) + ".bmp"
  cmd = "%s %s %s" % (convert, in_png, png_bmp)
  run_silent(cmd)
  bmp_jxr = png_bmp + ".jxr"
  cmd = "%s -i %s -o %s -q %f" % (cjxr, png_bmp, bmp_jxr, quality)
  run_silent(cmd)
  jxr_file_size = os.path.getsize(bmp_jxr)
  jxr_bmp = bmp_jxr + ".bmp"
  cmd = "%s -i %s -o %s" % (djxr, bmp_jxr, jxr_bmp)
  run_silent(cmd)
  bmp_png = jxr_bmp + ".png"
  cmd = "%s %s %s" % (convert, jxr_bmp, bmp_png)
  run_silent(cmd)
  ssim = ssim_float_for_images(in_png, bmp_png)
  os.remove(png_bmp)
  os.remove(bmp_jxr)
  os.remove(jxr_bmp)
  os.remove(bmp_png)
  return (ssim, jxr_file_size)

def quality_list_for_format(format):
  possible_q = []
  if format == 'hevc':
    q = 50
    while q >= 0.0:
      possible_q.append(q)
      q -= 0.5
    return possible_q
  if format == 'webp':
    q = 0
    while q < 101:
      possible_q.append(q)
      q += 1
    return possible_q
  if format == 'jxr':
    q = 0.0
    while q < 1.0:
      possible_q.append(q)
      q += 0.01
    return possible_q
  sys.stderr.write("Can't find quality list for format!\n")
  sys.exit(rv)

def results_function_for_format(format):
  if format == 'hevc':
    return get_hevc_results
  if format == 'webp':
    return get_webp_results
  if format == 'jxr':
    return get_jxr_results
  sys.stderr.write("Can't find results function for format!\n")
  sys.exit(rv)

# Each format is a tuple with name and associated functions
# Note that 'jxr' is disabled due to a lack of consistent encoding/decoding.
supported_formats = ['webp', 'hevc']

def main(argv):
  if len(argv) != 4:
    print "First arg is format to test %s" % (supported_formats)
    print "Second arg is a JPEG quality value to test (e.g. '75')."
    print "Third arg is the path to an image to test (e.g. 'images/Lenna.png')."
    print "Output is four lines: SSIM, target format file size, JPEG file size, and target format to JPEG file size ratio."
    print "Output labels have no spaces so that a string split on a line produces the numeric result at index 1."
    return

  format_name = argv[1]
  if format_name not in supported_formats:
    print "Image format not supported!"
    return
  quality_list = quality_list_for_format(format_name)
  results_function = results_function_for_format(format_name)

  jpg_q = int(argv[2])
  png = argv[3]

  jpg_results = get_jpeg_results(png, jpg_q)
  jpg_ssim = jpg_results[0]
  jpg_file_size = jpg_results[1]

  file_size = find_file_size_for_ssim(results_function, png, quality_list, jpg_ssim)

  ratio = float(file_size) / float(jpg_file_size)

  print "SSIM: " + str(jpg_ssim)[:5]
  print "%s_File_Size_(kb): %.1f" % (format_name, float(file_size) / 1024.0)
  print "jpeg_File_Size_(kb): %.1f" % (float(jpg_file_size) / 1024.0)
  print "WebP_to_JPEG_File_Size_Ratio: %.2f" % (ratio)

if __name__ == "__main__":
  main(sys.argv)
