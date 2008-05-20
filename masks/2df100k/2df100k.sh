#! /bin/sh

#script to create the angular mask for the 100k release of the 2dF Redshift Survey
#see http://www.mso.anu.edu.au/2dFGRS/ for more about the survey.
#USAGE: 2df100k.sh

if [ "$MANGLEBINDIR" = "" ] ; then
    MANGLEBINDIR="../../bin"
fi
if [ "$MANGLESCRIPTSDIR" = "" ] ; then
    MANGLESCRIPTSDIR="../../scripts"
fi
if [ "$MANGLEDATADIR" = "" ] ; then
    MANGLEDATADIR="../../masks"
fi

user=`whoami`
names=`finger $user | fgrep "ame:" | sed 's/.*: *\([^ ]*\)[^:]*/\1/'`
for name in ${names}; do break; done
echo "Hello $name, watch me make the angular mask for the 2dF 100k survey."

#to pixelize dynamically
#pix=
#restag=
#to pixelize everything to fixed resolution
scheme="s"
res=4
pix="-P${scheme}0,${res}"
restag="_res${res}${scheme}"

# to make verbose
quiet=
# to make quiet
#quiet=-q

# snap tolerances
snaptols="-a2 -b2 -t2"

#multiple intersection tolerance
mtol="-m1e-5"

# maximum harmonic number
lmax=20

# North

if [ -z "$quiet" ]; then
    echo "===========================================";
    echo "                   NORTH                   ";
fi

# name of output file to contain 2dF 100k North polygons
npol="2df100k_north${restag}.pol"

# -vo says to use old polygon ids, which are field numbers
echo "$MANGLEBINDIR/pixelize $quiet $mtol $pix -vo ngp_fields.dat jnfp"
$MANGLEBINDIR/pixelize $quiet $mtol $pix -vo ngp_fields.dat jnfp || exit
echo "$MANGLEBINDIR/pixelize $quiet $mtol $pix -vo ngpholes.dat jnhp"
$MANGLEBINDIR/pixelize $quiet $mtol $pix -vo ngpholes.dat jnhp || exit
echo "$MANGLEBINDIR/pixelize $quiet $mtol $pix -vo centres.ngp jncp"
$MANGLEBINDIR/pixelize $quiet $mtol $pix -vo centres.ngp jncp || exit
echo "$MANGLEBINDIR/snap $quiet $snaptols $mtol -vo jnfp jnf"
$MANGLEBINDIR/snap $quiet $snaptols $mtol -vo jnfp jnf || exit
echo "$MANGLEBINDIR/snap $quiet $snaptols $mtol -vo jnhp jnh"
$MANGLEBINDIR/snap $quiet $snaptols $mtol -vo jnhp jnh || exit
# -n intersects holes with their parent fields
echo "$MANGLEBINDIR/poly2poly $quiet $mtol -n jnh jnf jnhf"
$MANGLEBINDIR/poly2poly $quiet $mtol -n jnh jnf jnhf || exit
echo "$MANGLEBINDIR/balkanize $quiet $mtol jncp jnhf jnb"
$MANGLEBINDIR/balkanize $quiet $mtol jncp jnhf jnb || exit
echo "$MANGLEBINDIR/weight $quiet $mtol -z2dF100k jnb jnw"
$MANGLEBINDIR/weight $quiet $mtol -z2dF100k jnb jnw || exit
echo "$MANGLEBINDIR/unify $quiet $mtol jnw $npol"
$MANGLEBINDIR/unify $quiet $mtol jnw $npol || exit
echo "Polygons for 2dF 100k North are in $npol"

# South

if [ -z "$quiet" ]; then
    echo "===========================================";
    echo "                   SOUTH                   ";
fi

# name of output file to contain 2dF 100k South polygons
spol="2df100k_south${restag}.pol"

# -vo says to use old polygon ids, which are field numbers
echo "$MANGLEBINDIR/pixelize $quiet $mtol $pix -vo sgp_fields.dat jsfp"
$MANGLEBINDIR/pixelize $quiet $mtol $pix -vo sgp_fields.dat jsfp || exit
echo "$MANGLEBINDIR/pixelize $quiet $mtol $pix -vo sgpholes.dat jshp"
$MANGLEBINDIR/pixelize $quiet $mtol $pix -vo sgpholes.dat jshp || exit
echo "$MANGLEBINDIR/pixelize $quiet $mtol $pix -vo centres.sgp jscp"
$MANGLEBINDIR/pixelize $quiet $mtol $pix -vo centres.sgp jscp || exit
echo "$MANGLEBINDIR/pixelize $quiet $mtol $pix -vo centres.ran jrcp"
$MANGLEBINDIR/pixelize $quiet $mtol $pix -vo centres.ran jrcp || exit
echo "$MANGLEBINDIR/snap $quiet $snaptols $mtol -vo jsfp jsf"
$MANGLEBINDIR/snap $quiet $snaptols $mtol -vo jsfp jsf || exit
echo "$MANGLEBINDIR/snap $quiet $snaptols $mtol -vo jshp jsh"
$MANGLEBINDIR/snap $quiet $snaptols $mtol -vo jshp jsh || exit
# -n intersects holes with their parent fields
echo "$MANGLEBINDIR/poly2poly $quiet $mtol -n jsh jsf jshf"
$MANGLEBINDIR/poly2poly $quiet $mtol -n jsh jsf jshf || exit
echo "$MANGLEBINDIR/balkanize $quiet $mtol centres.sgp centres.ran jshf jsb"
$MANGLEBINDIR/balkanize $quiet $mtol jscp jrcp jshf jsb || exit
echo "$MANGLEBINDIR/weight $quiet $mtol -z2dF100k jsb jsw"
$MANGLEBINDIR/weight $quiet $mtol -z2dF100k jsb jsw || exit
echo "$MANGLEBINDIR/unify $quiet $mtol jsw $spol"
$MANGLEBINDIR/unify $quiet $mtol jsw $spol || exit
echo "Polygons for 2dF 100k South are in $spol"

# Harmonics

if [ -z "$quiet" ]; then
    echo "===========================================";
    echo "                 THE WORLD                 ";
fi

# name of output file to contain harmonics
wlm="2df100k${restag}.wlm"

echo "$MANGLEBINDIR/harmonize $quiet $mtol -l$lmax $npol $spol $wlm"
$MANGLEBINDIR/harmonize $quiet $mtol -l$lmax $npol $spol $wlm || exit
echo "Harmonics for 2dF 100k mask up to l = $lmax are in $wlm"

# Map

# name of output file to contain map
map="2df100k${restag}.map"

echo "$MANGLEBINDIR/map $quiet -w$wlm azel.dat $map"
$MANGLEBINDIR/map $quiet -w$wlm azel.dat $map || exit
echo "Map of 2dF 100k mask up to l = $lmax is in $map"

# Vertices

# name of output file to contain vertices
vert="2df100k${restag}.vrt"

echo "$MANGLEBINDIR/poly2poly -ov $mtol $quiet $npol $spol $vert"
$MANGLEBINDIR/poly2poly -ov $quiet $mtol $npol $spol $vert || exit
echo "Vertices of 2dF 100k mask are in $vert"

# Graphics

# name of output file to contain graphics
grph="2df100k${restag}.grph"

# number of points per (2 pi) along each edge of a polygon
pts_per_twopi=30

echo "$MANGLEBINDIR/poly2poly -og$pts_per_twopi $quiet $mtol $npol $spol $grph"
$MANGLEBINDIR/poly2poly -og$pts_per_twopi $quiet $mtol $npol $spol $grph || exit
echo "Data suitable for plotting polygons of the 2dF 100k mask are in $grph:"
echo "each line is a sequence of az, el points delineating the perimeter of a polygon."

# for plotting with the matlab script


if which matlab ; then
# name of output file to contain matlab graphics
    list="2df100k${restag}.list"
    eps="2df100k${restag}.eps"

    echo "$MANGLEBINDIR/poly2poly -ol$pts_per_twopi $quiet $npol $spol $list"
    $MANGLEBINDIR/poly2poly -ol$pts_per_twopi $quiet $mtol $npol $spol $list || exit
    echo "Data for plotting polygons of the 2dF 100k mask in Matlab are in $list."
    echo "Using Matlab to plot the 2dF 100k mask ..."
    echo "$MANGLESCRIPTSDIR/graphmask.sh $list $eps"
    $MANGLESCRIPTSDIR/graphmask.sh $list $eps
    if [ $? -eq 0 ]; then
	echo "Made a figure illustrating the 2dF 100k mask: $eps" 
	echo "Type \"ggv $eps\" or \"gv $eps\" to view the figure."  
    elif which sm ; then
	echo "Using Supermongo to plot the 2dF 100k mask:"
	sm -m $MANGLESCRIPTSDIR/graphmask.sm $grph $eps > temp.out
	rm temp.out
	if [ -e $eps ]; then
	    echo "Made a figure illustrating the 2dF 100k mask: $eps" 
	    echo "Type \"ggv $eps\" or \"gv $eps\" to view the figure."  
	    echo "A script is also available to plot mangle files Matlab (with the mapping toolbox)," 
	    echo "or you can plot $grph using your own favorite plotting tool."
	fi
    else 
	echo "Scripts are available for plotting mangle polygons in Matlab" 
	echo "(with the mapping toolbox) or Supermongo, or you can plot $grph"
	echo "using your own favorite plotting tool."
    fi
elif which sm ; then
    echo "Using Supermongo to plot the 2dF 100k mask:"
    sm -m $MANGLESCRIPTSDIR/graphmask.sm $grph $eps > temp.out
    rm temp.out
    if [ -e $eps ]; then
	echo "Made a figure illustrating the 2dF 100k mask: $eps" 
	echo "Type \"ggv $eps\" or \"gv $eps\" to view the figure."  
	echo "A script is also available to plot mangle files Matlab (with the mapping toolbox)," 
        echo "or you can plot $grph using your own favorite plotting tool."
    fi
else
    echo "Scripts are available for plotting mangle polygons in Matlab" 
    echo "(with the mapping toolbox) or Supermongo, or you can plot $grph"
    echo "using your own favorite plotting tool."
fi

# remove temporary files
rm j[nsr]*

if [ -z "$quiet" ]; then
    echo "===========================================";
    echo "the universe?"
fi

if [ "$quiet" ]; then
    echo ""
    echo "If you'd like to repeat that with the sound on,"
    echo "please turn off the quiet button in 2df100k.sh and try again."
fi
