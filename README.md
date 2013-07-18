This is a test suite assembled to test various lossy image formats. Right now it supports testing WebP, HEVC-P, and JPEG-XR.

This suite was created and is maintained on OS X. It can probably work on Linux with minimal tweaking.

Requirements:
* opencv (install via MacPorts)
* svn://hevc.kw.bbc.co.uk/svn/jctvc-hm (HEVC-P encoder/decoder)
* https://jxrlib.codeplex.com/releases (JPEG-XR encoder/decoder)
* https://developers.google.com/speed/webp/download (WebP encoder/decoder)
* ImageMagick (install via MacPorts)
* http://mehdi.rabah.free.fr/SSIM/ (C++ SSIM evaluation)
