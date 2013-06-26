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
chevc = "/Users/josh/src/image-formats/jctvc-hm/trunk/bin/TAppEncoderStatic"
dhevc = "/Users/josh/src/image-formats/jctvc-hm/trunk/bin/TAppDecoderStatic"
png2y4m = "/Users/josh/src/image-formats/daala/tools/png2y4m"
y4m2png = "/Users/josh/src/image-formats/daala/tools/y4m2png"
ffmpeg = "/opt/local/bin/ffmpeg"

# HEVC config file
hevc_config = "/Users/josh/src/image-formats/jctvc-hm/trunk/cfg/encoder_randomaccess_main.cfg"

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

# This takes two lists, a and b, which must be of equal length.
# Lists can be integers or floats, and they don't have to match.
# Lists must contain values in ascending order, duplicates allowed.
# This also take a value in the same terms as the values in list a.
# This will interpolate a point in terms of list b based on where
# the a value falls in list a.
def interpolate(list_a, a_value, list_b):
  if (len(list_a) != len(list_b)) or (len(list_a) < 1):
    print "Unacceptable lists passed to interpolate function!"
  i = 0
  while i < len(list_a):
    if list_a[i] == a_value:
      return list_b[i]
    if list_a[i] > a_value:
      if i == 0:
        return list_b[0]
      a_diff = list_a[i] - list_a[i - 1]
      if a_diff == 0:
        return list_b[i]
      a_val_diff = a_value - list_a[i - 1]
      percent = a_val_diff / a_diff
      b_diff = list_b[i] - list_b[i - 1]
      return ((b_diff * percent) + list_b[i - 1])
    i += 1
  return list_b[len(list_b) - 1]

def get_png_width(png_path):
  cmd = "identify -format \"%%w\" %s" % (png_path)
  proc = os.popen(cmd, "r")
  return int(proc.readline().strip())

def get_png_height(png_path):
  cmd = "identify -format \"%%h\" %s" % (png_path)
  proc = os.popen(cmd, "r")
  return int(proc.readline().strip())

def png_to_hevc(in_png, quality, out_hevc):
  png_y4m = in_png + ".y4m"
  cmd = "%s %s -o %s" % (png2y4m, in_png, png_y4m)
  os.system(cmd)
  y4m_yuv = png_y4m + ".yuv"
  cmd = "%s -y -i %s %s" % (ffmpeg, png_y4m, y4m_yuv)
  os.system(cmd)
  cmd = "%s -c %s -wdt %i -hgt %i -aq 1 --SAOLcuBoundary 1 -q %i -i %s -fr 50 -f 500 -b %s" % (chevc, hevc_config, get_png_width(in_png), get_png_height(in_png), quality, y4m_yuv, out_hevc)
  os.system(cmd)
  os.remove(png_y4m)
  os.remove(y4m_yuv)

def hevc_to_png(in_hevc, out_png):
  hevc_yuv = in_hevc + ".yuv"
  cmd = "%s -b %s -o %s" % (dhevc, in_hevc, hevc_yuv)
  os.system(cmd)
  yuv_y4m = hevc_yuv + ".y4m"
  cmd = "%s -y -i %s %s" % (ffmpeg, hevc_yuv, yuv_y4m)
  os.system(cmd)
  cmd = "%s %s -o %s" % (y4m2png, yuv_y4m, out_png)
  os.system(cmd)
  os.remove(hevc_yuv)
  os.remove(yuv_y4m)