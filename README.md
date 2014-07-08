# What Is This

This is a collection of software that can test the compression efficiency of various lossy compressed image formats, according to various quality metrics. It can create graphs of the test data.

# Supported Formats

* JPEG (via libjpeg-turbo)
* JPEG (via mozjpeg)
* WebP
* HEVC-MSP
* JPEG XR

# Supported Quality Metrics

* YSSIM (luma-only SSIM)
* DSSIM (luma-only, based on SSIM)
* RGB-SSIM (average of SSIM applied to R, G, and B channels)
* PSNR-HVS-M (luma-only)

# Supported Operating Systems

This test suite is developed and tested on Linux (Fedora 20) and OS X (10.9). It's probably easy to get things working on other versions of Linux and OS X. Little to no effort has gone into getting this working on Windows.

# Prerequisites

* ImageMagick, specifically the 'convert' utility
  * http://www.imagemagick.org/
  * Version 6.8.6 or higher required, earlier versions have a bug in YUV conversion.
    * Note that latest Ubuntu stable still has buggy older version. Fedora 20+ has a good version.
* python
  * Any version > 2.7.0 and < 3.0 is fine.
* gnuplot
  * http://www.gnuplot.info/
  * Any version > 4.6.0
* libjpeg-turbo
  * http://libjpeg-turbo.virtualgl.org/
  * We prefer libjpeg-turbo over IJG libjpeg
  * Tested with 1.3.1 release
  * Place directory called "libjpeg-turbo-1.3.1" alongside this test suite.
* mozjpeg
  * git clone https://github.com/mozilla/mozjpeg.git
  * Tested with latest git revision
  * Place directory called "mozjpeg" alongside this test suite.
* HEVC-MSP Encoder/Decoder
  * svn checkout http://hevc.hhi.fraunhofer.de/svn/svn_HEVCSoftware/
  * Tested with r3928
  * Place directory called "svn_HEVCSoftware" alongside this test suite.
* JPEG XR Encoding/Decoding Library
  * git clone https://git01.codeplex.com/jxrlib
  * Tested with git revision db41362ccbc7
  * Place directory called "jxrlib" alongside this test suite.
* WebP Encoding/Decoding Library
  * https://developers.google.com/speed/webp/download
  * Tested with 0.4.0 release
  * Place directory called "libwebp-0.4.0" alongside this test suite.

# Usage

1. Install required software
2. Build included encoder/decoder wrappers and metrics programs
  * OS X: ./build-osx.sh
  * Linux: ./build-linux.sh
3. Collect data for desired format and images
  * $ ./rd_collect.py jpeg images/kodak/*.png
  * $ ./rd_collect.py mozjpeg images/kodak/*.png
4. Average data from images
  * $ ./rd_average.py images/kodak/*.jpeg.out > jpeg.out
  * $ ./rd_average.py images/kodak/*.mozjpeg.out > mozjpeg.out
5. Generate graphs
  * $ ./rd_plot.py jpeg-vs-mozjpeg jpeg.out mozjpeg.out
