'''
Author: Benyang Tang, btang(noSpam)@pacific.jpl.nasa.gov
Modified by: Nickolas Fotopoulos, nvf(noSpam)@mit.edu
Modified by: Alan C. Brooks, alancbrooks(noSpam)@gmail.com

2005 Version posted at:
    http://projects.scipy.org/scipy/scipy/attachment/ticket/14

========
Documentation:
========
This module, numpyIO, is an implementation in python of the c version of
SciPy's numpyio by Travis Oliphant. The advantage of using numpyIO is the ease
of installation: numpyIO depends only on numpy and does not need scipy.

Initial benchmarking with 10000000 samples indicates that numpyIO is about 5%
faster than SciPy's numpyio module.

Only 2 functions were implemented: fread and fwrite.

The interfaces of the 2 functions here are exactly the same as those of
numpyio. If you have code using numpyio, you don't have to change anything to
call fread and fwrite, except changing numpyio to numpyIO.

=======
Roadmap:
=======
Scipy's "IO Roadmap" on http://projects.scipy.org/scipy/scipy/roadmap says:

Reworking of IO package

The IO code in both NumPy and SciPy is undergoing a major reworking. NumPy
will be where basic code for reading and writing NumPy arrays is located,
while SciPy will house file readers and writers for various data formats
(data, audio, video, images, matlab, excel, etc.). This reworking started
NumPy 1.1.0 and will take place over many release. SciPy 0.7.0 has several
changes including:

Several functions in scipy.io have been deprecated and will be removed in the
0.8.0 release including npfile, save, load, create_module, create_shelf,
objload, objsave, fopen, read_array, write_array, fread, fwrite, bswap,
packbits, unpackbits, and convert_objectarray. Some of these functions have
been replaced by NumPy's raw reading and writing capabilities, memory-mapping
capabilities, or array methods. Others have been moved from SciPy to NumPy,
since basic array reading and writing capability is now handled by NumPy.

=======
History:
=======
2009-01-03: Read the roadmap and realized that I probably should be using 
            np.fromfile/tofile or np.memmap ... rewrote using to/fromfile
            and now it is often *faster* than SciPy's numpyio.
2009-01-01: Happy with refactored implementation and complete tests (ACB).
2008-12-30: Cleanup and port to numpy 1.3.0 (ACB).
2005-09-02: Added a few new read_types to support Matlab R14 mat-files. Not
            comprehensive.
2003-03-31: Coded and tested.
'''

import numpy as np

def fread(fid, num, read_type, mem_type=None, byteswap=0):
    '''g = numpyIO.fread(fid, num, read_type, {mem_type, byteswap})
     
     fid =       open file pointer object (i.e. from fid = open("filename") )
     num =       number of elements to read of type read_type (-1 for all)
     read_type = a character describing how to interpret bytes on disk:
                    1 byte  => b, B, c, S1
                    2 bytes => h, H
                    4 bytes => f, i, I, l, u4
                    8 bytes => d, F
                   16 bytes => D
OPTIONAL
     mem_type =  a character (PyArray type) describing what kind of
                 PyArray to return in g.   Default = read_type
     byteswap =  0 for no byteswapping or a 1 to byteswap (to handle
                 different endianness).    Default = 0'''

    # figure out mem_type
    if not mem_type:
        mem_type = read_type

    # read in
    a = np.fromfile(fid, dtype=read_type, count=num)

    # adjust for byteswap & mem_type
    if byteswap:
        a.byteswap(True)
    if read_type!=mem_type:
        a = a.astype(mem_type)

    return a


def fwrite(fid, num, a, write_type=None, byteswap=0):
    '''numpyIO.fwrite(fid, num, myArray, {write_type, byteswap})
     
     fid =       open file stream
     num =       number of elements to write (-1 for all)
     a =         NumPy array holding the data to write (will be
                 written as if ravel(myarray) was passed)
OPTIONAL
     write_type = character describing how to write data (what datatype
                  to use)                  Default = type of myarray.
                    1 byte  => b, B, c, S1
                    2 bytes => h, H
                    4 bytes => f, i, I, l, u4
                    8 bytes => d, F
                   16 bytes => D
     byteswap =   0 or 1 to determine if byteswapping occurs on write.
                  Default = 0.'''

    # figure out inputs
    mem_type = a.dtype.char
    if not write_type:
        write_type = mem_type
    if num==-1:
        num = a.size

    # if not all elements are written
    if num!=a.size:
        a = a.ravel()[:num]

    # adjust for byteswap & write_type
    if mem_type!=write_type:
        a = a.astype(write_type)
    if byteswap:
        a = a.byteswap()
    
    # write
    a.tofile(fid)
    

def _timed(func):
    '''Decorator that prints & returns the time it takes to run a function'''
    import time
    def wrapper(*__args,**__kw):
        start = time.time()
        out = func(*__args,**__kw)
        end = time.time()
        dt = end-start
        print "in %f sec" % dt,
        return (out, dt)
    return wrapper
    
def _subtestReadWrite(a, size, fn, fread, fwrite, what='Some'):
    import os
    print " %s testing .." % what,
    
    # Speed tests
    @_timed
    def innerSpeedTestWrite():
        fwrite(fid, size, a)
    @_timed
    def innerSpeedTestRead():
        return fread(fid, size, 'd')
    with open(fn,'w+b') as fid:
        tmp, dtW = innerSpeedTestWrite()
    with open(fn,'rb') as fid:
        a1, dtR = innerSpeedTestRead()
    os.remove(fn)
    
    # Test more options
    b = a[:10] # only use a few values for these tests
    with open(fn,'w+b') as fid:
        fwrite(fid, b.size, b, 'd', 1)
        fid.seek(0)
        # all data types: 'bBcS1hHfiIlu4dFD'
        b2 = fread(fid, b.size, 'd', 'f', 1) # convert to floats
        fid.seek(0)
        b3 = fread(fid, b.size, 'd', 'i', 1) # convert to int32
        fid.seek(0)
        b4 = fread(fid, b.size, 'd', 'b', 1) # convert to int8
        fid.seek(0)
        b5 = fread(fid, b.size, 'd', 'h', 1) # convert to int16
    os.remove(fn)
    
    # Finalize stuff
    if all(a == a1) and all(abs(b-b2) < 0.01) and \
       all(abs(b-b3) < 1) and all(abs(b-b4) < 1) and all(abs(b-b5) < 1):
        print ".. passed"
    else:
        print ".. failed"
        print " a=%s\na1=%s\nb2=%s\nb3=%s\nb4=%s\nb5=%s" % (
            a, a1, b2, b3, b4, b5)
    return dtW+dtR

@_timed
def _testFreadFwrite():
    # Unit tests of fread/fwrite
    from scipy.io import numpyio
    import time
    
    n = 10e5 #10e5 for quick dev; 10e6 for longer benchmark
    a = 127*(np.random.random_sample(n)-0.5)
    fn = 'temp.bin'
    dt = []
    print "Testing numpyIO with %d random samples written/read:" % n
    
    # Baseline scipy.io.numpyio
    t1 = _subtestReadWrite(a, a.size, fn, numpyio.fread, numpyio.fwrite, 
                           'numpyio')
    
    # Test this new package numpyIO & compare speed to baseline
    t2 = _subtestReadWrite(a, a.size, fn, fread, fwrite, 'numpyIO')
    
    # Mix the two
    t3 = _subtestReadWrite(a, a.size, fn, fread, numpyio.fwrite, 'numpyIo')
    t4 = _subtestReadWrite(a, a.size, fn, numpyio.fread, fwrite, 'numpyiO')
    
    # Print the relative results
    def printSlower(t1, t2, what1='a', what2='b'):
        speed = ('slower','faster')[t2<t1]
        print " %s is %2d%% %s than %s" % (
            what2, 100*abs(t2-t1)/t1, speed, what1)
    printSlower(t1, t2, "SciPy's numpyio", "numpyIO")
    printSlower(t1, t3, "SciPy's numpyio", "numpyIo")
    printSlower(t1, t4, "SciPy's numpyio", "numpyiO")
        
def _testAutoNum():
    import os
    print "Testing auto num feature of numpyIO ..",
    a = np.array((1,2,3),'d')
    fn = 'temp2.bin'
    with open(fn,'w+b') as fid:
        fwrite(fid, -1, a)
        fid.seek(0)
        a1 = fread(fid, -1, 'd')
    os.remove(fn)
    if all(a == a1):
        print "passed"
    else:
        print "failed"
        print " a=%s\na1=%s" % (a, a1)
    
def test():
    '''Run all unit tests'''
    _testAutoNum()
    _testFreadFwrite()
    
if __name__=='__main__':
    test()
