# PyAPW
## Python Aperture Photometry Tool for Students

Perform the aperture photometry for time-series observations. (e.g. exoplanet transit events, variable stars )

The Goal of Project
 - Be able to perform photometry without IRAF/Linux for the images obtained at DOAO (Deokheung Optical Astronomy Observatory)
 - Share the set of verified codes for an astronomical project
 - Explain the process of image processing and photometry for educational purpose 
  
## Components
- photlib.py (functions for image processing and photometry)  
- pyapw.par (input parameters for running)
- 01-run_ccdproc.py (run automatic image preprocessing)
- 02-run_photometry.py (run aperture photometry)
- 03-make_timeseries.py (run star-matching and generate the time-series of magnitudes)
- 05-chek_comps.py (find the comparisons for differential photometry)
- 06-plot_lightcurve.py (draw the light curves [flux] for the selected comparisons)
 
## How to use 
 
### Prepare a set of images obtained at DOAO using NYSC 1m telescope.
  - bias-???.fits
  - dark-???.fits 
  - flat-???.fits 
  - object-??????.fits  

### Input the parameters in pyapw.par 
```    
WORKDIR   ./180326-HAT-P-12b
BINNING   1            # (APPHOT) BINNING option of CCD images for processing
STARBOX   40           # (APPHOT) box half-size for photometry [pixel]
THRES     5            # (APPHOT) n-sigma threshold for finding stars
FWHMCUT   3,20         # (APPHOT) FWHM lower/upper limit for filtering non-stars [pixel]
SATU      60000        # (APPHOT) saturation level limit for filtering [ADU]
PHOTAPER  10,20,30     # (APPHOT)(NO_SPACE)apertures for photometry [pixel]
SKYANNUL  30,34        # (APPHOT)(NO_SPACE)sky-annulus for background [pixel]
SUBPIXEL  1            # (APPHOT) the division number for subpixel method
EGAIN     1.0          # (APPHOT) the gain of CCD for error estimation
PSCALE    0.464        # (APPHOT) pixel scale in stellar profile plot 0.3867,0.464
STARPLOT  0            # (APPHOT) flag for plotting the diagram for each star
LOGFILE   wobs.log     # (APPHOT) log file name for LC processing
APERUSED  2            # (TIMESERIES) index of aperture(in PHOTAPER) for LC
SHIFTPLOT 1            # (TIMESERIES) flag for plotting all shift-images
OBSDATE   180326       # (TIMESERIES) observation date
TARGETNAM HAT-P-12b    # (TIMESERIES) target name  
TARGETNUM 13           # (TIMESERIES) target star numbers in finding-chart 
COMPNUMS  10,17,22     # (TIMESERIES) (NOSPACE) comparison star numbers
CHKSIG    0.02         # (TIMESERIES) STD checking criteria for LC test
CHKDELM   3            # (TIMESERIES) DEL_MAG checking criteria for LC test
```
- WORKDIR: relative or absolute path of working directory
- BINNING: pixel binning of processing images
- STARBOX: crop box size for the photometry and analysis
- THRES: detecting threshold factor relative to the sigma of image pixels    
- FWHMCUT: minimum and maximum FWHM for filtering non-stars [in pixel]
- SATU: pixel value to exclude the saturated pixels [in ADU]
- PHOTAPER: aperture radius for photometry [in pixel] 
- SKYANNUL: sky annulus size to estimate the background of sky 
- SUBPIXEL: the number to divide a pixel using subpixel method for photometry
- EGAIN: gain value of CCD [e-/ADU] (if FITS header "EGAIN" is not defined)   
- PSCALE: pixel scale [arcsec/pix] for analysis of radial profile (Gaussian fitting)
- STARPLOT: ON/OFF stellar profile analysis for each star
- LOGFILE: log of basic information of each frame (will be used to generate light curve)   
- APERUSED: order of the applying aperture in the aperture size list PHOTAPER 
- SHIFTPLOT: ON/OFF matching result plots
- OBSDATE: observation date and target name for making files and plots
- TARGETNUM: target number in the finding-chart (XXXXXX-YYYYYY-chart.png)
- COMPNUMS: numbers of comparison stars for differential photometry in the finding-chart (XXXXXX-YYYYYY-chart.png)
- CHKSIG: cut-off sigma value in light curve to find a proper comparison star
- CHKDELM: cut-off delta magnitude in light curve to find a proper comparison star
 
