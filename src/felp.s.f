c-----------------------------------------------------------------------
c © A J S Hamilton 2001
c-----------------------------------------------------------------------
      real(16) function felp(epoch)
      integer dp
      parameter (dp = 16)
      real(dp) epoch
c
c        parameters
      include 'frames.par'
c        local (automatic) variables
      real(dp) t
c *
c * Ecliptic latitude of NCP = Dec of ecliptic NP
c * as a function of epoch (e.g. 1950, 2000).
c *
c        RA & Dec epoch in centuries since 1900
      t=(epoch-1900._dp)/100._dp
c        ecliptic latitude of NCP = Dec of ecliptic NP
      felp=90._dp-(E1+t*(E2+t*(E3+t*E4)))
      return
      end
c
