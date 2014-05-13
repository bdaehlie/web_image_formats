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

######## Paths to various programs and config files used by the tests #########
# Conversion
convert = "convert"

# Encoders and Decoders
yuvjpeg = "./encoders/yuvjpeg"
yuvmozjpeg = "./encoders/yuvmozjpeg"
yuvwebp = "./encoders/yuvwebp"
yuvjxr = "./encoders/yuvjxr"
chevc = "../svn_HEVCSoftware/trunk/bin/TAppEncoderStatic"

# Decoders
jpegyuv = "./decoders/jpegyuv"
webpyuv = "./decoders/webpyuv"
jxryuv = "./decoders/jxryuv"

# Tests
rgbssim = "./tests/rgbssim/rgbssim"
yssim = "./tests/ssim/ssim -y"
dssim = "./tests/ssim/ssim -y -d"
psnrhvsm = "./tests/psnrhvsm/psnrhvsm -y"
msssim = "./tests/msssim/msssim -y"

# HEVC config file
hevc_config = "../svn_HEVCSoftware/trunk/cfg/encoder_intra_main.cfg"

# Path to tmp dir to be used by the tests
tmpdir = "/tmp/"
###############################################################################

def run_silent(cmd):
  FNULL = open(os.devnull, 'w')
  rv = subprocess.call(shlex.split(cmd), stdout=FNULL, stderr=FNULL)
  if rv != 0:
    sys.stderr.write("Failure from subprocess:\n")
    sys.stderr.write("\t" + cmd + "\n")
    sys.stderr.write("Aborting!\n")
    sys.exit(rv)
  return rv

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

def quality_list_for_format(format):
  possible_q = []
  if format == 'jpeg' or format == 'mozjpeg':
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

def score_y_ssim(y4m1, y4m2):
  cmd = "%s %s %s" % (yssim, y4m1, y4m2)
  proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = proc.communicate()
  if proc.returncode != 0:
    sys.stderr.write("Failed process: %s\n" % (yssim))
    sys.exit(proc.returncode)
  lines = out.split(os.linesep)
  qscore = float(lines[1].rstrip()[7:])
  return qscore

def score_psnrhvsm(y4m1, y4m2):
  cmd = "%s %s %s" % (psnrhvsm, y4m1, y4m2)
  proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = proc.communicate()
  if proc.returncode != 0:
    sys.stderr.write("Failed process: %s\n" % (psnrhvsm))
    sys.exit(proc.returncode)
  lines = out.split(os.linesep)
  qscore = float(lines[1].rstrip()[7:])
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

def score_dssim(y4m1, y4m2):
  cmd = "%s %s %s" % (dssim, y4m1, y4m2)
  proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = proc.communicate()
  if proc.returncode != 0:
    sys.stderr.write("Failed process: %s\n" % (dssim))
    sys.exit(proc.returncode)
  lines = out.split(os.linesep)
  qscore = float(lines[1].rstrip()[7:])
  # Return the inverse of the distance to make this result work like the others
  return 1.0 - qscore

def score_msssim(y4m1, y4m2):
  cmd = "%s %s %s" % (msssim, y4m1, y4m2)
  proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = proc.communicate()
  if proc.returncode != 0:
    sys.stderr.write("Failed process: %s\n" % (msssim))
    sys.exit(proc.returncode)
  lines = out.split(os.linesep)
  qscore = float(lines[1].rstrip()[7:])
  return qscore

# Returns tuple containing:
#   (file_size, yssim_score, dssim_score, rgbssim_score, psnrhvsm_score, msssim_score)
def get_results(png, format, quality):
  width = get_png_width(png)
  height = get_png_height(png)

  png_yuv = path_for_file_in_tmp(png) + str(quality) + ".yuv"
  png_to_yuv(png, png_yuv)

  png_yuv_y4m = png_yuv + ".y4m"
  yuv_to_y4m(width, height, png_yuv, png_yuv_y4m)

  if format == "webp":
    png_yuv_target = png_yuv + ".webp"
    cmd = "%s %i %ix%i %s %s" % (yuvwebp, quality, width, height, png_yuv, png_yuv_target)
    run_silent(cmd)
    png_yuv_target_yuv = png_yuv_target + ".yuv"
    cmd = "%s %s %s" % (webpyuv, png_yuv_target, png_yuv_target_yuv)
    run_silent(cmd)
  elif format == "jxr":
    png_yuv_target = png_yuv + ".jxr"
    cmd = "%s %d %ix%i %s %s" % (yuvjxr, quality, width, height, png_yuv, png_yuv_target)
    run_silent(cmd)
    png_yuv_target_yuv = png_yuv_target + ".yuv"
    cmd = "%s %s %s" % (jxryuv, png_yuv_target, png_yuv_target_yuv)
    run_silent(cmd)
  elif format == "hevc":
    png_yuv_target = png_yuv + ".hevc"
    png_yuv_target_yuv = png_yuv_target + ".yuv"
    cmd = "%s -c %s -wdt %i -hgt %i -q %i -i %s -fr 50 -f 1 --SEIDecodedPictureHash 0 -b %s -o %s" % (chevc, hevc_config, width, height, quality, png_yuv, png_yuv_target, png_yuv_target_yuv)
    run_silent(cmd)
  elif format == "jpeg":
    png_yuv_target = png_yuv + ".jpg"
    cmd = "%s %i %ix%i %s %s" % (yuvjpeg, quality, width, height, png_yuv, png_yuv_target)
    run_silent(cmd)
    png_yuv_target_yuv = png_yuv_target + ".yuv"
    cmd = "%s %s %s" % (jpegyuv, png_yuv_target, png_yuv_target_yuv)
    run_silent(cmd)
  elif format == "mozjpeg":
    png_yuv_target = png_yuv + ".jpg"
    cmd = "%s %i %ix%i %s %s" % (yuvmozjpeg, quality, width, height, png_yuv, png_yuv_target)
    run_silent(cmd)
    png_yuv_target_yuv = png_yuv_target + ".yuv"
    cmd = "%s %s %s" % (jpegyuv, png_yuv_target, png_yuv_target_yuv)
    run_silent(cmd)

  png_yuv_target_yuv_y4m = png_yuv_target_yuv + ".y4m"
  yuv_to_y4m(width, height, png_yuv_target_yuv, png_yuv_target_yuv_y4m)

  png_yuv_target_yuv_png = png_yuv_target_yuv + ".png"
  yuv_to_png(width, height, png_yuv_target_yuv, png_yuv_target_yuv_png)

  target_file_size = os.path.getsize(png_yuv_target)
  if format == "hevc":
    target_file_size += 80 # Penalize HEVC bit streams for not having a container like
                           # other formats do. Came up with this number because a
                           # 1x1 pixel hevc file is 84 bytes.

  yssim_score = score_y_ssim(png_yuv_y4m, png_yuv_target_yuv_y4m)
  dssim_score = score_dssim(png_yuv_y4m, png_yuv_target_yuv_y4m)
  rgb_ssim_score = score_rgb_ssim(png, png_yuv_target_yuv_png)
  psnrhvsm_score = score_psnrhvsm(png_yuv_y4m, png_yuv_target_yuv_y4m)
  msssim_score = score_msssim(png_yuv_y4m, png_yuv_target_yuv_y4m)

  os.remove(png_yuv)
  os.remove(png_yuv_y4m)
  os.remove(png_yuv_target)
  os.remove(png_yuv_target_yuv)
  os.remove(png_yuv_target_yuv_y4m)
  os.remove(png_yuv_target_yuv_png)

  return (target_file_size, yssim_score, dssim_score, rgb_ssim_score, psnrhvsm_score, msssim_score)

def process_image(args):
  [format, png] = args;

  file = open(png + "." + format + ".out", "w")

  pixels = get_png_height(png) * get_png_width(png)

  quality_list = quality_list_for_format(format)

  i = 0
  while i < len(quality_list):
    q = quality_list[i]
    results = get_results(png, format, q)
    file.write("%d %d %s %s %s %s %s\n" % (pixels, results[0], str(results[1])[:5], str(results[2])[:5], str(results[3])[:5], str(results[4])[:5], str(results[5])[:5]))
    i += 1

  file.close()

supported_formats = ['jpeg', 'mozjpeg', 'webp', 'hevc', 'jxr']

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
