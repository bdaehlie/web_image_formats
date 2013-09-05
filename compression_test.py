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
yuvjxr = "./encoders/yuvjxr"
jxryuv = "./decoders/jxryuv"
convert = "/opt/local/bin/convert"
chevc = "/Users/josh/src/image-formats/jctvc-hm/trunk/bin/TAppEncoderStatic"
ssim = "/Users/josh/src/image-formats/SSIM/ssim"
psnrhvs = "/Users/josh/src/image-formats/daala/tools/dump_psnrhvs"
matlab = "/Applications/MATLAB_R2013a.app/bin/matlab"

# HEVC config file
hevc_config = "/Users/josh/src/image-formats/jctvc-hm/trunk/cfg/encoder_intra_main.cfg"

# path to directory containing required MATLAB code, see README
matlab_iwssim_dir = "/Users/josh/src/image-formats/iwssim"

# Path to tmp dir to be used by the tests.
tmpdir = "/tmp/"

# Run a subprocess with silent non-error output
def run_silent(cmd):
  FNULL = open(os.devnull, 'w')
  rv = subprocess.call(cmd, shell=True, stdout=FNULL, stderr=FNULL)
  if rv != 0:
    sys.stderr.write("Failure from subprocess, aborting!\n")
    sys.exit(rv)
  return rv

def psnrhvs_score(width, height, yuv1, yuv2):
  yuv_y4m1 = yuv1 + ".y4m"
  yuv_to_y4m(width, height, yuv1, yuv_y4m1)
  yuv_y4m2 = yuv2 + ".y4m"
  yuv_to_y4m(width, height, yuv2, yuv_y4m2)
  cmd = "%s -y %s %s" % (psnrhvs, yuv_y4m1, yuv_y4m2)
  proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = proc.communicate()
  lines = out.split(os.linesep)
  qscore = float(lines[1][7:13])
  os.remove(yuv_y4m1)
  os.remove(yuv_y4m2)
  return qscore

def ssim_score(png1, png2):
  cmd = "%s %s %s" % (ssim, png1, png2)
  proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = proc.communicate()
  lines = out.split(os.linesep)
  r = float(lines[1].strip().strip('%'))
  g = float(lines[2].strip().strip('%'))
  b = float(lines[3].strip().strip('%'))
  return (((r + g + b) / 3) / 100)

def iw_ssim_score(png1, png2):
  cmd = "%s -nosplash -nodesktop -r \"addpath('%s'), iwssim(rgb2gray(imread('%s')), rgb2gray(imread('%s'))), quit\"" % (matlab, matlab_iwssim_dir, png1, png2)
  proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = proc.communicate()
  lines = out.split(os.linesep)
  i = 0
  while i < len(lines):
    if lines[i].strip() == "ans =":
      result = float(lines[i + 2].strip())
      break
    i += 1;
  return result

def quality_score(quality_test, png1, png2, yuv1, yuv2):
  if quality_test == 'ssim':
    return ssim_score(png1, png2)
  elif quality_test == 'iwssim':
    return iw_ssim_score(png1, png2)
  elif quality_test == 'psnrhvs':
    return psnrhvs_score(get_png_width(png1), get_png_height(png1), yuv1, yuv2)
  sys.stderr.write("Failure: Invalid quality test!\n")
  sys.exit(1)
  return 0.0

def path_for_file_in_tmp(path):
  return tmpdir + str(os.getpid()) + os.path.basename(path)

def file_size_interpolate(qscore_high, qscore_low, qscore, file_size_high, file_size_low):
  qscore_p = 1.0
  if qscore_high != qscore_low:
    qscore_p = (qscore - qscore_low) / (qscore_high - qscore_low)
  return (((file_size_high - file_size_low) * qscore_p) + file_size_low)

def get_png_width(path):
  cmd = "identify -format \"%%w\" %s" % (path)
  proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = proc.communicate()
  lines = out.split(os.linesep)
  return int(lines[0].strip())

def get_png_height(path):
  cmd = "identify -format \"%%h\" %s" % (path)
  proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = proc.communicate()
  lines = out.split(os.linesep)
  return int(lines[0].strip())

def find_file_size_for_qscore(results_function, quality_test, png, quality_list, jpg_qscore):
  low_index = -1
  low_results = (0.0, 0)
  high_index = len(quality_list)
  high_results = (0.0, 0)
  while (high_index - low_index) > 1:
    i = int(math.floor((float(high_index - low_index) / 2.0)) + low_index)
    results = results_function(quality_test, png, quality_list[i])
    qscore = results[0]
    if qscore == jpg_qscore:
      low_index = high_index = i
      low_results = high_results = results
      break
    if qscore < jpg_qscore:
      low_index = i
      low_results = results
    if qscore > jpg_qscore:
      high_index = i
      high_results = results
  if low_index == -1:
    # We're OK with not being able to produce something as bad as the jpg.
    # Just return the smallest file size we were able to generate, which is
    # stored in "high_results" because we never produced anything smaller.
    return high_results[1]
  if high_index == len(quality_list):
    sys.stderr.write("Failure: Unsuccessful binary search!\n")
    sys.exit(1)
  return file_size_interpolate(high_results[0], low_results[0], jpg_qscore, high_results[1], low_results[1])

def png_to_yuv(png, out_yuv):
  cmd = "%s png:%s -sampling-factor 4:2:0 -depth 8 %s" % (convert, png, out_yuv)
  run_silent(cmd)

def yuv_to_png(width, height, yuv, out_png):
  cmd = "%s -sampling-factor 4:2:0 -depth 8 -size %ix%i yuv:%s %s" % (convert, width, height, yuv, out_png)
  run_silent(cmd)

def yuv_to_y4m(width, height, yuv, out_y4m):
  in_file = open(yuv, 'rb')
  yuv_bytes = in_file.read()
  in_file.close()
  out_file = open(out_y4m, 'wb')
  out_file.write("YUV4MPEG2 W%s H%s F30:1 Ip A0:0" % (width, height))
  out_file.write(b'\x0A')
  out_file.write("FRAME")
  out_file.write(b'\x0A')
  out_file.write(yuv_bytes)
  out_file.close()

def get_jpeg_results(quality_test, png, jpg_quality):
  png_yuv = path_for_file_in_tmp(png) + str(jpg_quality) + ".yuv"
  png_to_yuv(png, png_yuv)
  yuv_jpg = png_yuv + ".jpg"
  cmd = "%s %i %ix%i %s %s" % (yuvjpeg, jpg_quality, get_png_width(png), get_png_height(png), png_yuv, yuv_jpg)
  run_silent(cmd)
  jpeg_file_size = os.path.getsize(yuv_jpg)
  jpg_yuv = yuv_jpg + ".yuv"
  cmd = "%s %s %s" % (jpegyuv, yuv_jpg, jpg_yuv)
  run_silent(cmd)
  yuv_png = jpg_yuv + ".png"
  yuv_to_png(get_png_width(png), get_png_height(png), jpg_yuv, yuv_png)
  qscore = quality_score(quality_test, png, yuv_png, png_yuv, jpg_yuv)
  os.remove(png_yuv)
  os.remove(yuv_jpg)
  os.remove(jpg_yuv)
  os.remove(yuv_png)
  return (qscore, jpeg_file_size)

def get_webp_results(quality_test, png, webp_quality):
  png_yuv = path_for_file_in_tmp(png) + str(webp_quality) + ".yuv"
  png_to_yuv(png, png_yuv)
  yuv_webp = png_yuv + ".webp"
  cmd = "%s %i %ix%i %s %s" % (yuvwebp, webp_quality, get_png_width(png), get_png_height(png), png_yuv, yuv_webp)
  run_silent(cmd)
  webp_file_size = os.path.getsize(yuv_webp)
  webp_yuv = yuv_webp + ".yuv"
  cmd = "%s %s %s" % (webpyuv, yuv_webp, webp_yuv)
  run_silent(cmd)
  yuv_png = webp_yuv + ".png"
  yuv_to_png(get_png_width(png), get_png_height(png), webp_yuv, yuv_png)
  qscore = quality_score(quality_test, png, yuv_png, png_yuv, webp_yuv)
  os.remove(png_yuv)
  os.remove(yuv_webp)
  os.remove(webp_yuv)
  os.remove(yuv_png)
  return (qscore, webp_file_size)

def get_hevc_results(quality_test, png, hevc_quality):
  png_yuv = path_for_file_in_tmp(png) + str(hevc_quality) + ".yuv"
  png_to_yuv(png, png_yuv)
  yuv_hevc = png_yuv + ".hevc"
  hevc_yuv = yuv_hevc + ".yuv"
  cmd = "%s -c %s -wdt %i -hgt %i -q %i -i %s -fr 50 -f 1 --SEIDecodedPictureHash 0 -b %s -o %s" % (chevc, hevc_config, get_png_width(png), get_png_height(png), hevc_quality, png_yuv, yuv_hevc, hevc_yuv)
  run_silent(cmd)
  hevc_file_size = os.path.getsize(yuv_hevc)
  hevc_file_size += 80 # Penalize HEVC bit streams for not having a container like
                       # other formats do. Came up with this number because a
                       # 1x1 pixel hevc file is 84 bytes.
  yuv_png = hevc_yuv + ".png"
  yuv_to_png(get_png_width(png), get_png_height(png), hevc_yuv, yuv_png)
  qscore = quality_score(quality_test, png, yuv_png, png_yuv, hevc_yuv)
  os.remove(png_yuv)
  os.remove(yuv_hevc)
  os.remove(hevc_yuv)
  os.remove(yuv_png)
  return (qscore, hevc_file_size)

def get_jxr_results(quality_test, png, jxr_quality):
  png_yuv = path_for_file_in_tmp(png) + str(jxr_quality) + ".yuv"
  png_to_yuv(png, png_yuv)
  yuv_jxr = png_yuv + ".jxr"
  cmd = "%s %d %ix%i %s %s" % (yuvjxr, jxr_quality, get_png_width(png), get_png_height(png), png_yuv, yuv_jxr)
  run_silent(cmd)
  jxr_file_size = os.path.getsize(yuv_jxr)
  jxr_yuv = yuv_jxr + ".yuv"
  cmd = "%s %s %s" % (jxryuv, yuv_jxr, jxr_yuv)
  run_silent(cmd)
  yuv_png = jxr_yuv + ".png"
  yuv_to_png(get_png_width(png), get_png_height(png), jxr_yuv, yuv_png)
  qscore = quality_score(quality_test, png, yuv_png, png_yuv, jxr_yuv)
  os.remove(png_yuv)
  os.remove(yuv_jxr)
  os.remove(jxr_yuv)
  os.remove(yuv_png)
  return (qscore, jxr_file_size)

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
    q = 0
    while q < 101:
      possible_q.append(q)
      q += 1
    return possible_q
  sys.stderr.write("Can't find quality list for format!\n")
  sys.exit(1)

def results_function_for_format(format):
  if format == 'hevc':
    return get_hevc_results
  if format == 'webp':
    return get_webp_results
  if format == 'jxr':
    return get_jxr_results
  sys.stderr.write("Can't find results function for format!\n")
  sys.exit(1)

# Each format is a tuple with name and associated functions
# Note that 'jxr' is disabled due to a lack of consistent encoding/decoding.
supported_formats = ['webp', 'hevc', 'jxr']

supported_tests = ['ssim', 'iwssim', 'psnrhvs']

def main(argv):
  if len(argv) != 5:
    print "Arg 1: format to test %s" % (supported_formats)
    print "Arg 2: image quality test to use %s" % (supported_tests)
    print "Arg 3: JPEG quality value to test (e.g. '75')."
    print "Arg 4: path to an image to test (e.g. 'images/Lenna.png')."
    print "Output is four lines: quality score, target format file size, JPEG file size, and target format to JPEG file size ratio."
    print "Output labels have no spaces so that a string split on a line produces the numeric result at index 1."
    return

  format_name = argv[1]
  if format_name not in supported_formats:
    print "Image format not supported!"
    return
  quality_list = quality_list_for_format(format_name)
  results_function = results_function_for_format(format_name)

  quality_test = argv[2]
  if quality_test not in supported_tests:
    print "Image quality test not supported!"
    return

  jpg_q = int(argv[3])
  png = argv[4]

  jpg_results = get_jpeg_results(quality_test, png, jpg_q)
  jpg_qscore = jpg_results[0]
  jpg_file_size = jpg_results[1]

  file_size = find_file_size_for_qscore(results_function, quality_test, png, quality_list, jpg_qscore)

  ratio = float(file_size) / float(jpg_file_size)

  print "%s: %s" % (quality_test, str(jpg_qscore)[:5])
  print "%s_file_size_(kb): %.1f" % (format_name, float(file_size) / 1024.0)
  print "jpeg_file_size_(kb): %.1f" % (float(jpg_file_size) / 1024.0)
  print "%s_to_jpeg_file_size_ratio: %.2f" % (format_name, ratio)

if __name__ == "__main__":
  main(sys.argv)
