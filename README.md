This is a test suite assembled to test various lossy image formats. Right now it supports testing WebP, HEVC-P, and JPEG XR. Supported image quality tests are SSIM, IW-SSIM, and PSNR-HVS.

This suite was created and is maintained on OS X. It can probably work on Linux with minimal tweaking. I tried here and there to make life easier for anyone attempting this on Windows, but it'll probably be a pain to get everything working.

Install all of the requirements listed below, build whatever needs to be built in the requirements, then build every source file in './encoders' and './decoders'. Compile commands for the encoders and decoders are in comments near the top of the source files themselves, paths may need tweaking.

Requirements:

Must Have
* ImageMagick, specifically the 'convert' utility, http://www.imagemagick.org/
** Version 6.8.6 or higher required, earlier versions have a bug in YUV conversion

HEVC-MSP Support
* svn://hevc.kw.bbc.co.uk/svn/jctvc-hm

JPEG XR Support
* https://jxrlib.codeplex.com/releases

WebP Support
* https://developers.google.com/speed/webp/download

SSIM Support (C++ SSIM Implementation)
* http://mehdi.rabah.free.fr/SSIM/

PSNR-HVS Support (C++ PSNR-HVS Implementation)
* https://xiph.org/daala/

IW-SSIM Support via MATLAB script
* May only work on OS X as written now
* Requires that MATLAB be installed
* https://ece.uwaterloo.ca/~z70wang/research/iwssim/
* http://www.cns.nyu.edu/lcv/software.php
* Download the iw-ssim soure, then download the matlabPyrTools source, then put all of the files in the matlabPyrTools directory into the iw-ssim source directory so that all of the required MATLAB files are in the same directory.
