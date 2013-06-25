This is a test suite assembled to test various lossy image formats. Right now it supports testing WebP and HEVC-P.

This suite was created and is maintained on OS X. It can probably work on Linux with minimal tweaking.

Requirements:
* opencv (install via MacPorts)
* http://hevc.kw.bbc.co.uk/git/w/jctvc-hm.git (HEVC-P encoder/decoder)
* ImageMagick (install via MacPorts)
* http://mehdi.rabah.free.fr/SSIM/ (C++ SSIM evaluation)
* https://xiph.org/daala/ (we need y4m2png and png2y4m)
* ffmpeg (install via MacPorts)
