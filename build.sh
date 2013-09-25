# This script will build all of the binary encoders and decoders included with
# the test harness, provided you have the required libraries installed at the
# correct locations. Tweaking may be required.

cd encoders
echo "Compiling yuvjpeg..."
gcc -std=c99 yuvjpeg.c -I/opt/local/include/ -L/opt/local/lib/ -ljpeg -o yuvjpeg || { echo 'Failed!' ; exit 1; }
echo "Compiling yuvjxr..."
gcc -I../../jxrlib/jxrtestlib -I../../jxrlib/common/include -I../../jxrlib/jxrgluelib -I../../jxrlib/image/sys -D__ANSI__ -o yuvjxr -L../../jxrlib -ljpegxr -ljxrglue yuvjxr.c  || { echo 'Failed!' ; exit 1; }
echo "Compiling yuvwebp..."
gcc -std=c99 yuvwebp.c -I/Users/josh/src/image-formats/libwebp-0.3.1/src/ -L/Users/josh/src/image-formats/libwebp-0.3.1/src/ -lwebp -o yuvwebp  || { echo 'Failed!' ; exit 1; }

cd ../decoders
echo "Compiling jpegyuv..."
gcc -std=c99 jpegyuv.c -I/opt/local/include/ -L/opt/local/lib/ -ljpeg -o jpegyuv  || { echo 'Failed!' ; exit 1; }
echo "Compiling jxryuv..."
gcc -I../../jxrlib/jxrtestlib -I../../jxrlib/common/include -I../../jxrlib/jxrgluelib -I../../jxrlib/image/sys -D__ANSI__ -o jxryuv -L../../jxrlib -ljpegxr -ljxrglue jxryuv.c  || { echo 'Failed!' ; exit 1; }
echo "Compiling webpyuv..."
gcc -std=c99 webpyuv.c -I/Users/josh/src/image-formats/libwebp-0.3.1/src/ -L/Users/josh/src/image-formats/libwebp-0.3.1/src/ -lwebp -o webpyuv  || { echo 'Failed!' ; exit 1; }

echo "Success building all encoders and decoders."
exit 0
