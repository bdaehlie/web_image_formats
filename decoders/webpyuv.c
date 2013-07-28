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

/* Input: WebP */
/* Output: YUV 4:2:0 */

/* gcc webpyuv.c -I/Users/josh/src/image-formats/libwebp-0.3.1/src/ -L/Users/josh/src/image-formats/libwebp-0.3.1/src/ -lwebp -o webpyuv */

#include <errno.h>
#include <stdio.h>
#include <inttypes.h>
#include <sys/stat.h>
#include <string.h>
#include <stdlib.h>

#include "webp/decode.h"

int main(int argc, char *argv[]) {
  if (argc < 2 || argc > 5) {
    fprintf(stderr, "Required arguments:\n");
    fprintf(stderr, "1. Path to WebP input file\n");
    fprintf(stderr, "2. Path to YUV (4:2:0) output file\n");
    return 1;
  }

  /* Will check these for validity when opening via 'fopen'. */
  const char *webp_path = argv[1];
  const char *yuv_path = argv[2];

  FILE *webp_fd = fopen(webp_path, "r");
  if (!webp_fd) {
    fprintf(stderr, "Invalid path to WebP file!");
    return 1;
  }
  fseek(webp_fd, 0, SEEK_END);
  long webp_buffer_size = ftell(webp_fd);
  fseek(webp_fd, 0, SEEK_SET);
  uint8_t *webp_buffer = malloc(webp_buffer_size);
  fread(webp_buffer, webp_buffer_size, 1, webp_fd);

  int image_width = 0;
  int image_height = 0;
  uint8_t *u_buffer = NULL;
  uint8_t *v_buffer = NULL;
  int y_stride = 0;
  int uv_stride = 0;
  uint8_t *y_buffer = WebPDecodeYUV(webp_buffer, webp_buffer_size,
                                    &image_width, &image_height,
                                    &u_buffer, &v_buffer,
                                    &y_stride, &uv_stride);
  if (!y_buffer) {
    fprintf(stderr, "Error decoding WebP file!\n");
    return 1;
  }

  FILE *yuv_fd = fopen(yuv_path, "wb");
  if (!yuv_fd) {
    fprintf(stderr, "Invalid path to YUV file!");
    return 1;
  }

  fwrite(y_buffer, y_stride * image_height, 1, yuv_fd);
  fwrite(u_buffer, uv_stride * image_height / 2, 1, yuv_fd);
  fwrite(v_buffer, uv_stride * image_height / 2, 1, yuv_fd);
  close(webp_fd);

  free(y_buffer);

  return 0;
}
