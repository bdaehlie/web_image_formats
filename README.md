This test suite tests compression for various lossy image formats:

* JPEG (via libjpeg-turbo)
* JPEG (via mozjpeg)
* WebP
* HEVC-MSP
* JPEG XR

Supported image quality metrics are:

* YSSIM (luma-only SSIM)
* DSSIM (luma-only, based on SSIM)
* RGB-SSIM (average of SSIM applied to R, G, and B channels)
* PSNR-HVS-M (luma-only)

This test suite is developed primarily on Linux, and secondarily on OS X. Little to no effort has gone into making this work on Windows.

Install all of the requirements listed below, build whatever needs to be built in the requirements, then run 'build-[platform].sh' to build encoders, decoders, and quality tests.

Requirements:

* ImageMagick, specifically the 'convert' utility
  * http://www.imagemagick.org/
  * Version 6.8.6 or higher required, earlier versions have a bug in YUV conversion.
    * Note that latest Ubuntu stable still has buggy older version. Fedora 20+ has a good version.
* python
  * Any version > 2.7.0 and < 3.0 is fine.
* libjpeg-turbo
  * http://libjpeg-turbo.virtualgl.org/
  * We prefer libjpeg-turbo over IJG libjpeg
  * Tested with 1.3.1 release
  * Place directory called "libjpeg-turbo-1.3.1" alongside this test suite.
* mozjpeg
  * git clone git@github.com:mozilla/mozjpeg.git
  * Tested with latest git revision
  * Place directory called "mozjpeg" alongside this test suite.
* HEVC-MSP Encoder/Decoder
  * svn checkout http://hevc.hhi.fraunhofer.de/svn/svn_HEVCSoftware/
  * Tested with r3928
  * Place directory called "svn_HEVCSoftware" alongside this test suite.
* JPEG XR Encoding/Decoding Library
  * git clone https://git01.codeplex.com/jxrlib
  * Tested with git revision cae40c1
  * Place directory called "jxrlib" alongside this test suite.
* WebP Encoding/Decoding Library
  * https://developers.google.com/speed/webp/download
  * Tested with 0.4.0 release
  * Place directory called "libwebp-0.4.0" alongside this test suite.
