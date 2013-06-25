#!/usr/bin/python
#
# Copyright 2010 Google Inc.
#
# This code is licensed under the same terms as WebM:
#  Software License Agreement:  http://www.webmproject.org/license/software/
#  Additional IP Rights Grant:  http://www.webmproject.org/license/additional/
# -----------------------------------------------------------------------------
# Modified by Josh Aas, Mozilla Corporation

import os
import sys
import time

ssim = "/Users/josh/src/image-formats/SSIM/ssim"
cjpeg = "/opt/local/bin/cjpeg -optimize"
djpeg = "/opt/local/bin/djpeg"
chevc = "/Users/josh/src/image-formats/jctvc-hm/trunk/bin/TAppEncoderStatic"
dhevc = "/Users/josh/src/image-formats/jctvc-hm/trunk/bin"
convert = "/opt/local/bin/convert"
png2y4m = "/Users/josh/src/image-formats/daala/tools/png2y4m"
y4m2png = "/Users/josh/src/image-formats/daala/tools/y4m2png"
ffmpeg = "/opt/local/bin/ffmpeg"
hevc_config = "/Users/josh/src/image-formats/jctvc-hm/trunk/cfg/encoder_randomaccess_main.cfg"

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

def get_png_width(png_path):
  cmd = "identify -format \"%w\" %s" % (png_path)
  proc = os.popen(cmd, "r")
  return int(proc.readline().strip())

def get_png_height(png_path):
  cmd = "identify -format \"%h\" %s" % (png_path)
  proc = os.popen(cmd, "r")
  return int(proc.readline().strip())

def ssim_for_png_to_hevc(png_path, quality):
  y4m_path = png_path + ".y4m"
  cmd = "%s %s -o %s" % (png2y4m, png_path, y4m_path)
  os.system(cmd)
  png_yuv_path = png_path + ".yuv"
  cmd = "%s -y -i %s %s" % (ffmpeg, y4m_path, png_yuv_path)
  os.system(cmd)
  hevc_path = png_path + ".hevc"
  hevc_yuv_path = hevc_path + ".yuv"
  cmd = "%s -c %s -wdt %i -hgt %i -aq 1 --SAOLcuBoundary 1 -q %i -i %s -fr 50 -f 500 -b %s -o %s" % (chevc, hevc_config, get_png_width(png_path), get_png_height(png_path), quality, yuv_path, hevc_path, hevc_yuv_path)
  os.system(cmd)
  hevc_y4m_path = hevc_path + ".y4m"
  cmd = "%s -y -s %ix%i -i %s %s" % (ffmpeg, get_png_width(png_path), get_png_height(png_path), hevc_yuv_path, hevc_y4m_path)
  os.system(cmd)
  hevc_png_path = hevc_path + ".png"
  cmd = "%s %s -o %s" % (y4m2png, hevc_y4m_path, hevc_png_path)
  return ssim_float_for_images(png_path, hevc_png_path)

def main(argv):
  png = argv[1]
  filename = os.path.basename(png)
  basename = tmpdir + os.path.splitext(filename)[0]

  # Quality values we're interested in. This is essentially an optimization
  # to avoid working on every one.
  quality_values = [50, 55, 60, 65, 70, 75, 80, 85, 90, 95]

  # These lists will have one entry per quality value we're testing.
  jpeg_ssim_values = []
  jpeg_file_sizes = []

  # Each list will be 100 entries long, one for each quality option.
  hevc_ssim_values = []
  hevc_file_sizes = []

  # Calculate SSIM and file size for all JPEG quality levels.
  for q in quality_values:
    ppm =     basename + str(q) + ".ppm"
    jpg =     basename + str(q) + ".jpg"
    jpg_ppm = basename + str(q) + "_jpg.ppm"
    jpg_png = basename + str(q) + "_jpg.png"

    cmd = "%s %s %s" % (convert, png, ppm)
    os.system(cmd)
    cmd = "%s -quality %d -outfile %s %s" % (cjpeg, q, jpg, ppm)
    os.system(cmd)
    cmd = "%s -outfile %s %s" % (djpeg, jpg_ppm, jpg)
    os.system(cmd)
    cmd = "%s %s %s" % (convert, jpg_ppm, jpg_png)
    os.system(cmd)

    jpeg_ssim_values.append(ssim_float_for_images(png, jpg_png))
    jpeg_file_sizes.append(os.path.getsize(jpg))

    os.remove(ppm)
    os.remove(jpg)
    os.remove(jpg_ppm)
    os.remove(jpg_png)

  # Calculate SSIM and file size for all hevc quality levels.
  i = 0
  while i < 100:
    q = i + 1

    hevc =     basename + str(q) + ".webp"
    webp_png = basename + str(q) + "_webp.png"

    cmd = "%s -quiet -q %d %s -o %s" % (cwebp, q, png, webp)
    os.system(cmd)
    cmd = "%s %s -o %s" % (dwebp, webp, webp_png)
    os.system(cmd)

    webp_ssim_values.append(ssim_float_for_images(png, webp_png))
    webp_file_sizes.append(os.path.getsize(webp))

    os.remove(webp)
    os.remove(webp_png)

    i += 1

  # For each quality value we're interested in, calculate the size of a
  # WebP file that is equivalent to the JPEG file via interpolation.
  webp_ssim_equiv_file_sizes = []
  for s in jpeg_ssim_values:
    i = 0
    while i < 100:
      if webp_ssim_values[i] < s:
        if i == 99:
          webp_ssim_equiv_file_sizes.append(webp_file_sizes[99])
          break;
      if webp_ssim_values[i] == s:
        webp_ssim_equiv_file_sizes.append(webp_file_sizes[i])
        break
      if webp_ssim_values[i] > s:
        if i == 0:
          webp_ssim_equiv_file_sizes.append(webp_file_sizes[0])
          break
        webp_diff = webp_ssim_values[i] - webp_ssim_values[i - 1]
        if webp_diff == 0:
          webp_ssim_equiv_file_sizes.append(webp_file_sizes[i])
          break;
        jpeg_diff = s - webp_ssim_values[i - 1]
        percent = jpeg_diff / webp_diff
        webp_fs_diff = webp_file_sizes[i] - webp_file_sizes[i - 1]
        interpolated = (webp_fs_diff * percent) + webp_file_sizes[i - 1]
        # print "JPEG SSIM: " + str(s)
        # print "WebP SSIM larger: " + str(webp_ssim_values[i]) + " WebP SSIM smaller: " + str(webp_ssim_values[i - 1])
        # print "WebP file size larger: " + str(webp_file_sizes[i]) + " WebP file size smaller: " + str(webp_file_sizes[i - 1])
        # print "Interpolated file size: " + str(interpolated)
        webp_ssim_equiv_file_sizes.append(interpolated)
        break;

      i += 1

  jpeg_total_size = 0
  for fs in jpeg_file_sizes:
    jpeg_total_size += fs

  webp_total_size = 0
  for fs in webp_ssim_equiv_file_sizes:
    webp_total_size += fs

  print "File size change from JPEG to WebP at equivalent SSIM: " + str(float(webp_total_size) / float(jpeg_total_size))[:5]

if __name__ == "__main__":
  main(sys.argv)
