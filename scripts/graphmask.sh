#!/bin/sh
# � M E C Swanson 2008
#plot the angular mask described by a polygon file in .list format
#using the matlab mapping toolbox
#optional 3rd-6th arguments give the RA and Dec range to plot the mask
#if no range is given, the full sky will be plotted
#optional 7th argument turns on drawing black outlines around each polygon
#
#if specifying the full path to a file (rather than just running in the directory 
#containing the file you want to plot), put the path in double-quotes as shown below.
#
#graphmask.sh <infile> <outfile> [<ramin>] [<ramax>] [<decmin>] [<decmax>] [<outlines>]
#EXAMPLES: 
#fullsky, no outlines: graphmask.sh "dr4/safe0/sdss_dr4safe0_mask.list" "dr4/safe0/sdss_dr4safe0_mask.eps"
#defined range, no outlines: graphmask.sh sdss_slice.list sdss_slice.eps -45 35 8 20
#defined range, outlines: graphmask.sh sdss_slice.list sdss_slice.eps -45 35 8 20 on

if [ "$MANGLESCRIPTSDIR" = "" ] ; then
    MANGLESCRIPTSDIR="../../scripts"
fi

if [ $# -le 2 ]; then
    matlab -nodisplay -r addpath\(\'$MANGLESCRIPTSDIR\'\)\;graphmask\(\'$1\',\'$2\'\)
elif [ $# -ge 6 ]; then
    matlab -nodisplay -r addpath\(\'$MANGLESCRIPTSDIR\'\)\;graphmask\(\'$1\',\'$2\',\[$3,$4,$5,$6\],\'$7\'\)
else
    echo "foo"
fi
if [ -e matlabexit.temp ]; then
    rm matlabexit.temp
    exit 1
fi
echo all done!
