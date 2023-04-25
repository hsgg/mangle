c-----------------------------------------------------------------------
c � A J S Hamilton 2001
c-----------------------------------------------------------------------
      subroutine azel(ra,dec,raz,elp,azp,az,el)
      integer dp
      parameter (dp = 16)
      real(dp) ra,dec,raz,elp,azp,az,el
c
c        parameters
      include 'radian.par'
      real(dp) CIRCLE
      parameter (CIRCLE = 360._dp)
c        local (automatic) variables
      integer iz
      real(dp) cazm,cdec,cel,celp,cra,sazm,sdec,sel,selp,sra
c *
c * Convert RA & Dec ra, dec -> azimuth & elevation.
c * To accomplish the inverse operation, az, el -> ra, dec,
c *   call azel(az, el, azp, elp, raz, ra, dec);
c * To convert RA & Dec to Galactic Longitude and Latitude, use
c *   raz = 192.25, elp = 27.4, azp = 123.
c *
c  Input: ra = RA in degrees.
c         dec = Dec in degrees.
c         raz = RA of zenith in degrees.
c         elp = elevation of NCP in degrees = Dec of zenith.
c         azp = azimuth of NCP in degrees.
c Output: az = azimuth in degrees (0.le.az.lt.360).
c         el = elevation in degrees (-90.le.el.le.90).
c
c        sines and cosines of input angles
      sdec=sin(dec/RADIAN)
      cdec=cos(dec/RADIAN)
      selp=sin(elp/RADIAN)
      celp=cos(elp/RADIAN)
      sra=sin((ra-raz)/RADIAN)
      cra=cos((ra-raz)/RADIAN)
c        sine and cosine of elevation
      sel=cdec*celp*cra+sdec*selp
      if (sel.gt.1._dp) then
        sel=1._dp
      elseif (sel.lt.-1._dp) then
        sel=-1._dp
      endif
      cel=sqrt(1._dp-sel**2)
c        elevation in degrees
      el=asin(sel)*RADIAN
c        if elevation is +90 or -90 degrees, set azimuth to that of NCP
      if (cel.eq.0._dp) then
        az=azp
      elseif (cel.ne.0._dp) then
c        sine and cosine of azimuth relative to NCP azimuth
        sazm=-cdec*sra/cel
        cazm=(sdec*celp-cdec*selp*cra)/cel
c        azimuth in degrees
        az=atan2(sazm,cazm)*RADIAN+azp
c        ensure azimuth is in interval [0,360)
        iz=az/CIRCLE
        if (az.lt.0._dp) iz=iz-1
        az=az-iz*CIRCLE
      endif
      return
      end
c
