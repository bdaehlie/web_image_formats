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
import shlex
from multiprocessing import Pool

# Paths to various programs used by the tests.
yuvjpeg = "./encoders/yuvjpeg"
jpegyuv = "./decoders/jpegyuv"
jpgcrush = "./encoders/jpgcrush/jpgcrush"
yuvwebp = "./encoders/yuvwebp"
webpyuv = "./decoders/webpyuv"
yuvjxr = "./encoders/yuvjxr"
jxryuv = "./decoders/jxryuv"
convert = "convert"
chevc = "../jctvc-hm/trunk/bin/TAppEncoderStatic"
rgbssim = "./tests/rgbssim/rgbssim"
dssim = "./tests/dssim/dssim"
psnrhvsm = "./tests/psnrhvsm/psnrhvsm"
yssim = "./tests/ssim/ssim"

# HEVC config file
hevc_config = "../jctvc-hm/trunk/cfg/encoder_intra_main.cfg"

# Path to tmp dir to be used by the tests.
tmpdir = "/tmp/"

# Run a subprocess with silent non-error output
def run_silent(cmd):
  FNULL = open(os.devnull, 'w')
  rv = subprocess.call(shlex.split(cmd), stdout=FNULL, stderr=FNULL)
  if rv != 0:
    sys.stderr.write("Failure from subprocess:\n")
    sys.stderr.write("\t" + cmd + "\n")
    sys.stderr.write("Aborting!")
    sys.exit(rv)
  return rv

def score_y_ssim(width, height, yuv1, yuv2):
  yuv_y4m1 = yuv1 + ".y4m"
  yuv_to_y4m(width, height, yuv1, yuv_y4m1)
  yuv_y4m2 = yuv2 + ".y4m"
  yuv_to_y4m(width, height, yuv2, yuv_y4m2)
  cmd = "%s -y %s %s" % (yssim, yuv_y4m1, yuv_y4m2)
  proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = proc.communicate()
  if proc.returncode != 0:
    sys.stderr.write("Failed process: %s\n" % (psnrhvsm))
    sys.exit(proc.returncode)
  lines = out.split(os.linesep)
  qscore = float(lines[1][7:13])
  os.remove(yuv_y4m1)
  os.remove(yuv_y4m2)
  return qscore

def score_psnrhvsm(width, height, yuv1, yuv2):
  yuv_y4m1 = yuv1 + ".y4m"
  yuv_to_y4m(width, height, yuv1, yuv_y4m1)
  yuv_y4m2 = yuv2 + ".y4m"
  yuv_to_y4m(width, height, yuv2, yuv_y4m2)
  cmd = "%s -y %s %s" % (psnrhvsm, yuv_y4m1, yuv_y4m2)
  proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = proc.communicate()
  if proc.returncode != 0:
    sys.stderr.write("Failed process: %s\n" % (psnrhvsm))
    sys.exit(proc.returncode)
  lines = out.split(os.linesep)
  qscore = float(lines[1][7:13])
  os.remove(yuv_y4m1)
  os.remove(yuv_y4m2)
  return qscore

def score_rgb_ssim(png1, png2):
  cmd = "%s %s %s" % (rgbssim, png1, png2)
  proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = proc.communicate()
  if proc.returncode != 0:
    sys.stderr.write("Failed process: %s\n" % (rgbssim))
    sys.exit(proc.returncode)
  lines = out.split(os.linesep)
  r = float(lines[1].strip().strip('%'))
  g = float(lines[2].strip().strip('%'))
  b = float(lines[3].strip().strip('%'))
  return (((r + g + b) / 3) / 100)

def score_dssim(png1, png2):
  cmd = "%s %s %s" % (dssim, png1, png2)
  proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = proc.communicate()
  if proc.returncode != 0:
    sys.stderr.write("Failed process: %s\n" % (dssim))
    sys.exit(proc.returncode)
  lines = out.split(os.linesep)
  d = float(lines[0].strip())
  # Return the inverse of the distance to make this result work like the others
  return 1.0 - d

def path_for_file_in_tmp(path):
  return tmpdir + str(os.getpid()) + os.path.basename(path)

def get_png_width(path):
  cmd = "identify -format \"%%w\" %s" % (path)
  proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = proc.communicate()
  if proc.returncode != 0:
    sys.stderr.write("Failed process: identify\n")
    sys.exit(proc.returncode)
  lines = out.split(os.linesep)
  return int(lines[0].strip())

def get_png_height(path):
  cmd = "identify -format \"%%h\" %s" % (path)
  proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = proc.communicate()
  if proc.returncode != 0:
    sys.stderr.write("Failed process: identify\n")
    sys.exit(proc.returncode)
  lines = out.split(os.linesep)
  return int(lines[0].strip())

def process_image(args):
  [format, png] = args;

  file = open(png + "." + format + ".out", "w")

  pixels = get_png_height(png) * get_png_width(png)

  i = 0
  quality_list = quality_list_for_format(format)
  results_function = results_function_for_format(format)
  while i < len(quality_list):
    q = quality_list[i]
    results = results_function(png, q)
    file.write("%d %d %s %s %s %s\n" % (pixels, results[0], str(results[1])[:5], str(results[2])[:5], str(results[3])[:5], str(results[4])[:5]))
    i += 1

  file.close()

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

def get_jpeg_results(png, quality):
  png_yuv = path_for_file_in_tmp(png) + str(quality) + ".yuv"
  png_to_yuv(png, png_yuv)
  yuv_jpg = png_yuv + ".jpg"
  cmd = "%s %i %ix%i %s %s" % (yuvjpeg, quality, get_png_width(png), get_png_height(png), png_yuv, yuv_jpg)
  run_silent(cmd)
  cmd = "%s %s" % (jpgcrush, yuv_jpg)
  run_silent(cmd)
  jpg_yuv = yuv_jpg + ".yuv"
  cmd = "%s %s %s" % (jpegyuv, yuv_jpg, jpg_yuv)
  run_silent(cmd)
  yuv_png = jpg_yuv + ".png"
  yuv_to_png(get_png_width(png), get_png_height(png), jpg_yuv, yuv_png)

  jpeg_file_size = os.path.getsize(yuv_jpg)

  yssim_score = score_y_ssim(get_png_width(png), get_png_height(png), png_yuv, jpg_yuv)
  dssim_score = score_dssim(png, yuv_png)
  rgb_ssim_score = score_rgb_ssim(png, yuv_png)
  psnrhvsm_score = score_psnrhvsm(get_png_width(png), get_png_height(png), png_yuv, jpg_yuv)

  os.remove(png_yuv)
  os.remove(yuv_jpg)
  os.remove(jpg_yuv)
  os.remove(yuv_png)

  return (jpeg_file_size, yssim_score, dssim_score, rgb_ssim_score, psnrhvsm_score)

def get_webp_results(png, quality):
  png_yuv = path_for_file_in_tmp(png) + str(quality) + ".yuv"
  png_to_yuv(png, png_yuv)
  yuv_webp = png_yuv + ".webp"
  cmd = "%s %i %ix%i %s %s" % (yuvwebp, quality, get_png_width(png), get_png_height(png), png_yuv, yuv_webp)
  run_silent(cmd)
  webp_yuv = yuv_webp + ".yuv"
  cmd = "%s %s %s" % (webpyuv, yuv_webp, webp_yuv)
  run_silent(cmd)
  yuv_png = webp_yuv + ".png"
  yuv_to_png(get_png_width(png), get_png_height(png), webp_yuv, yuv_png)

  webp_file_size = os.path.getsize(yuv_webp)

  yssim_score = score_y_ssim(get_png_width(png), get_png_height(png), png_yuv, webp_yuv)
  dssim_score = score_dssim(png, yuv_png)
  rgb_ssim_score = score_rgb_ssim(png, yuv_png)
  psnrhvsm_score = score_psnrhvsm(get_png_width(png), get_png_height(png), png_yuv, webp_yuv)

  os.remove(png_yuv)
  os.remove(yuv_webp)
  os.remove(webp_yuv)
  os.remove(yuv_png)

  return (webp_file_size, yssim_score, dssim_score, rgb_ssim_score, psnrhvsm_score)

def get_hevc_results(png, quality):
  png_yuv = path_for_file_in_tmp(png) + str(quality) + ".yuv"
  png_to_yuv(png, png_yuv)
  yuv_hevc = png_yuv + ".hevc"
  hevc_yuv = yuv_hevc + ".yuv"
  cmd = "%s -c %s -wdt %i -hgt %i -q %i -i %s -fr 50 -f 1 --SEIDecodedPictureHash 0 -b %s -o %s" % (chevc, hevc_config, get_png_width(png), get_png_height(png), quality, png_yuv, yuv_hevc, hevc_yuv)
  run_silent(cmd)
  yuv_png = hevc_yuv + ".png"
  yuv_to_png(get_png_width(png), get_png_height(png), hevc_yuv, yuv_png)

  hevc_file_size = os.path.getsize(yuv_hevc)
  hevc_file_size += 80 # Penalize HEVC bit streams for not having a container like
                       # other formats do. Came up with this number because a
                       # 1x1 pixel hevc file is 84 bytes.

  yssim_score = score_y_ssim(get_png_width(png), get_png_height(png), png_yuv, hevc_yuv)
  dssim_score = score_dssim(png, yuv_png)
  rgb_ssim_score = score_rgb_ssim(png, yuv_png)
  psnrhvsm_score = score_psnrhvsm(get_png_width(png), get_png_height(png), png_yuv, hevc_yuv)

  os.remove(png_yuv)
  os.remove(yuv_hevc)
  os.remove(hevc_yuv)
  os.remove(yuv_png)

  return (hevc_file_size, yssim_score, dssim_score, rgb_ssim_score, psnrhvsm_score)

def get_jxr_results(png, quality):
  png_yuv = path_for_file_in_tmp(png) + str(quality) + ".yuv"
  png_to_yuv(png, png_yuv)
  yuv_jxr = png_yuv + ".jxr"
  cmd = "%s %d %ix%i %s %s" % (yuvjxr, quality, get_png_width(png), get_png_height(png), png_yuv, yuv_jxr)
  run_silent(cmd)
  jxr_yuv = yuv_jxr + ".yuv"
  cmd = "%s %s %s" % (jxryuv, yuv_jxr, jxr_yuv)
  run_silent(cmd)
  yuv_png = jxr_yuv + ".png"
  yuv_to_png(get_png_width(png), get_png_height(png), jxr_yuv, yuv_png)

  jxr_file_size = os.path.getsize(yuv_jxr)

  yssim_score = score_y_ssim(get_png_width(png), get_png_height(png), png_yuv, jxr_yuv)
  dssim_score = score_dssim(png, yuv_png)
  rgb_ssim_score = score_rgb_ssim(png, yuv_png)
  psnrhvsm_score = score_psnrhvsm(get_png_width(png), get_png_height(png), png_yuv, jxr_yuv)

  os.remove(png_yuv)
  os.remove(yuv_jxr)
  os.remove(jxr_yuv)
  os.remove(yuv_png)

  return (jxr_file_size, yssim_score, dssim_score, rgb_ssim_score, psnrhvsm_score)

def quality_list_for_format(format):
  possible_q = []
  if format == 'jpeg':
    q = 0
    while q < 101:
      possible_q.append(q)
      q += 1
    return possible_q
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
    while q < 100:
      possible_q.append(q)
      q += 1
    return possible_q
  sys.stderr.write("Can't find quality list for format!\n")
  sys.exit(1)

# All of these functions return tuples containing:
#   (file_size, yssim_score, dssim_score, rgbssim_score, psnrhvsm_score)
def results_function_for_format(format):
  if format == 'jpeg':
    return get_jpeg_results
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
supported_formats = ['jpeg', 'webp', 'hevc', 'jxr']

def main(argv):
  if len(argv) < 3:
    print "Arg 1: format to test %s" % (supported_formats)
    print "Arg 2+: paths to images to test (e.g. 'images/Lenna.png')"
    return

  format = argv[1]
  if format not in supported_formats:
    print "Image format not supported!"
    return

  Pool().map(process_image, [(format, png) for png in argv[2:]])

if __name__ == "__main__":
  main(sys.argv)

