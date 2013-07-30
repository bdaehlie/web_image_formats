/*
 * Written by Josh Aas
 * Copyright (c) 2013, Mozilla Corporation
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 * 3. Neither the name of the Mozilla Corporation nor the names of its
 *    contributors may be used to endorse or promote products derived from this
 *    software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

/* Expects 4:2:0 YCbCr */

/* gcc -std=c99 yuvwebp.c -I/Users/josh/src/image-formats/libwebp-0.3.1/src/ -L/Users/josh/src/image-formats/libwebp-0.3.1/src/ -lwebp -o yuvwebp */

#include <errno.h>
#include <stdio.h>
#include <inttypes.h>
#include <sys/stat.h>
#include <string.h>
#include <stdlib.h>

#include "webp/encode.h"

int main(int argc, char *argv[]) {
  if (argc != 5) {
    fprintf(stderr, "Required arguments:\n");
    fprintf(stderr, "1. WebP quality value, 0-100\n");
    fprintf(stderr, "2. Image size (e.g. '512x512'\n");
    fprintf(stderr, "3. Path to YUV input file\n");
    fprintf(stderr, "4. Path to WebP output file\n");
    return 1;
  }

  errno = 0;

  long quality = strtol(argv[1], NULL, 10);
  if (errno != 0 || quality < 0 || quality > 100) {
    fprintf(stderr, "Invalid WebP quality value!\n");
    return 1;
  }

  const char *size = argv[2];
  char *x = strchr(size, 'x');
  if (!x && x != size && x != (x + strlen(x) - 1)) {
    fprintf(stderr, "Invalid image size input!\n");
    return 1;
  }
  long width = strtol(size, NULL, 10);
  if (errno != 0) {
    fprintf(stderr, "Invalid image size input!\n");
    return 1;
  }
  long height = strtol(x + 1, NULL, 10);
  if (errno != 0) {
    fprintf(stderr, "Invalid image size input!\n");
    return 1;
  }

  /* Will check these for validity when opening via 'fopen'. */
  const char *yuv_path = argv[3];
  const char *webp_path = argv[4];

  WebPConfig config;
  if (!WebPConfigPreset(&config, WEBP_PRESET_PHOTO, (float)quality)) {
    fprintf(stderr, "WebP library version error!\n");
    return 1;
  }

  if (!WebPValidateConfig(&config)) {
    fprintf(stderr, "WebP input configuration error!\n");
    return 1;
  }

  WebPPicture pic;
  if (!WebPPictureInit(&pic)) {
    fprintf(stderr, "Failed to init WebPPicture struct!\n");
    return 1;
  }
  pic.use_argb = 0;
  pic.colorspace = WEBP_YUV420;
  pic.width = width;
  pic.height = height;
  if (!WebPPictureAlloc(&pic)) {
    fprintf(stderr, "Failed to allocate for WebPPicture struct!\n");
    return 1;
  }

  FILE *yuv_fd = fopen(yuv_path, "r");
  if (!yuv_fd) {
    fprintf(stderr, "Invalid path to YUV file!");
    return 1;
  }
  const int uv_width = (pic.width + 1) / 2;
  const int uv_height = (pic.height + 1) / 2;
  int y;
  for (y = 0; y < pic.height; ++y) {
    if (fread(pic.y + y * pic.y_stride, pic.width, 1, yuv_fd) != 1) {
      fprintf(stderr, "Failure reading YUV file!\n");
      return 1;
    }
  }
  for (y = 0; y < uv_height; ++y) {
    if (fread(pic.u + y * pic.uv_stride, uv_width, 1, yuv_fd) != 1) {
      fprintf(stderr, "Failure reading YUV file!\n");
      return 1;
    }
  }
  for (y = 0; y < uv_height; ++y) {
    if (fread(pic.v + y * pic.uv_stride, uv_width, 1, yuv_fd) != 1) {
      fprintf(stderr, "Failure reading YUV file!\n");
      return 1;
    }
  }

  fclose(yuv_fd);

  WebPMemoryWriter writer;
  WebPMemoryWriterInit(&writer);
  pic.writer = WebPMemoryWrite;
  pic.custom_ptr = &writer;

  int ok = WebPEncode(&config, &pic);
  WebPPictureFree(&pic);
  if (!ok) {
    fprintf(stderr, "WebP encoding failed!\n");
    return 1;
  }

  FILE *webp_fd = fopen(webp_path, "wb");
  if (!webp_fd) {
    fprintf(stderr, "Invalid path to WebP file!");
    return 1;
  }
  fwrite(writer.mem, writer.size, 1, webp_fd);
  fclose(webp_fd);

  return 0;
}
