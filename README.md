This test suite tests compression for various lossy image formats:

* JPEG
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

Must Have
* ImageMagick, specifically the 'convert' utility
** http://www.imagemagick.org/
** Version 6.8.6 or higher required, earlier versions have a bug in YUV conversion
* python
** Any version > 2.7.0 and < 3.0 is fine.
* perl
** Any version 5.x from the past few years is probably fine.
** This is used for the in-tree 'jpgcrush' program.
* jpegtran
** Failure to install this will result in jpgcrush failure.
** Part of 'libjpeg-progs' on Ubuntu

HEVC-MSP Support
* svn://hevc.kw.bbc.co.uk/svn/jctvc-hm
** Tested with r3923

JPEG XR Support
* https://jxrlib.codeplex.com/releases
** Tested with git revision cae40c1

WebP Support
* https://developers.google.com/speed/webp/download
** Tested with 0.4.0 release

Y-SSIM Support (C)
* Included in the repository under 'tests'.
* Taken from the Xiph Daala project

RGB-SSIM Support (C++)
* Included in the repository under 'tests'.
* http://mehdi.rabah.free.fr/SSIM/

DSSIM Support (C++)
* Included in the repository under 'tests'.
* http://colecovision.eu/graphics/DSSIM/

PSNR-HVS-M Support (C)
* Included in the repository under 'tests'.
* Taken from the Xiph Daala project

