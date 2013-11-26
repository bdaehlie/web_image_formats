/*
	This DSSIM program has been created by Philipp Klaus Krause based on
	Rabah Mehdi's C++ implementation of SSIM (http://mehdi.rabah.free.fr/SSIM).
	Originally it has been created for the VMV '09 paper
	"ftc - floating precision texture compression" by Philipp Klaus Krause.

	The latest version of this program can probably be found somewhere at
	http://www.colecovision.eu.

	It can be compiled using g++ -I/usr/include/opencv -lcv -lhighgui dssim.cpp
	Make sure OpenCV is installed (e.g. for Debian/ubuntu: apt-get install
	libcv-dev libhighgui-dev).

	DSSIM is described in
	"Structural Similarity-Based Object Tracking in Video Sequences" by Loza et al.
	however setting all Ci to 0 as proposed there results in numerical instabilities.
	Thus this implementation used the Ci from the SSIM implementation.
	SSIM is described in
	"Image quality assessment: from error visibility to structural similarity" by Wang et al.
*/

/*
	Copyright (c) 2005, Rabah Mehdi <mehdi.rabah@gmail.com>

	Feel free to use it as you want and to drop me a mail
	if it has been useful to you. Please let me know if you enhance it.
	I'm not responsible if this program destroy your life & blablabla :)

	Copyright (c) 2009, Philipp Klaus Krause <philipp@colecovision.eu>

	Permission to use, copy, modify, and/or distribute this software for any
	purpose with or without fee is hereby granted, provided that the above
	copyright notice and this permission notice appear in all copies.

	THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
	WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
	MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
	ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
	WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
	ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
	OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
*/

#include <cv.h>	
#include <highgui_c.h>
#include <iostream>
#include <algorithm>

using namespace std;

int main(int argc, char** argv)
{
	if(argc!=3)
	{
		std::cerr << "Usage: dssim image0 image1\n";
		return(-1);
	}
	
	// default settings
	double C1 = 6.5025, C2 = 58.5225;

	IplImage
		*img1=NULL, *img2=NULL, *img1_img2=NULL,
		*img1_temp=NULL, *img2_temp=NULL,
		*img1_sq=NULL, *img2_sq=NULL,
		*mu1=NULL, *mu2=NULL,
		*mu1_sq=NULL, *mu2_sq=NULL, *mu1_mu2=NULL,
		*sigma1_sq=NULL, *sigma2_sq=NULL, *sigma12=NULL,
		*ssim_map=NULL, *temp1=NULL, *temp2=NULL, *temp3=NULL;
	

	/***************************** INITS **********************************/
	img1_temp = cvLoadImage(argv[1], CV_LOAD_IMAGE_ANYCOLOR);
	img2_temp = cvLoadImage(argv[2], CV_LOAD_IMAGE_ANYCOLOR);

	if(!img1_temp)
	{
		std::cerr << "Could not read image file " << argv[1] << "\n";
		return(-1);
	}

	if(!img2_temp)
	{
		std::cerr << "Could not read image file " << argv[2] << "\n";
		return(-1);
	}

	int x=img1_temp->width, y=img1_temp->height;
	int nChan=img1_temp->nChannels, d=IPL_DEPTH_32F;
	CvSize size = cvSize(x, y);

	img1 = cvCreateImage( size, d, nChan);
	img2 = cvCreateImage( size, d, nChan);

	cvConvert(img1_temp, img1);
	cvConvert(img2_temp, img2);
	cvReleaseImage(&img1_temp);
	cvReleaseImage(&img2_temp);

	
	img1_sq = cvCreateImage( size, d, nChan);
	img2_sq = cvCreateImage( size, d, nChan);
	img1_img2 = cvCreateImage( size, d, nChan);
	
	cvPow( img1, img1_sq, 2 );
	cvPow( img2, img2_sq, 2 );
	cvMul( img1, img2, img1_img2, 1 );

	mu1 = cvCreateImage( size, d, nChan);
	mu2 = cvCreateImage( size, d, nChan);

	mu1_sq = cvCreateImage( size, d, nChan);
	mu2_sq = cvCreateImage( size, d, nChan);
	mu1_mu2 = cvCreateImage( size, d, nChan);
	

	sigma1_sq = cvCreateImage( size, d, nChan);
	sigma2_sq = cvCreateImage( size, d, nChan);
	sigma12 = cvCreateImage( size, d, nChan);

	temp1 = cvCreateImage( size, d, nChan);
	temp2 = cvCreateImage( size, d, nChan);
	temp3 = cvCreateImage( size, d, nChan);

	ssim_map = cvCreateImage( size, d, nChan);
	/*************************** END INITS **********************************/


	//////////////////////////////////////////////////////////////////////////
	// PRELIMINARY COMPUTING
	cvSmooth( img1, mu1, CV_GAUSSIAN, 11, 11, 1.5 );
	cvSmooth( img2, mu2, CV_GAUSSIAN, 11, 11, 1.5 );
	
	cvPow( mu1, mu1_sq, 2 );
	cvPow( mu2, mu2_sq, 2 );
	cvMul( mu1, mu2, mu1_mu2, 1 );


	cvSmooth( img1_sq, sigma1_sq, CV_GAUSSIAN, 11, 11, 1.5 );
	cvAddWeighted( sigma1_sq, 1, mu1_sq, -1, 0, sigma1_sq );
	
	cvSmooth( img2_sq, sigma2_sq, CV_GAUSSIAN, 11, 11, 1.5 );
	cvAddWeighted( sigma2_sq, 1, mu2_sq, -1, 0, sigma2_sq );

	cvSmooth( img1_img2, sigma12, CV_GAUSSIAN, 11, 11, 1.5 );
	cvAddWeighted( sigma12, 1, mu1_mu2, -1, 0, sigma12 );
	

	//////////////////////////////////////////////////////////////////////////
	// FORMULA

	// (2*mu1_mu2 + C1)
	cvScale( mu1_mu2, temp1, 2 );
	cvAddS( temp1, cvScalarAll(C1), temp1 );

	// (2*sigma12 + C2)
	cvScale( sigma12, temp2, 2 );
	cvAddS( temp2, cvScalarAll(C2), temp2 );

	// ((2*mu1_mu2 + C1).*(2*sigma12 + C2))
	cvMul( temp1, temp2, temp3, 1 );

	// (mu1_sq + mu2_sq + C1)
	cvAdd( mu1_sq, mu2_sq, temp1 );
	cvAddS( temp1, cvScalarAll(C1), temp1 );

	// (sigma1_sq + sigma2_sq + C2)
	cvAdd( sigma1_sq, sigma2_sq, temp2 );
	cvAddS( temp2, cvScalarAll(C2), temp2 );

	// ((mu1_sq + mu2_sq + C1).*(sigma1_sq + sigma2_sq + C2))
	cvMul( temp1, temp2, temp1, 1 );

	// ((2*mu1_mu2 + C1).*(2*sigma12 + C2))./((mu1_sq + mu2_sq + C1).*(sigma1_sq + sigma2_sq + C2))
	cvDiv( temp3, temp1, ssim_map, 1 );


	CvScalar index_scalar = cvAvg( ssim_map );

	double dssim = index_scalar.val[0];
	for(unsigned int i = 1; i < nChan; i++)
		dssim = min(dssim, index_scalar.val[i]);
	dssim = 1.0 / dssim - 1;

	std::cout.precision(3);
	std::cout << fixed << dssim << "\n";

	// if you use this code within a program
	// don't forget to release the IplImages
	return(0);
}
