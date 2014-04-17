# This script will build all of the binary encoders and decoders included with
# the test harness, provided you have the required libraries installed at the
# correct locations. Tweaking may be required.

cd encoders
echo "Compiling yuvjpeg..."
gcc yuvjpeg.c -std=c99 -I/opt/local/include/ -L/opt/local/lib/ -ljpeg -o yuvjpeg || { echo 'Failed!' ; exit 1; }
echo "Compiling yuvjxr..."
gcc yuvjxr.c -I../../jxrlib/jxrtestlib -I../../jxrlib/common/include -I../../jxrlib/jxrgluelib -I../../jxrlib/image/sys -D__ANSI__ -o yuvjxr -L../../jxrlib -ljpegxr -ljxrglue || { echo 'Failed!' ; exit 1; }
echo "Compiling yuvwebp..."
gcc yuvwebp.c -o yuvwebp -std=c99 -I../../libwebp-0.4.0/src/ ../../libwebp-0.4.0/src/.libs/libwebp.a -lm -pthread || { echo 'Failed!' ; exit 1; }
cd ..

cd decoders
echo "Compiling jpegyuv..."
gcc jpegyuv.c -std=c99 -I/opt/local/include/ -L/opt/local/lib/ -ljpeg -o jpegyuv || { echo 'Failed!' ; exit 1; }
echo "Compiling jxryuv..."
gcc jxryuv.c -I../../jxrlib/jxrtestlib -I../../jxrlib/common/include -I../../jxrlib/jxrgluelib -I../../jxrlib/image/sys -D__ANSI__ -o jxryuv -L../../jxrlib -ljpegxr -ljxrglue || { echo 'Failed!' ; exit 1; }
echo "Compiling webpyuv..."
gcc webpyuv.c -o webpyuv -std=c99 -I../../libwebp-0.4.0/src/ ../../libwebp-0.4.0/src/.libs/libwebp.a -lm -pthread || { echo 'Failed!' ; exit 1; }
cd ..

cd tests/rgbssim
echo "Compiling rgbssim..."
g++ rgbssim.cpp -O2 -o rgbssim -I /opt/local/include/ -I /opt/local/include/opencv/ -I /opt/local/include/opencv2/highgui/ -L/opt/local/lib/ -lopencv_core -lopencv_imgproc -lopencv_highgui || { echo 'Failed!' ; exit 1; }
cd ../..

# Not used any more, but left in case we use it again in the future.
# We now use the dssim mode in the 'ssim' program.
#cd tests/dssim
#echo "Compiling dssim..."
#g++ dssim.cpp -O2 -o dssim -I /opt/local/include/ -I /opt/local/include/opencv/ -I /opt/local/include/opencv2/highgui/ -L/opt/local/lib/ -lopencv_core -lopencv_imgproc -lopencv_highgui || { echo 'Failed!' ; exit 1; }
#cd ../..

cd tests/ssim
echo "Compiling ssim..."
gcc -o ssim vidinput.c y4m_input.c ssim.c -lm || { echo 'Failed!' ; exit 1; }
cd ../..

cd tests/psnrhvsm
echo "Compiling psnrhvsm..."
gcc -o psnrhvsm vidinput.c y4m_input.c psnrhvs.c -lm || { echo 'Failed!' ; exit 1; }
cd ../..

echo "Success building all encoders and decoders."
exit 0
