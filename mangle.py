# mangle.py
"""Basic mangle routines for identifying which points are in which polygons.

For more on Mangle:
    http://space.mit.edu/~molly/mangle/

To build the included cython mangle_utils code, which will result in a ~4x
speed up for polyid commands:
    python setup.py build_ext --inplace

Example usage:
    import mangle
    polyfile = 'geometry-boss7.ply' #(also accepts fits files)
    mng = mangle.Mangle(polyfile)
    # ... read in a file with ra/dec coordinates as a numpy array
    polyids = mng.get_areas(ra,dec)
    mng.areas[polyids] == mng.get_areas(ra,dec)
    mng.weights[polyids] == mng.get_weights(ra,dec)
    first_mng = mng[:10] # new mangle instance with just the first 10 polygons

Requires numpy > 1.0, and pyfits > 2.3.1 for loading fits files.
"""
# Author:		Martin White	(UCB)
# Written		17-Mar-2010
# Modified:		17-Mar-2010	(Basic bug fixes)
#			22-Mar-2010	(Track pixel area)
#			20-Apr-2010	(Add setweight and writeply methods)
#			21-Apr-2010	(Add totalarea method)
#			12-May-2010	(Allow no space before "caps")
#        24-Jun-2010 jkp: (tweaks to gain ~40% speed improvement.)
#        29-Jun-2010 jkp: (numpy vectorized polyid for >10x speed improvement.)
#        22-Jul-2010 jkp: (completed and tested numpy version. Speed is ~1/2 that of the commandline mangle)
#        10-Aug-2010 jkp: (Added resorting of out-of-order polygons and altered original polylist structure)
#        10-Oct-2010 jkp: (Added __getitem__, returning a new Mangle instance given an index)
#        10-Mar-2011 jkp: (Added support for mangle_utils, with a 4x faster cythonized _incap)
#        18-May-2011 apw: (Added support using the photofield database tables in dr8db/spectradb)
#        10-Sep-2011 mecs: (allow ascii polygon files to be named .pol or .ply)
#        10-Sep-2011 mecs: (added option to keep existing id numbers from the polygon file)
#        15-Sep-2011 mecs: (added support to parse mangle header keywords in ascii and fits polygon files)
#        20-Sep-2011 mecs: (added method to write a polygon fits file)
#        27-Sep-2011 mecs: (added support to read in whatever extra column names are included in an input fits file)
#        27-Sep-2011 mecs: (added metadata structure to track of extra columns and methods to add and remove columns)
#        27-Sep-2011 mecs: (added support for reading and writing variable length array columns)
#        03-Nov-2011 mecs: (added support to read and write extra columns in ascii format)
#        29-Nov-2011 mecs: (fixed various bugs with importing ascii files with space before header keywords or negative weights/ids)
#        30-Nov-2011 mecs: (integrated with my graphmask plotting module)


import os
import re
import string
import copy
from itertools import izip
import graphmask

try:
    #raise ImportError # uncomment this to force pure-python code
    import mangle_utils
except ImportError as e:
    print "Error, could not import mangle_utils:",e
    print "Mangle routines will still function, but be slower."
    print "Check that you have built mangle_utils.so (see README.txt)."
    useUtils = False
else:
    useUtils = True

import numpy as np
# some of these will need to be called often, so explicitly name them
from numpy import array,sin,cos,fabs,pi,empty,zeros,ones,argsort,take,arange
import pyfits

class Mangle:
    """Implements basic mangle routines to identify polygons containing points.
    
    All functions assume ra,dec are in decimal degrees.

    Initialize with a single string containing the mask file, which can be
    either a polygon format file or a fits file.

    Default values, if the file does not specify them:
        weight == 0.
        area = -1.
        pixel = 0

    For working with large numbers of points, use the get_XXX() functions:
        get_polyids(), get_weight(), get_areas()
    which are up to 100x faster than the single value functions:
        polyid(), weight(), area()
    when operating on numpy arrays.
    
    Supports slicing, e.g.:
        newmng = mng[:10]
        newmng2 = mng[mng.areas < 1e-7]
        newmng3 = mng[[1,3,5,7,9]]
    """

    __author__ = "John Parejko, Martin White, Molly Swanson"
    __version__ = "2.2"
    __email__  = "john.parejko@yale.edu"

    def incap_spam(self,cap,x0,y0,z0):
        """
        Internal class function.

        Returns True if (theta,phi) lies in the cap specified by the
        4-vector "cap" containing (x,y,z,cm).
        """
        cd = 1.0-cap[0]*x0-cap[1]*y0-cap[2]*z0
        if cap[3]<0.0:
            if cd>fabs(cap[3]):
                return True
            else:
                return False
        else:
            if cd<cap[3]:
                return True
            else:
                return False

    def incap_vec(self,cap,x0,y0,z0):
        """
        Internal class function.

        Returns True for each (theta,phi) that lies in the cap specified by the
        4-vector "cap" containing (x,y,z,cm), and False for the rest."""
        cd = 1.0-cap[0]*x0-cap[1]*y0-cap[2]*z0
        return ((cap[3] < 0.0) & (cd>fabs(cap[3]))) | ((cap[3] > 0.0) & (cd<cap[3]))
    #...

    def inpoly_spam(self,polygon,theta,phi):
        """
        Internal class function.

        Returns True if (theta,phi) is in the polygon, i.e. if it is
        within all of the caps in the polygon.
        A polygon is a list giving the polygon number, the weight and
        then all of the caps (each cap is a 4-vector/4-list)."""
        # precompute the trig functions
        sintheta =  sin(theta)
        x0 = sintheta*cos(phi)
        y0 = sintheta*sin(phi)
        z0 = cos(theta)
        # this is faster than a for loop or list comprehension,
        # since it stops as soon as one returns false.
        return all(self.incap_spam(cap,x0,y0,z0) for cap in polygon)

    def inpoly_vec(self,polygon,x0,y0,z0):
        """
        Internal class function.

        Returns True for each (theta,phi) if it is in the polygon,
        i.e. if it is within all of the caps in the polygon.
        A polygon is a list giving the polygon number, the weight and
        then all of the caps (each cap is a 4-vector/4-list).
        """
        test = ones(len(x0),dtype=bool)
        if useUtils:
            for cap in polygon:
                test &= mangle_utils._incap(cap,x0,y0,z0)
        else:
            for cap in polygon:
                test &= self.incap_vec(cap,x0,y0,z0)
        return test
    #...
    
    def which_pixel(self,ra,dec):
        """Return the pixel numbers for each pair of ra,dec.
        
        UNFINISHED!!!
        The pixelization information is , given pixelization
        resolution res and scheme 's' or 'd'.
        !!! NOTE: only scheme 's' is currently implemented"""
        if self.pixelization == None:
            raise TypeError('No pixelization defined in this mangle instance.')
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        ### TBD!!!
        ### Math for this comes from which_pixel in the mangle2.2/src directory
        return None
    #...        

    def get_polyids(self,ra,dec):
        """Return the ID numbers of the polygons containing each RA/Dec pair.

        ra/dec should be numpy arrays in decimal degrees.
        """
        # force an upconversion to double, in case ra/dec are float32
        theta = pi/180. * (90.0-np.float64(dec))
        phi = pi/180. * np.float64(ra)
        sintheta = sin(theta)
        x0 = sintheta*cos(phi)
        y0 = sintheta*sin(phi)
        z0 = cos(theta)
        # If we have a pixelized mask, we can reduce the number of polygons 
        # we have to check for each object.
        #if self.npixels > 0:
        #    for pix in self.pixels:
        #        pixels = self.which_pixel(ra,dec)
        #    # TBD: This needs to be finished!
        #    return None
        #else:
        goodpolys = -ones(len(ra),dtype=int)
        for i,poly in izip(self.polyids,self.polylist):
            test = self.inpoly_vec(poly,x0,y0,z0)
            goodpolys[test] = i
        return goodpolys
    #...

    def get_areas(self,ra,dec):
        """Return the areas of the polygons containing each RA/Dec pair.

        ra/dec should be numpy arrays in decimal degrees.

        Return value is in steradians.

        Polygon areas are taken directly from the input file.
        """
        polyids=self.get_polyids(ra,dec)
        return self.areas[polyids]
    #...

    def get_weights(self,ra,dec):
        """Return the weights of the polygons containing each RA/dec pair.

        ra,dec should be numpy arrays in decimal degrees.

        The weight is taken directly from the input file."""
        polyids=self.get_polyids(ra,dec)
        return self.weights[polyids]
    #...

    def polyid(self,ra,dec):
        """Return the polyid of the polygon containing (ra,dec).
        
        ra,dec should be in decimal degrees.
        """
        theta = pi/180. * (90.0-dec)
        phi   = pi/180. * ra
        ipoly = -1
        for i,poly in zip(self.polyids,self.polylist):
            if self.inpoly_spam(poly,theta,phi):
                ipoly = i
                break
        return(ipoly)

    def weight(self,ra,dec):
        """Return the weight of the polygon containing (ra,dec).
        
        ra,dec should be in decimal degrees.
        """
        theta = pi/180. * (90.0-dec)
        phi   = pi/180. * ra
        weight= -1
        for w,poly in zip(self.weights,self.polylist):
            if self.inpoly_spam(poly,theta,phi):
                weight = w
                break
        return(weight)

    def area(self,ra,dec):
        """Return the area of the polygon containing (ra,dec).
        
        ra,dec should be in decimal degrees.

        Return value is in steradians.
        """
        theta = pi/180. * (90.0-dec)
        phi   = pi/180. * ra
        area  = -1.0
        for a,poly in izip(self.areas,self.polylist):
            if self.inpoly_spam(poly,theta,phi):
                area = a
                break
        return(area)

    def totalarea(self):
        """Return the total area and the 'effective' area in the mask.

        total area is the sum of the areas of each polygon.
        effective area is the area weighted by the completeness.
        """
        tot_area = self.areas.sum()
        eff_area = (self.weights*self.areas).sum()
        return((tot_area,eff_area))

    def set_weight(self,polyid,weight):
        """Set the weight of polygon 'polyid' to weight.
        
        polyid can be an int, index array or boolean index array.
        """
        self.weights[polyid] = weight

    def set_area(self,polyid,area):
        """Set the area of polygon 'polyid' to area.
        
        polyid can be an int, index array or boolean index array.
        """
        self.area[polyid] = area

    def set_pixel(self,polyid,pixel):
        """Set the pixel ID of polygon 'polyid' to pixel.
        
        polyid can be an int, index array or boolean index array.
        """
        self.pixel[polyid] = pixel

    def set_allarea(self,area):
        """Set the area of all polygons to weight."""
        self.areas.flat = area

    def set_allweight(self,weight):
        """Set the weight of all polygons to weight."""
        self.weights.flat = weight

    def set_allpixel(self,pixel):
        """Set the weight of all polygons to weight."""
        self.pixels.flat = pixel

    def writeply(self,filename,keep_ids=False,write_extra_columns=False,weight=None):
        """Write a Mangle-formatted polygon file containing these polygons."""
        ff = open(filename,"w")
        ff.write("%d polygons\n"%len(self.polylist))
        if self.pixelization is not None:
            ff.write("pixelization %d%s\n"%(self.pixelization[0],self.pixelization[1]))
        if self.snapped == True:
            ff.write("snapped\n")
        if self.balkanized == True:
            ff.write("balkanized\n")
        if ('ids' in self.names) & keep_ids==True:
            ids_to_write=self.ids
        else:
            ids_to_write=self.polyids
        for i in range(self.npoly):
            # TBD: add writing pixel information to the output file.
            str = "polygon %10d ( %d caps,"%(ids_to_write[i],len(self.polylist[i]))
            str+= " %.8f weight, %d pixel, %.15f str):\n"%(self.weights[i],self.pixels[i],self.areas[i])
            ff.write(str)
            for cap in self.polylist[i]:
                ff.write("%25.20f %25.20f %25.20f %25.20f\n"%\
                  (cap[0],cap[1],cap[2],cap[3]))
        ff.close()

        #write extra columns stored in this format:
        # polygon file named poly.pol or poly_obstime.pol (to denote that the polygons are weighted by observation time)
        # additional columns will be written as poly.maglims, poly.obstime, poly.XXX where XXX is the name of the column
        # if a name is provided as the weight argument, e.g., weight='obstime', then that column will be written as the weights, and if 'obstime'
        # is contained in the filename, e.g., polys_obstime.pol, additional columns will be written as poly.XXX (not poly_obstime.XXX)
        # additional column files will have number of rows equal to the number of polygons 
        # this allows alternate weights and extra information about the polygons that are stored in a fits file to be written in ascii format        
        if write_extra_columns:
            base_filename=string.split(filename,'.')[0]
            # if column to weight by is provided, e.g., weights='obstime', check to see if base filename ends
            # in _obstime and strip it off if it does before generating extra column filenames 
            if weight is not None:
                if weight==string.split(base_filename,'_')[-1]:
                    base_filename='_'.join(string.split(base_filename,'_')[:-1])
            for name in self.names:
                asciiformat=self.metadata[name]['asciiformat']
                if asciiformat is not None:
                    np.savetxt(base_filename+'.'+name, vars(self)[name],fmt=asciiformat)

    def __getitem__(self,idx):
        """Slice this mangle instance by the index array idx.
        
        Return a mangle instance containing only those polygons
        referenced in idx, which can be a single integer, array or list
        of indicies, a boolean index array, or a slice.
        """
        mng2=copy.deepcopy(self)
        mng2.polyids = self.polyids[idx]
        # slices also have no len(), so we need to test after indexing
        # incase a slice was passed.
        try:
            mng2.npoly = len(mng2.polyids)
        except TypeError:
            idx = [idx,]
            mng2.polyids = self.polyids[idx]
            mng2.npoly = len(mng2.polyids)
        mng2.polylist = mng2.polylist[idx]
        mng2.areas = mng2.areas[idx]
        mng2.weights = mng2.weights[idx]
        mng2.ncaps = mng2.ncaps[idx]
        mng2.pixels = mng2.pixels[idx]
        for name in mng2.names:
            vars(mng2)[name]=vars(mng2)[name][idx]
        return mng2
    #...

    def drawpolys(self,skymap=None,**kwargs):
        if 'graphicsfilename' in kwargs:
            graphicsfilename=kwargs.pop('graphicsfilename')
        else:
            graphicsfilename=None
        if 'pointsper2pi' in kwargs:
            pointsper2pi=kwargs.pop('pointsper2pi')
        else:
            pointsper2pi=None
        if skymap is None:
            if hasattr(self,'graphicsfilename'):
                p,m=graphmask.plot_mangle_map(self.graphicsfilename,graphicsfilename=graphicsfilename,pointsper2pi=pointsper2pi,**kwargs)
            else:
                p,m=graphmask.plot_mangle_map(self,graphicsfilename=graphicsfilename,pointsper2pi=pointsper2pi,**kwargs)
        else:
            m=skymap
            if hasattr(self,'graphicsfilename'):
                azel,weight=m.get_graphics_polygons(self.graphicsfilename,graphicsfilename=graphicsfilename,pointsper2pi=pointsper2pi)
            else:
                azel,weight=m.get_graphics_polygons(self,graphicsfilename=graphicsfilename,pointsper2pi=pointsper2pi) 
            p=graphmask.draw_weighted_polygons(m.world2pix(azel),weight=weight,**kwargs)
        if graphicsfilename is not None:
            self.graphicsfilename=graphicsfilename
        howmany=graphmask.expecting()
        if howmany<2:
            return p
        else:
            return p,m
        
    ## def graphics(self):
    ##     """Return an array of edge points, to plot these polygons.

    ##     Calls the command-line 'poly2poly' to generate a temporary graphics
    ##     file and return the output.

    ##     The returned array has len() == npoly, with each element
    ##     being an array of ra/dec pairs. Plot a polygon with, e.g.:
    ##         polys = mng.graphics()
    ##         pylab.plot(polys[0]['ra'],polys[0]['dec'])
    ##     or all of them (this may take a while,if there are a lot of polygons):
    ##         polys = mng.graphics()
    ##         for poly in polys:
    ##             pylab.plot(poly['ra'],poly['dec'])
    ##     """
    ##     import tempfile
    ##     import subprocess
    ##     tempIn = tempfile.NamedTemporaryFile('rw+b')
    ##     self.writeply(tempIn.name)
    ##     tempOut = tempfile.NamedTemporaryFile('rw+b')
    ##     call = ' '.join(('poly2poly -q -ol30',tempIn.name,tempOut.name))
    ##     subprocess.call(call,shell=True)
    ##     # NOTE: poly2poly -ol always outputs a separate weight file.
    ##     tempIn.close()
    ##     # the mangle list format has polygons delimited by NaN pairs.
    ##     dtype=[('ra','>f8'),('dec','>f8')]
    ##     data=np.loadtxt(tempOut,dtype=dtype)
    ##     weights=np.loadtxt(tempOut.name+'.weight',dtype=dtype)
    ##     tempOut.close()
    ##     os.remove(tempOut.name+'.weight')
    ##     i = 0
    ##     polys = np.empty(len(weights),dtype='object')
    ##     temp = []
    ##     for x in data:
    ##         if np.isnan(x[0]) and np.isnan(x[1]):
    ##             polys[i] = np.array(temp,dtype=dtype)
    ##             temp = []
    ##             i += 1
    ##         else:
    ##             temp.append(x)
    ##     return polys
    #...

    def read_ply_file(self,filename,read_extra_columns=False):
        import glob
        """Read in polygons from a .ply file."""
        # It's useful to pre-compile a regular expression for a mangle line
        # defining a polygon.
        rePoly = re.compile(r"polygon\s+(-*\d+)\s+\(\s*(\d+)\s+caps")
        reWeight = re.compile(r"(-*\d*\.?\d+)\s+weight")
        reArea = re.compile(r"(-*\d*\.?\d+)\s+str")
        rePixel = re.compile(r"(-*\d*)\s+pixel")
        rePixelization = re.compile(r"pixelization\s+(-*\d+)([sd])")
        rePolycount = re.compile(r"(-*\d+)\s+polygons")
        reSnapped = re.compile(r"snapped")
        reBalkanized = re.compile(r"balkanized")
        reHeaderKeywords = re.compile(r"(-*\d+)\s+polygons|pixelization\s+(-*\d+)([sd])|balkanized|snapped")
        #
        ff = open(filename,"r")
        self.npoly = None
        self.pixelization=None
        self.snapped=False
        self.balkanized=False
        self.names=[]
        self.metadata={}
        line = ff.readline()
        #loop to read through header lines - stops when rePoly.match(line) returns something, indicating that we've
        #made it through the header and have reached a polygon.
        while (rePoly.search(line) is None)&(len(line)>0):
            sss=reHeaderKeywords.search(line)
            #if line starts with a header keyword, add the info as metadata
            if sss is not None:
                if rePolycount.search(line) is not None:
                    self.npoly = int( sss.group(1) )
                elif rePixelization.search(line) is not None:
                    self.pixelization = (int(sss.group(2)),sss.group(3))
                elif reSnapped.search(line) is not None: 
                    self.snapped = True
                elif reBalkanized.search(line) is not None:
                    self.balkanized = True
            #print warning if the line doesn't match any of the header keywords
            else:
                print "WARNING: line \""+line+"\" in "+filename+" ignored."
            #read next line
            line = ff.readline()
                
        if self.npoly is None:
            raise RuntimeError,"Did not find polygon count line \"n polygons\" in header of %s"%filename

        self.polylist = empty(self.npoly,dtype='object')
        self.polyids = zeros(self.npoly,dtype=int)
        self.areas = -ones(self.npoly)
        self.weights = zeros(self.npoly)
        self.ncaps = zeros(self.npoly,dtype=int)
        self.pixels = zeros(self.npoly,dtype=int)
        counter = 0
        ss = rePoly.search(line)
        while len(line)>0:
            while (ss==None)&(len(line)>0):
                line = ff.readline()
                ss   = rePoly.search(line)
            if len(line)>0:
                ipoly= int(ss.group(1))
                ncap = int(ss.group(2))
                # Check to see if we have a weight.
                ss = reWeight.search(line)
                if ss==None:
                    weight=0.0
                else:
                    weight=float(ss.group(1))
                # Check to see if we have an area.
                ss = reArea.search(line)
                if ss==None:
                    area= -1.0
                else:
                    area=float(ss.group(1))
                # Check to see if we have a pixel number.
                ss = rePixel.search(line)
                if ss==None:
                    pixel = 0
                else:
                    pixel=float(ss.group(1))
                self.polyids[counter] = ipoly
                self.areas[counter] = area
                self.weights[counter] = weight
                self.ncaps[counter] = ncap
                self.pixels[counter] = pixel
                # NOTE: Looping over a numpy array appears to be slower
                # than a python list, using a numpy array for polylist slows
                # down polyid(),area(),etc. by ~2x.  But it makes
                # the get_XX() functions cleaner.
                self.polylist[counter] = zeros((ncap,4))
                for i in range(ncap):
                    line = ff.readline()
                    cap  = [float(x) for x in string.split(line)]
                    self.polylist[counter][i] = cap
                ss=None
                counter += 1
        self.npixels = len(set(self.pixels))
        ff.close()

        #read in extra columns stored in this format:
        # polygon file named poly.pol or poly_obstime.pol (to denote that the polygons are weighted by observation time)
        # additional columns can be provided as poly.maglims, poly.obstime, poly.XXX where XXX is whatever tag applies to the column
        # an additional column will be added to the mangle polygon object named XXX 
        # additional column files should have number of rows equal to the number of polygons in poly.pol
        # this allows alternate weights and extra information about the polygons that are stored in a fits file to be written in ascii format      
        if read_extra_columns:
            #grab base name of file, e.g., poly.pol will yield base_filename=poly
            base_filename=string.split(self.filename,'.')[0]
            #get list of files that satisfy base_filename.* 
            files=glob.glob(base_filename+'.*')
            #remove any files that are clearly not meant to be extra column files from the list - anything that ends in .pol,.ply,.fits,.list,.list.weight, or .eps
            files=[f for f in files if (f[-4:] != '.ply') & (f[-4:] != '.pol') & (f[-5:] != '.fits') & (f[-5:] != '.list') & (f[-5:] != '.eps') &  (f[-12:] != '.list.weight')]
            #if that didn't find any files to read in, try stripping off everything after the final underscore for the basename, so poly_obstime.pol yields base_filename=poly
            if len(files)==0:
                weights_tag=string.split(base_filename,'_')[-1] 
                base_filename='_'.join(string.split(base_filename,'_')[:-1])
                files=glob.glob(base_filename+'.*')
                files=[f for f in files if (f[-4:] != '.ply') & (f[-4:] != '.pol') & (f[-5:] != '.fits') & (f[-5:] != '.list') & (f[-5:] != '.eps') &  (f[-12:] != '.list.weight')]
            #loop through files
            for f in files:
                try:
                    #basic file read that should work for anything with a fixed number of columns
                    data=np.genfromtxt(f,dtype=None,invalid_raise=True)
                except:
                    try:
                        #this can read a file that has a variable number of integers on each line - e.g., the output of the 'polyid' mangle function
                        data=array([array([int(x) for x in string.split(line)]) for line in open(f,'r')])                        
                    except:
                        try:
                            #this can read a file with a variable number of floats on each line
                            data=array([array([float(x) for x in string.split(line)]) for line in open(f,'r')])
                        except:
                            print 'WARNING: could not read column from file '+f
                            continue                            
                if len(data)!=self.npoly:
                    print 'number of lines in '+f+' does not match number of polygons in '+self.filename
                    continue
                name=string.split(f,'.')[-1]
                self.add_column(name,data)
                
    #...

    def convert_db(self, windows):
        """Read in polygons from a windows db table in photofielddb."""
        self.npoly = len(windows)
        self.pixelization=None

        # pull out the relevant fields
        self.polylist= empty(self.npoly,dtype='object')
        self.polyids= arange(0,self.npoly,dtype=int)
        self.npixels = 0
        self.areas= zeros(self.npoly, dtype= 'float64')
        self.weight= zeros(self.npoly, dtype= 'float32')
        self.pixels= zeros(self.npoly, dtype= 'int32')
        self.ifield= zeros(self.npoly, dtype= 'int32')
        self.ncaps= zeros(self.npoly, dtype='int32')
        for i in range(self.npoly):
            self.areas[i]= windows[i].str
            self.weight[i]= windows[i].weight
            self.pixels[i]= windows[i].pixel
            self.ifield[i]= windows[i].ifield
            self.ncaps[i] = windows[i].ncaps
        for i,n,w in zip(self.polyids,self.ncaps,windows):
            self.polylist[i] = zeros((n,4))
            self.polylist[i][...,:-1] = array(w.xcaps[:3*n]).reshape(n,3)
            self.polylist[i][...,-1] = w.cmcaps[:n]
    #...

    def read_fits_file(self,filename):
        """Read in polygons from a .fits file."""
        data = pyfits.open(filename,memmap=True)[1].data
        header = pyfits.open(filename,memmap=True)[0].header
        self.npoly = len(data)
        self.pixelization=None
        self.snapped=False
        self.balkanized=False
        self.names=[]
        self.formats=()
        names = data.dtype.names
        formats=data.formats

        #if mangle header keywords are present, use them
        if ('PIXRES' in header.keys()) & ('PIXTYPE' in header.keys()) &  ('SNAPPED' in header.keys()) &  ('BLKNIZED' in header.keys()):
            self.pixelization=(header['PIXRES'], header['PIXTYPE'])
            self.snapped=header['SNAPPED']
            self.balkanized=header['BLKNIZED']
        #if mangle header keywords aren't present, check for text in header that looks like the header of an ascii polygon file:
        else:
            rePixelization = re.compile(r"pixelization\s+(\d+)([sd])")
            reSnapped = re.compile(r"snapped")
            reBalkanized = re.compile(r"balkanized")
            reHeaderKeywords = re.compile(r"pixelization\s+(\d+)([sd])|balkanized|snapped")
            cardlist=header.ascardlist()

            for card in header.ascardlist():
                line=str(card)
                sss=reHeaderKeywords.search(line)
            #if line starts with a header keyword, add the info as metadata
                if sss is not None:
                    if rePixelization.search(line) is not None:
                        self.pixelization = (int(sss.group(1)),sss.group(2))
                    elif reSnapped.search(line) is not None: 
                        self.snapped = True
                    elif reBalkanized.search(line) is not None:
                        self.balkanized = True
        
        # pull out the relevant fields
        self.polylist = empty(self.npoly,dtype='object')
        self.polyids = arange(0,self.npoly,dtype=int)
        if 'STR' in names:
            self.areas = data['STR']
        else:
            self.areas = -ones(self.npoly)
        if 'WEIGHT' in names:
            self.weights = data['WEIGHT']
        else:
            self.weights = zeros(self.npoly)
        if 'PIXEL' in names:
            self.pixels = data['PIXEL']
        else:
            self.pixels = zeros(self.npoly,dtype=int)
        self.npixels = len(set(self.pixels))
        self.ncaps = data['NCAPS']
        for i,n,x in izip(self.polyids,self.ncaps,data):
            self.polylist[i] = zeros((n,4))
            self.polylist[i][...,:-1] = x['XCAPS'].reshape(-1,1)[:3*n].reshape(n,3)
            self.polylist[i][...,-1] = x['CMCAPS'].reshape(-1)[:n]

        # Read any additional fields that may be in the file
        info=data.columns.info(output=False)
        self.metadata={}
        for i, name in enumerate(names):
            if ((name != 'XCAPS') & (name != 'CMCAPS') & (name != 'NCAPS') & (name != 'STR') & (name != 'WEIGHT') & (name != 'PIXEL')):
               # fits files use bzero and bscale along with signed int data types to represent unsigned integers
                # e.g. for an unsigned 32 bit integer, the format code will be 'J' (same as for a signed 32 bit int),
                # bscale will be 1 and bzero will be 2**31.  The data gets automatically converted as data=bscale*rawdata+bzero
                if (info['bscale'][i] == 1.0) & (info['bzero'][i] is not ''):
                    precision=str(np.int(np.log2(np.abs(np.double(info['bzero'][i])))+1)) # equal to '8', '16','32', '64'
                    if ((precision == '16') | (precision == '32') | (precision == '64')) & (info['bzero'][i]>0):
                        #define a numpy data type that is an unsigned int of the given precision
                        dt=np.typeDict['uint'+precision]
                        col = dt(data[name])
                    #for 8 bit ints, it's vice-versa: fits natively has an unsigned 8 bit int and requires bzero to convert to signed.
                    elif (precision == '8') & (info['bzero'][i]<0):
                        #define a numpy data type that is an unsigned int of the given precision 
                        dt=np.typeDict['int'+precision]
                        col = dt(data[name])
                    else:
                        col = data[name]
                else:
                    col = data[name]
                self.add_column(string.lower(name), col, format=info['format'][i], asciiformat=None, unit=info['unit'][i], null=info['null'][i], bscale=info['bscale'][i], bzero=info['bzero'][i], disp=info['disp'][i], start=info['start'][i], dim=info['dim'][i])


    def add_column(self,name, data, format=None, asciiformat=None, unit=None, null=None, bscale=None, bzero=None, disp=None, start=None, dim=None):
        """Add a column to the polygons object. Keyword arguments are the same as the pyfits.Column constructor.
        Format will be detected automatically from the data type if not provided."""
        #check to make sure length of array matches number of polygons
        if len(data) != self.npoly:
            raise RuntimeError('Length of array does not match number of polygons.')
        #detect dimensions of array
        if data.ndim==1:
            size=''
        elif data.ndim==2:
            size=str(data.shape[-1])
        elif data.ndim>2:
            size=str(np.prod(data.shape[1:]))
            if dim is None:
                dim=str(data.shape[1:])

        if data.dtype.type is np.object_:
            size='P'
            dt=data[0].dtype.type
        else:
            dt=data.dtype.type
                
        #detect appropriate format based on numpy type
        #use bzero and bscale for unsigned integers                  
        if dt is np.float64:
            ftype='D'
            asciiformat='%.15g'
        elif dt is np.int32:
            ftype='J'
            asciiformat='%d'
        elif dt is np.uint32:
            ftype='J'
            bzero=2**31
            bscale=1
            asciiformat='%u'
        elif dt is np.string_:
            #add the string length to the dimensions in order to store an array of strings
            dims=(data.dtype.itemsize,)+data.shape[1:]
            size=str(np.prod(dims))
            if len(dims)>1:
                if dim is None:
                    dim=str(dims)
                ftype='A'
            asciiformat='%s'
        elif dt is np.float32:
            ftype='E'
            asciiformat='%.6g'
        elif dt is np.int16:
            ftype='I'
            asciiformat='%d'
        elif dt is np.uint16:
            ftype='I'
            bzero=2**15
            bscale=1
            asciiformat='%u'
        elif dt is np.int64:
            ftype='K'
            asciiformat='%d'
        elif dt is np.uint64:
            #64 bit unsigned ints don't work right now b/c scaling is done by converting bzero to a double, which doesn't have enough precision
            #format='K'
            #bzero=2**63
            #use 32 bit unsigned int instead:
            type='J'
            bzero=2**31
            bscale=1
            asciiformat='%d'
        elif dt is np.complex64:
            ftype='C'
            asciiformat=None
        elif dt is np.complex128:
            ftype='M'
            asciiformat=None
        elif dt is np.bool_:
            ftype='L'
            asciiformat='%d'
        elif dt is np.int8:
            ftype='B'
            bzero=-2**7
            bscale=1
            asciiformat='%d'
        elif dt is np.uint8:
            ftype='B'
            asciiformat='%u'
        else:
            raise RuntimeError('data type '+str(dt)+' not supported')

        if size=='P':
            asciiformat=None
        if format is None:
            format=size+ftype
            if size=='P':
                format=format+'()'
        
        self.metadata.update({name:{'bscale':bscale,
                                    'bzero':bzero,
                                    'dim':dim,
                                    'disp':disp,
                                    'format':format,
                                    'asciiformat':asciiformat,
                                    'name':string.upper(name),
                                    'null':null,
                                    'start':start,
                                    'unit':unit}})
        vars(self)[name] = data
        self.names+=[name]

    def remove_column(self,name):
        """removes a column from the polygon structure and metadata"""
        del vars(self)[name]
        del self.metadata[name]
        self.names.remove(name)
        
    def write_fits_file(self,filename,clobber=True,keep_ids=False):
        """Write polygons to a .fits file."""

        #define size of xcaps and cmcaps arrays based on the maximum number of caps in any polygon, fill extra spaces with zeros
        maxn=self.ncaps.max()

        #initialize to zero-filled arrays
        xcaps=zeros((len(self.polylist),maxn,3))
        cmcaps=zeros((len(self.polylist),maxn))

        #run through polygons and massage caps data in polylist to fit into cmcaps and xcaps arrays
        polyids=arange(0,self.npoly,dtype=int)
        for i,n,poly in izip(polyids,self.ncaps,self.polylist):
            cmcaps[i,:n]= poly[...,-1]
            xcaps[i,:n]=poly[...,:-1]

        #reshape xcaps array to have dimensions (npolys, 3*maxn) rather than (npolys,maxn,3) to keep pyfits happy  
        xcaps=xcaps.reshape(-1,3*maxn)

        #if keeping polygon id number in fits file, add 'ids' column
        if keep_ids == True:
            if 'ids' not in self.names:
                self.add_column('ids',self.polyids)

        #define pyfits columns for basic polygon file elements
        xcaps_col=pyfits.Column(name='XCAPS',format=str(3*maxn)+'D',dim='( 3, '+str(maxn)+')',array=xcaps)
        cmcaps_col=pyfits.Column(name='CMCAPS',format=str(maxn)+'D',array=cmcaps)
        ncaps_col=pyfits.Column(name='NCAPS',format='J',array=self.ncaps)
        str_col=pyfits.Column(name='STR',format='D',array=self.areas)
        weight_col=pyfits.Column(name='WEIGHT',format='D',array=self.weights)
        pixel_col=pyfits.Column(name='PIXEL',format='J',array=self.pixels)

        #define pyfits columns for any extra columns listed in self.names
        extracols=[]
        for name in self.names:
            info=self.metadata[name]
            data=vars(self)[name]
            #reshape arrays into 1-dim arrays so pyfits can deal
            if data.dtype.type is np.string_:
                if data.ndim>1:
                    raise RuntimeError('arrays of strings not supported for exporting to fits file.')
                   # using the line below give "operands could not be broadcast together" error
                   #  data=array([''.join([a.ljust(data.dtype.itemsize) for a in x.flat]) for x in data])                 
            else:
                if data.ndim>2:
                    data=data.reshape(-1,np.prod(data.shape[1:]))
            col=pyfits.Column(name=info['name'],
                              format=info['format'],
                              bscale=info['bscale'],
                              bzero=info['bzero'],
                              dim=info['dim'],
                              disp=info['disp'],
                              null=info['null'],
                              start=info['start'],
                              unit=info['unit'],
                              array=data)
            extracols=extracols+[col]

        #make a primary HDU for the table and add metadata
        primary=pyfits.PrimaryHDU()
        if self.pixelization is not None:
            primary.header.update('PIXRES',self.pixelization[0])
            primary.header.update('PIXTYPE',self.pixelization[1])    
        primary.header.update('SNAPPED',self.snapped)
        primary.header.update('BLKNIZED',self.balkanized)

        #make new fits table and write it to file 
        table=pyfits.new_table(pyfits.ColDefs([xcaps_col,cmcaps_col,ncaps_col,weight_col,pixel_col,str_col]+extracols))
        tablehdus=pyfits.HDUList([primary, table])
        tablehdus.writeto(filename,clobber=clobber)

    def __init__(self,filename,db=False,keep_ids=False,read_extra_columns=False):
        """
        Initialize Mangle with a file containing the polygon mask.
        If db == True, filename is expected to be a windows db table.

        Acceptable formats (determined from the file extension):
            .ply or .pol <-- Mangle polygon files:
                http://space.mit.edu/~molly/mangle/manual/polygon.html
            .fits <-- FITS file
            windows db table <-- if db == True
        """
        if db == True:
            self.convert_db(filename)
            self.filename == None
        else:
            if not os.path.exists(filename):
                raise IOError,"Can not find %s"%filename
            self.filename = filename # useful to keep this around.
            if (filename[-4:] == '.ply') | (filename[-4:] == '.pol'):
                self.read_ply_file(filename,read_extra_columns=read_extra_columns)
            elif filename[-5:] == '.fits':
                self.read_fits_file(filename)
            else:
                raise IOError,"Unknown file extension for %s"%filename

        if len(self.polylist) != self.npoly:
            print "Got %d polygons, expecting %d."%\
              (len(self.polylist),self.npoly)
        if keep_ids == True:
            self.add_column('ids',self.polyids)
            self.polyids=arange(0,self.npoly,dtype=int)
        else:                
            # Check whether the polyids are sequential and range from 0 to npoly-1
            # If they don't, then there may be a problem with the file.
            # NOTE: this should always be correct for current_boss_geometry.
            badcounter = 0
            if (min(self.polyids)==0) & (max(self.polyids)==self.npoly-1) :
                for i,polyid in enumerate(self.polyids):
                    if i != polyid:
                        badcounter += 1
                if badcounter > 0:
                    print "WARNING!!!!"
                    print "Found",badcounter,"polygons out of order."
                    print "Reordering polygons so that polyid=index"
                    sorter = argsort(self.polyids)
                    self.polylist = take(self.polylist,sorter)
                    self.weights = self.weights[sorter]
                    self.areas = self.areas[sorter]
                    self.polyids = self.polyids[sorter]
                    badcounter = 0
            else:
                print "WARNING!!!!"
                print "Range of polygon ids in input is (",min(self.polyids),",",max(self.polyids),"), not ( 0 ,",self.npoly-1,")"
                print "Forcing 'polyids' attribute to be 0 to npoly-1 and saving ids from input as 'id' attribute"
                print "To do this automatically, use 'keep_ids=True' in the mangle.Mangle constructor."
                print "To write polygon file retaining the input ids, use 'keep_ids=True' in writeply()."
                self.add_column('ids',self.polyids)
                self.polyids=arange(0,self.npoly,dtype=int)
     #...
#...

#def quad2doubledouble(quad):
#    if quad.dtype==np.float128:
#        t=(2**57+1)*quad
#        hi=t-(t-quad)
#        lo=quad-hi
#        doubledouble=np.complex128(hi+lo*j)
#    else:
#        raise TypeError("error: quad value is wrong datatype")
#    return doubledouble        
    

#def doubledoubletoquad(doubledouble):
