#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "vidinput.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#if !defined(M_PI)
# define M_PI (3.141592653589793238462643)
#endif
#include <string.h>
/*Yes, yes, we're going to hell.*/
#if defined(_WIN32)
#include <io.h>
#include <fcntl.h>
#endif
#include "getopt.h"
#include <ogg/os_types.h>

typedef ogg_int32_t od_coeff;

#define OD_UNBIASED_RSHIFT(_a, _b) ((_a)/(1<<(_b)))
#define OD_DCT_RSHIFT(_a, _b) OD_UNBIASED_RSHIFT(_a, _b)

void od_bin_fdct8(od_coeff _y[8], const od_coeff *_x, int _xstride) {
  /*31 adds, 5 shifts, 15 "muls".*/
  /*The minimum theoretical number of multiplies for a uniformly-scaled 8-point
     transform is 11, but the best I've been able to come up with for a
     reversible version with orthonormal scaling is 15.
    We pick up 3 multiplies when computing the DC, since we have an odd number
     of summation stages, leaving no chance to cancel the asymmetry in the last
     one.
    Instead, we have to implement it as a rotation by \frac{\pi}{4} using
     lifting steps.
    We pick up one more multiply when computing the Type IV DCT in the odd
     half.
    This comes from using 3 lifting steps to implement another rotation by
     \frac{\pi}{4} (with asymmetrically scaled inputs and outputs) instead of
     simply scaling two values by \sqrt{2}.*/
  int t0;
  int t1;
  int t1h;
  int t2;
  int t3;
  int t4;
  int t4h;
  int t5;
  int t6;
  int t6h;
  int t7;
  /*Initial permutation:*/
  t0 = *(_x+0*_xstride);
  t4 = *(_x+1*_xstride);
  t2 = *(_x+2*_xstride);
  t6 = *(_x+3*_xstride);
  t7 = *(_x+4*_xstride);
  t3 = *(_x+5*_xstride);
  t5 = *(_x+6*_xstride);
  t1 = *(_x+7*_xstride);
  /*+1/-1 butterflies:*/
  t1 = t0-t1;
  t1h = OD_DCT_RSHIFT(t1, 1);
  t0 -= t1h;
  t4 += t5;
  t4h = OD_DCT_RSHIFT(t4, 1);
  t5 -= t4h;
  t3 = t2-t3;
  t2 -= OD_DCT_RSHIFT(t3, 1);
  t6 += t7;
  t6h = OD_DCT_RSHIFT(t6, 1);
  t7 = t6h-t7;
  /*+ Embedded 4-point type-II DCT.*/
  t0 += t6h;
  t6 = t0-t6;
  t2 = t4h-t2;
  t4 = t2-t4;
  /*|-+ Embedded 2-point type-II DCT.*/
  /*13573/32768~=\sqrt{2}-1~=0.41421356237309504880168872420970*/
  t0 -= (t4*13573+16384)>>15;
  /*11585/16384~=\sqrt{\frac{1}{2}}~=0.70710678118654752440084436210485*/
  t4 += (t0*11585+8192)>>14;
  /*13573/32768~=\sqrt{2}-1~=0.41421356237309504880168872420970*/
  t0 -= (t4*13573+16384)>>15;
  /*|-+ Embedded 2-point type-IV DST.*/
  /*21895/32768~=\frac{1-cos(\frac{3\pi}{8})}{\sin(\frac{3\pi}{8})}~=
     0.66817863791929891999775768652308*/
  t6 -= (t2*21895+16384)>>15;
  /*15137/16384~=sin(\frac{3\pi}{8})~=0.92387953251128675612818318939679*/
  t2 += (t6*15137+8192)>>14;
  /*21895/32768~=\frac{1-cos(\frac{3\pi}{8})}{\sin(\frac{3\pi}{8})}~=
     0.66817863791929891999775768652308*/
  t6 -= (t2*21895+16384)>>15;
  /*+ Embedded 4-point type-IV DST.*/
  /*19195/32768~=2-\sqrt{2}~=0.58578643762690495119831127579030*/
  t3 += (t5*19195+16384)>>15;
  /*11585/16384~=\sqrt{\frac{1}{2}}~=0.70710678118654752440084436210485*/
  t5 += (t3*11585+8192)>>14;
  /*29957/32768~=\sqrt{2}-\frac{1}{2}~=0.91421356237309504880168872420970*/
  t3 -= (t5*29957+16384)>>15;
  t7 = OD_DCT_RSHIFT(t5, 1)-t7;
  t5 -= t7;
  t3 = t1h-t3;
  t1 -= t3;
  /*3227/32768~=\frac{1-cos(\frac{\pi}{16})}{sin(\frac{\pi}{16})}~=
     0.098491403357164253077197521291327*/
  t7 += (t1*3227+16384)>>15;
  /*6393/32768~=sin(\frac{\pi}{16})~=0.19509032201612826784828486847702*/
  t1 -= (t7*6393+16384)>>15;
  /*3227/32768~=\frac{1-cos(\frac{\pi}{16})}{sin(\frac{\pi}{16})}~=
     0.098491403357164253077197521291327*/
  t7 += (t1*3227+16384)>>15;
  /*2485/8192~=\frac{1-cos(\frac{3\pi}{16})}{sin(\frac{3\pi}{16})}~=
     0.30334668360734239167588394694130*/
  t5 += (t3*2485+4096)>>13;
  /*18205/32768~=sin(\frac{3\pi}{16})~=0.55557023301960222474283081394853*/
  t3 -= (t5*18205+16384)>>15;
  /*2485/8192~=\frac{1-cos(\frac{3\pi}{16})}{sin(\frac{3\pi}{16})}~=
     0.30334668360734239167588394694130*/
  t5 += (t3*2485+4096)>>13;
  _y[0] = (od_coeff)t0;
  _y[1] = (od_coeff)t1;
  _y[2] = (od_coeff)t2;
  _y[3] = (od_coeff)t3;
  _y[4] = (od_coeff)t4;
  _y[5] = (od_coeff)t5;
  _y[6] = (od_coeff)t6;
  _y[7] = (od_coeff)t7;
}

void od_bin_fdct8x8(od_coeff *_y, int _ystride, const od_coeff *_x,
 int _xstride) {
  od_coeff z[8*8];
  int      i;
  for (i = 0; i < 8; i++) od_bin_fdct8(z+8*i, _x+i, _xstride);
  for (i = 0; i < 8; i++) od_bin_fdct8(_y+_ystride*i, z+i, 8);
}

const char *optstring = "frsy";
const struct option options[]={
  {"frame-type",no_argument,NULL,'f'},
  {"raw",no_argument,NULL,'r'},
  {"summary",no_argument,NULL,'s'},
  {"luma-only",no_argument,NULL,'y'},
  {NULL,0,NULL,0}
};

static int show_frame_type;
static int summary_only;
static int luma_only;

/*Normalized inverse quantization matrix for 8x8 DCT at the point of transparency.
  This is not the JPEG based matrix from the paper,
  this one gives a slightly higher MOS agreement.*/
float csf_y[8][8]={{1.6193873005, 2.2901594831, 2.08509755623, 1.48366094411, 1.00227514334, 0.678296995242, 0.466224900598, 0.3265091542},
                 {2.2901594831, 1.94321815382, 2.04793073064, 1.68731108984, 1.2305666963, 0.868920337363, 0.61280991668, 0.436405793551},
                 {2.08509755623, 2.04793073064, 1.34329019223, 1.09205635862, 0.875748795257, 0.670882927016, 0.501731932449, 0.372504254596},
                 {1.48366094411, 1.68731108984, 1.09205635862, 0.772819797575, 0.605636379554, 0.48309405692, 0.380429446972, 0.295774038565},
                 {1.00227514334, 1.2305666963, 0.875748795257, 0.605636379554, 0.448996256676, 0.352889268808, 0.283006984131, 0.226951348204},
                 {0.678296995242, 0.868920337363, 0.670882927016, 0.48309405692, 0.352889268808, 0.27032073436, 0.215017739696, 0.17408067321},
                 {0.466224900598, 0.61280991668, 0.501731932449, 0.380429446972, 0.283006984131, 0.215017739696, 0.168869545842, 0.136153931001},
                 {0.3265091542, 0.436405793551, 0.372504254596, 0.295774038565, 0.226951348204, 0.17408067321, 0.136153931001, 0.109083846276}};
float csf_cb420[8][8]={{1.91113096927, 2.46074210438, 1.18284184739, 1.14982565193, 1.05017074788, 0.898018824055, 0.74725392039, 0.615105596242},
                       {2.46074210438, 1.58529308355, 1.21363250036, 1.38190029285, 1.33100189972, 1.17428548929, 0.996404342439, 0.830890433625},
                       {1.18284184739, 1.21363250036, 0.978712413627, 1.02624506078, 1.03145147362, 0.960060382087, 0.849823426169, 0.731221236837},
                       {1.14982565193, 1.38190029285, 1.02624506078, 0.861317501629, 0.801821139099, 0.751437590932, 0.685398513368, 0.608694761374},
                       {1.05017074788, 1.33100189972, 1.03145147362, 0.801821139099, 0.676555426187, 0.605503172737, 0.55002013668, 0.495804539034},
                       {0.898018824055, 1.17428548929, 0.960060382087, 0.751437590932, 0.605503172737, 0.514674450957, 0.454353482512, 0.407050308965},
                       {0.74725392039, 0.996404342439, 0.849823426169, 0.685398513368, 0.55002013668, 0.454353482512, 0.389234902883, 0.342353999733},
                       {0.615105596242, 0.830890433625, 0.731221236837, 0.608694761374, 0.495804539034, 0.407050308965, 0.342353999733, 0.295530605237}};
float csf_cr420[8][8]={{2.03871978502, 2.62502345193, 1.26180942886, 1.11019789803, 1.01397751469, 0.867069376285, 0.721500455585, 0.593906509971},
                       {2.62502345193, 1.69112867013, 1.17180569821, 1.3342742857, 1.28513006198, 1.13381474809, 0.962064122248, 0.802254508198},
                       {1.26180942886, 1.17180569821, 0.944981930573, 0.990876405848, 0.995903384143, 0.926972725286, 0.820534991409, 0.706020324706},
                       {1.11019789803, 1.3342742857, 0.990876405848, 0.831632933426, 0.77418706195, 0.725539939514, 0.661776842059, 0.587716619023},
                       {1.01397751469, 1.28513006198, 0.995903384143, 0.77418706195, 0.653238524286, 0.584635025748, 0.531064164893, 0.478717061273},
                       {0.867069376285, 1.13381474809, 0.926972725286, 0.725539939514, 0.584635025748, 0.496936637883, 0.438694579826, 0.393021669543},
                       {0.721500455585, 0.962064122248, 0.820534991409, 0.661776842059, 0.531064164893, 0.438694579826, 0.375820256136, 0.330555063063},
                       {0.593906509971, 0.802254508198, 0.706020324706, 0.587716619023, 0.478717061273, 0.393021669543, 0.330555063063, 0.285345396658}};

static double calc_psnrhvs(const unsigned char *_src,int _systride,
 const unsigned char *_dst,int _dystride,double _par,int _w,int _h, int _step, float _csf[8][8]){
  float    ret;
  od_coeff dct_s[8*8];
  od_coeff dct_d[8*8];
  float mask[8][8];
  int pixels;
  int x;
  int y;
  (void)_par;
  ret=pixels=0;
  /*In the PSNR-HVS-M paper[1] the authors describe the construction of
     their masking table as "we have used the quantization table for the
     color component Y of JPEG [6] that has been also obtained on the
     basis of CSF. Note that the values in quantization table JPEG have
     been normalized and then squared." Their CSF matrix (from PSNR-HVS)
     was also constructed from the JPEG matrices. I can not find any obvious
     scheme of normalizing to produce their table, but if I multiply their
     CSF by 0.38857 and square the result I get their masking table.
     I have no idea where this constant comes from, but deviating from it
     too greatly hurts MOS agreement.

    [1] Nikolay Ponomarenko, Flavia Silvestri, Karen Egiazarian, Marco Carli,
        Jaakko Astola, Vladimir Lukin, "On between-coefficient contrast masking
        of DCT basis functions", CD-ROM Proceedings of the Third
        International Workshop on Video Processing and Quality Metrics for Consumer
        Electronics VPQM-07, Scottsdale, Arizona, USA, 25-26 January, 2007, 4 p.*/
  for(x=0;x<8;x++)for(y=0;y<8;y++)mask[x][y]=(_csf[x][y]*0.3885746225901003)*(_csf[x][y]*0.3885746225901003);
  for(y=0;y<_h-7;y+=_step){
    for(x=0;x<_w-7;x+=_step){
      int i;
      int j;
      float s_means[4];
      float d_means[4];
      float s_vars[4];
      float d_vars[4];
      float s_gmean=0;
      float d_gmean=0;
      float s_gvar=0;
      float d_gvar=0;
      float s_mask=0;
      float d_mask=0;
      for(i=0;i<4;i++)s_means[i]=d_means[i]=s_vars[i]=d_vars[i]=0;
      for(i=0;i<8;i++){
        for(j=0;j<8;j++){
          int sub=((i&12)>>2)+((j&12)>>1);
          dct_s[i*8+j]=_src[(y+i)*_systride+(j+x)];
          dct_d[i*8+j]=_dst[(y+i)*_dystride+(j+x)];
          s_gmean+=dct_s[i*8+j];
          d_gmean+=dct_d[i*8+j];
          s_means[sub]+=dct_s[i*8+j];
          d_means[sub]+=dct_d[i*8+j];
        }
      }
      s_gmean/=64.f;
      d_gmean/=64.f;
      for(i=0;i<4;i++)s_means[i]/=16.f;
      for(i=0;i<4;i++)d_means[i]/=16.f;
      for(i=0;i<8;i++){
        for(j=0;j<8;j++){
          int sub=((i&12)>>2)+((j&12)>>1);
          s_gvar+=(dct_s[i*8+j]-s_gmean)*(dct_s[i*8+j]-s_gmean);
          d_gvar+=(dct_d[i*8+j]-d_gmean)*(dct_d[i*8+j]-d_gmean);
          s_vars[sub]+=(dct_s[i*8+j]-s_means[sub])*(dct_s[i*8+j]-s_means[sub]);
          d_vars[sub]+=(dct_d[i*8+j]-d_means[sub])*(dct_d[i*8+j]-d_means[sub]);
        }
      }
      s_gvar*=1/63.f*64;
      d_gvar*=1/63.f*64;
      for(i=0;i<4;i++)s_vars[i]*=1/15.f*16;
      for(i=0;i<4;i++)d_vars[i]*=1/15.f*16;
      if(s_gvar>0)s_gvar=(s_vars[0]+s_vars[1]+s_vars[2]+s_vars[3])/s_gvar;
      if(d_gvar>0)d_gvar=(d_vars[0]+d_vars[1]+d_vars[2]+d_vars[3])/d_gvar;
      od_bin_fdct8x8(dct_s,8,dct_s,8);
      od_bin_fdct8x8(dct_d,8,dct_d,8);
      for(i=0;i<8;i++)for(j=(i==0);j<8;j++)s_mask+=dct_s[i*8+j]*dct_s[i*8+j]*mask[i][j];
      for(i=0;i<8;i++)for(j=(i==0);j<8;j++)d_mask+=dct_d[i*8+j]*dct_d[i*8+j]*mask[i][j];
      s_mask=sqrt(s_mask*s_gvar)/32.f;
      d_mask=sqrt(d_mask*d_gvar)/32.f;
      if(d_mask>s_mask)s_mask=d_mask;
      for(i=0;i<8;i++){
        for(j=0;j<8;j++){
          float err;
          err=fabs(dct_s[i*8+j]-dct_d[i*8+j]);
          if(i!=0||j!=0)err=err<s_mask/mask[i][j]?0:err-s_mask/mask[i][j];
          ret+=(err*_csf[i][j])*(err*_csf[i][j]);
          pixels++;
        }
      }
    }
  }
  ret/=pixels;
  return ret;
}

static void usage(char *_argv[]){
  fprintf(stderr,"Usage: %s [options] <video1> <video2>\n"
   "    <video1> and <video2> may be either YUV4MPEG or Ogg Theora files.\n\n"
   "    Options:\n\n"
   "      -f --frame-type Show frame type and QI value for each Theora frame.\n"
   "      -s --summary    Only output the summary line.\n"
   "      -y --luma-only  Only output values for the luma channel.\n",_argv[0]);
}

static double convert_score_db(double _score,double _weight){
  return 10*(log10(255*255)-log10(_weight*_score));
}

int main(int _argc,char *_argv[]){
  video_input vid1;
  video_input_info info1;
  video_input vid2;
  video_input_info info2;
  double gssim[3];
  double cweight;
  double par;
  int frameno;
  FILE *fin;
  int long_option_index;
  int c;
#ifdef _WIN32
  /*We need to set stdin/stdout to binary mode on windows.
    Beware the evil ifdef.
    We avoid these where we can, but this one we cannot.
    Don't add any more, you'll probably go to hell if you do.*/
  _setmode(_fileno(stdin),_O_BINARY);
#endif
  /*Process option arguments.*/
  while((c=getopt_long(_argc,_argv,optstring,options,&long_option_index))!=EOF){
    switch(c){
      case 'f':show_frame_type=1;break;
      case 's':summary_only=1;break;
      case 'y':luma_only=1;break;
      default:{
        usage(_argv);
        exit(EXIT_FAILURE);
      }break;
    }
  }
  if(optind+2!=_argc){
    usage(_argv);
    exit(EXIT_FAILURE);
  }
  fin=strcmp(_argv[optind],"-")==0?stdin:fopen(_argv[optind],"rb");
  if(fin==NULL){
    fprintf(stderr,"Unable to open '%s' for extraction.\n",_argv[optind]);
    exit(EXIT_FAILURE);
  }
  fprintf(stderr,"Opening %s...\n",_argv[optind]);
  if(video_input_open(&vid1,fin)<0)exit(EXIT_FAILURE);
  video_input_get_info(&vid1,&info1);
  fin=strcmp(_argv[optind+1],"-")==0?stdin:fopen(_argv[optind+1],"rb");
  if(fin==NULL){
    fprintf(stderr,"Unable to open '%s' for extraction.\n",_argv[optind+1]);
    exit(EXIT_FAILURE);
  }
  fprintf(stderr,"Opening %s...\n",_argv[optind+1]);
  if(video_input_open(&vid2,fin)<0)exit(EXIT_FAILURE);
  video_input_get_info(&vid2,&info2);
  /*Check to make sure these videos are compatible.*/
  if(info1.pic_w!=info2.pic_w||info1.pic_h!=info2.pic_h){
    fprintf(stderr,"Video resolution does not match.\n");
    exit(EXIT_FAILURE);
  }
  if(info1.pixel_fmt!=info2.pixel_fmt){
    fprintf(stderr,"Pixel formats do not match.\n");
    exit(EXIT_FAILURE);
  }
  if((info1.pic_x&!(info1.pixel_fmt&1))!=(info2.pic_x&!(info2.pixel_fmt&1))||
   (info1.pic_y&!(info1.pixel_fmt&2))!=(info2.pic_y&!(info2.pixel_fmt&2))){
    fprintf(stderr,"Chroma subsampling offsets do not match.\n");
    exit(EXIT_FAILURE);
  }
  if(info1.fps_n*(ogg_int64_t)info2.fps_d!=
   info2.fps_n*(ogg_int64_t)info1.fps_d){
    fprintf(stderr,"Warning: framerates do not match.\n");
  }
  if(info1.par_n*(ogg_int64_t)info2.par_d!=
   info2.par_n*(ogg_int64_t)info1.par_d){
    fprintf(stderr,"Warning: aspect ratios do not match.\n");
  }
  par=info1.par_n>0&&info2.par_d>0?
   info1.par_n/(double)info2.par_d:1;
  gssim[0]=gssim[1]=gssim[2]=0;
  /*We just use a simple weighting to get a single full-color score.
    In reality the CSF for chroma is not the same as luma.*/
  cweight=0.25*(4>>!(info1.pixel_fmt&1)+!(info1.pixel_fmt&2));
  for(frameno=0;;frameno++){
    video_input_ycbcr f1;
    video_input_ycbcr f2;
    double ssim[3];
    char tag1[5];
    char tag2[5];
    int ret1;
    int ret2;
    int pli;
    ret1=video_input_fetch_frame(&vid1,f1,tag1);
    ret2=video_input_fetch_frame(&vid2,f2,tag2);
    if(ret1==0&&ret2==0)break;
    else if(ret1<0||ret2<0)break;
    else if(ret1==0){
      fprintf(stderr,"%s ended before %s.\n",
       _argv[optind],_argv[optind+1]);
      break;
    }
    else if(ret2==0){
      fprintf(stderr,"%s ended before %s.\n",
       _argv[optind+1],_argv[optind]);
      break;
    }
    /*Okay, we got one frame from each.*/
    for(pli=0;pli<3;pli++){
      int xdec;
      int ydec;
      xdec=pli&&!(info1.pixel_fmt&1);
      ydec=pli&&!(info1.pixel_fmt&2);
      ssim[pli]=calc_psnrhvs(
       f1[pli].data+(info1.pic_y>>ydec)*f1[pli].stride+(info1.pic_x>>xdec),
       f1[pli].stride,
       f2[pli].data+(info2.pic_y>>ydec)*f2[pli].stride+(info2.pic_x>>xdec),
       f2[pli].stride,
       par,(info1.pic_x+info1.pic_w+xdec>>xdec)-(info1.pic_x>>xdec),
       (info1.pic_y+info1.pic_h+ydec>>ydec)-(info1.pic_y>>ydec),7,pli==0?csf_y:pli==1?csf_cb420:csf_cr420);
      gssim[pli]+=ssim[pli];
    }
    if(!summary_only){
      if(show_frame_type)printf("%s%s",tag1,tag2);
      if(!luma_only){
        printf("%08i: %-8G  (Y': %-8G  Cb: %-8G  Cr: %-8G)\n",frameno,
         convert_score_db(ssim[0]+cweight*(ssim[1]+ssim[2]),1+2*cweight),
         convert_score_db(ssim[0],1),convert_score_db(ssim[1],1),convert_score_db(ssim[2],1));
      }
      else printf("%08i: %8G\n",frameno,convert_score_db(ssim[0],1));
    }
  }
  if(!luma_only){
    printf("Total: %-8G  (Y': %-8G  Cb: %-8G  Cr: %-8G)\n",
     convert_score_db(gssim[0]+cweight*(gssim[1]+gssim[2]),(1+2*cweight)*frameno),
     convert_score_db(gssim[0],frameno),convert_score_db(gssim[1],frameno),
     convert_score_db(gssim[2],frameno));
  }
  else printf("Total: %-8G\n",convert_score_db(gssim[0],frameno));
  video_input_close(&vid1);
  video_input_close(&vid2);
  return EXIT_SUCCESS;
}

