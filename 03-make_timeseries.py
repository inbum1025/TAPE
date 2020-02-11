# -*- coding: utf-8 -*-
"""
03-make_timeseries
 (1) READ the photometry files (apw)
 (2) GENERATE the time-seriese files (apx)

@author: wskang
@update: 2019/09/25
"""
import os, time 
import numpy as np 
import matplotlib.pyplot as plt 
from astropy.io import fits 
from photlib import read_params

# ====================================================================
# PARAMETERS for the list of time-series observation 
# ====================================================================
par = read_params()

WORKDIR = par['WORKDIR']
SHIFT_PLOT = bool(int(par['SHIFTPLOT']))  # ON/OFF image shift plot 
N_APER = len(par['PHOTAPER'].split(',')) # number of aperture in .apw file, photometry result
FWHM_CUT2 = np.array(par['FWHMCUT'].split(','),float)[1]
LOGFILE = par['LOGFILE']
NSTARS = int(par['NSTARS'])
OBSDATE = par['OBSDATE'] 
TARGETNAME = par['TARGETNAM']
WNAME = OBSDATE+'-'+TARGETNAME

print ('#WORK DIR: ', WORKDIR)
print ('#SHIFT PLOT: ', SHIFT_PLOT)
print ('#LOG FILE: ', LOGFILE)

# MOVE to the working directory 
os.chdir(WORKDIR)

# READ log file and 
# SET the fiducial frame index and position 
# automatically find the first frame 
flog = open(LOGFILE,'r')
lfrm, lname, lJD, lX = [], [], [], [] 
for line in flog:
    tmp = line.split()
    lfrm.append(int(tmp[0]))
    lname.append(tmp[1])
    lJD.append(float(tmp[2]))
    lX.append(float(tmp[4]))
FNUM, FLIST, FJD, FX = np.array(lfrm), np.array(lname), np.array(lJD), np.array(lX)
flog.close()
FID = FLIST[0]
    
# READ fiducial frame index and position
# ------------------------------------------
# YOU SHOULD CUSTOMIZE THIS NUMBER OF STARS TO MATCH
# ------------------------------------------
NCUT = 20
# ------------------------------------------
dat = np.genfromtxt(FID+'.apw')
tx, ty = dat[:,0], dat[:,1] 
tnum = np.arange(1,len(tx)+1, dtype=int)
tmag = dat[:,(2*N_APER+N_APER+1)]
tbb = np.argsort(tmag)[:NCUT]

fmat = open('Wmatching.log','w')
jds, xs, ys, alts, azis, decs = [FJD[0],], [0,], [0,], [0,], [0,], [0,]
# LOOP for apw files
for i, fidx in enumerate(FLIST):

    # READ the FITS header 
    hdu = fits.open(fidx+'.fits')
    img, hdr = hdu[0].data, hdu[0].header
    EXPTIME = float(hdr.get('EXPTIME'))
    FILTER = hdr.get('FILTER')
    HJD = hdr.get('HJD')
    if HJD is None: HJD = FJD[i]
    ALT = float(hdr.get('ALT'))
    AZI = float(hdr.get('AZ'))
    AIRMASS = hdr.get('AIRMASS')
    if AIRMASS is None: AIRMASS = FX[i]
    try:
        sDEC = hdr.get('DEC')
        tmp = sDEC[1:].split()
        dDEC = float(tmp[0]) + float(tmp[1])/60.0 + float(tmp[2])/3600.0 
        if sDEC.startswith('-'): dDEC = - dDEC
    except:
        dDEC = 0
    # READ the apw file with number and index of apertures 
    dat = np.genfromtxt(fidx+'.apw')
    if len(dat) < 20: continue
    
    # READ all coordiates ------------------------------------------
    xpix, ypix = dat[:,0], dat[:,1] 
    # READ brightness data 
    mag = dat[:,(2*N_APER+N_APER+1)]

    # FILTERING coordinates of bright stars by magnitude-limits
    vv = np.argsort(mag)[:NCUT]
    xpix2, ypix2 = xpix[vv], ypix[vv]
    
    dx, dy = [], [] 
    for inum, ix, iy in zip(tnum[tbb], tx[tbb], ty[tbb]):
        rsq = (ix - xpix2)**2 + (iy - ypix2)**2 
        mm = np.argmin(rsq)
        dx.append(ix - xpix2[mm])
        dy.append(iy - ypix2[mm])
    # CALC. the median of shifts
    xmed, xsig = np.median(dx), np.std(dx)
    ymed, ysig = np.median(dy), np.std(dy)
    
    # PLOT the shift result in the image 
    if SHIFT_PLOT == True:
        fig, ax = plt.subplots(num=1, figsize=(8,8))
        ny, nx = img.shape
        limg = np.arcsinh(img)
        z1, z2 = np.percentile(limg,30), np.percentile(limg,99.5)
        ax.imshow(-limg, vmin=-z2, vmax=-z1, cmap='gray')
        ax.scatter(xpix, ypix, 100,facecolors='none', edgecolor='b', alpha=0.7)
        ax.plot(tx-xmed, ty-ymed, 'r+', mew=1, ms=18, alpha=0.7, \
                label='dx=%.3f, dy=%.3f' % (xmed, ymed))
        ax.set_xlim(0,nx)
        ax.set_ylim(ny,0)
        ax.set_title('Shift of Image: '+fidx, fontsize=15)
        ax.legend(loc='upper right', fontsize=15)
        fig.savefig(fidx+'-matching')
        fig.clf()
    
    print ('%s dx=%.2f(%.2f) dy=%.2f(%.2f) %i/%i' % \
          (fidx, xmed, xsig, ymed, ysig, len(dx), len(tbb)))
    fmat.write('%s %8.3f %6.3f %8.3f %6.3f %i \n' % \
              (fidx, xmed, xsig, ymed, ysig, len(dx)))
    jds.append(HJD)
    xs.append(xmed)
    ys.append(ymed)
    alts.append(ALT)
    azis.append(AZI)
    decs.append(dDEC)

    # SAVE photometry result of the same star on the same row
    fdat = open(fidx+'.apx', 'w')         
    for i, ix, iy in zip(tnum, tx, ty):
        rsq = (ix - xpix - xmed)**2 + (iy - ypix - ymed)**2 
        mm = np.argmin(rsq)
        if rsq[mm] > FWHM_CUT2**2:
            flag = 99
        else:
            flag = 0
        fstr = '%03i %10.3f %10.3f ' % (i, xpix[mm], ypix[mm])
        fstr1, fstr2, fstr3, fstr4 = '', '', '', ''
        for k in range(N_APER):
            fstr1 = fstr1 + '%12.3f ' % (dat[mm,(k+2)],)
            fstr2 = fstr2 + '%12.3f ' % (dat[mm,(N_APER+k+2)],)
            fstr3 = fstr3 + '%8.3f ' % (dat[mm,(2*N_APER+k+2)],)
            fstr4 = fstr4 + '%8.3f ' % (dat[mm,(3*N_APER+k+2)],)
        fstr += fstr1 + fstr2 + fstr3 + fstr4 
        fstr += '%12.3f %i \n' % (rsq[mm], flag) 
        fdat.write(fstr)
    fdat.close()            

# PLOT the shift for all images
fmat.close()

# shift plot ====================================================
plt.plot(xs, ys, 'r-', alpha=0.5)
fout = open('w'+WNAME+'-shift.txt', 'w')
num = range(len(xs))
jd0 = jds[0]
djd = jds[-1] - jd0
print (jd0, djd)
for p1, p2, p3, p4, p5, p6, p7 in zip(num, xs, ys, jds, alts, azis, decs):
    fout.write('%4i %20.8f %8.3f %8.3f %8.3f %8.3f %8.3f\n' % \
               ( p1, p4, p2, p3, p5, p6, p7))
    plt.plot(p2, p3, 'ro', ms=((p4-jd0)*(3600*12)/500.), alpha=0.5) 
fout.close()
for i in np.linspace(0,djd*3600*12,6):
    plt.plot(-200,200,'ro',ms=(i/500.), \
             alpha=0.5, label='%5d s' % (i,))
plt.xlim(min(xs)-5,max(xs)+5)
plt.ylim(min(ys)-5,max(ys)+5)
plt.gca().set_aspect(1)
plt.grid()
plt.legend(fontsize=10,loc='upper right', ncol=3, numpoints=1)
plt.savefig('w'+WNAME+'-shift')
plt.close('all')

# READ AND PLOT the finding-chart
hdu = fits.open(FID+'.fits')
img, hdr = hdu[0].data, hdu[0].header
ny, nx = img.shape
fig, ax = plt.subplots(figsize=(9,9))
limg = np.arcsinh(img)
z1, z2 = np.percentile(limg,30), np.percentile(limg,99.5)
ax.imshow(-limg, vmin=-z2, vmax=-z1, cmap='gray')
tpp = np.argsort(tmag)[:200]
# LOOP for the bright stars 
for ix, iy, inum in zip(tx[tpp], ty[tpp], tnum[tpp]):
    ax.text(ix+30, iy, '%02i' % (inum,), \
            fontsize=10, color='#0022FF')
ax.set_xlim(0,nx)
ax.set_ylim(ny,0)
ax.set_title('Star Index Chart: '+WNAME+'-'+FILTER+' / '+FID)
print ('WRITE TO w'+WNAME+'-chart.png...')
fig.savefig('w'+WNAME+'-chart.png')
plt.close('all')




