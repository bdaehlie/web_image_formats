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

* ImageMagick, specifically the 'convert' utility
** http://www.imagemagick.org/
** Version 6.8.6 or higher required, earlier versions have a bug in YUV conversion.
* python
** Any version > 2.7.0 and < 3.0 is fine.
* JPEG Encoder/Decoder Library
** Recommend libjpeg-turbo over IJG libjpeg
** http://libjpeg-turbo.virtualgl.org/
** System install is used.
* HEVC-MSP Encoder/Decoder
** svn://hevc.kw.bbc.co.uk/svn/jctvc-hm
** Tested with r3923
** Place directory called "jctvc-hm" alongside this test suite.
* JPEG XR Encoding/Decoding Library
** https://jxrlib.codeplex.com/releases
** Tested with git revision cae40c1
** Place directory called "jxrlib" alongside this test suite.
* WebP Encoding/Decoding Library
** https://developers.google.com/speed/webp/download
** Tested with 0.4.0 release
** Place directory called "libwebp-0.4.0" alongside this test suite.

