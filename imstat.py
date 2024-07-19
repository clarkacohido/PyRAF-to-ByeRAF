#!/usr/bin/env python
# coding: utf-8

"""imstat

Task that replicates the imstatistics function in IRAF

version 1 - July 12, 2024

12Jul 2024: got fields parameter working as intended. image field is also fixed now
19Jul 2024: implemented the binwidth parameter

"""

import numpy as np
from scipy import stats
from statistics import stdev

import argparse
from parse import fparse

__version__ = '20240710'
__author__ = 'clarkacohido'

def main(instring, 
           fields ='image,npix,mean,stddev,min,max',
            #lower = float('-inf'),
            #upper = float('inf'),
            #nclip = 0,
            #lsigma = 3.0,
            #usigma = 3.0,
            binwidth=0.1
            #cache - I have no intent on doing this one in the future
            ##i listed all of the parameters that are available in IRAF even if I haven't implemented them yet
            ):
            
    ###parsed string (should be a dictionary)
    ps = fparse(instring)

    if ps == False:
        print('file not found')
        return

    ###field array
    farray = list(fields.split(','))

    ###fits data (already masked based on x/y lims in the input)
    dat = ps['data']

    ###field dictionary
    fd = {}
    fd['image'] = ps['image']
    fd["npix"] = dat.size##npix - the number of pixels used to do the statistics
    fd["mean"] = np.nanmean(dat) ##mean - the mean of the pixel distribution
    fd["stddev"] = np.nanstd(dat) ##stddev - the standard deviation of the pixel distribution

    fd["skew"] = stats.skew(dat.flatten(), nan_policy="omit", keepdims=True)[0] ##skew - the skew of the pixel distribution
    fd["kurtosis"] = stats.kurtosis(dat.flatten(), nan_policy="omit", keepdims=True)[0] ##kurtosis - the kurtosis of the pixel distribution
    fd["min"] = np.nanmin(dat) ##min - the minimum pixel value
    fd["max"] = np.nanmax(dat) ##max - the maximum pixel value
    fd["midpt"] = np.nanmedian(dat.flatten()) ##midpt - estimate of the median of the pixel distribution

    bins = np.arange(fd['min'], fd['max'], binwidth*fd['stddev'])
    ibindat = np.digitize(dat, bins)
    digidat = []
    
    for n in ibindat.flatten():
        digidat.append(bins[n-1])

    
    ##this is the 'true' median, but now im gonna try to calculate the interpolated median:
    trmed = bins[int(np.nanmedian(ibindat))]

    
    n1 = len([n for n in digidat if n < trmed])
    
    if digidat.count(trmed) <= 1:
        fd['midpt'] = trmed
    else:
        numer = (0.5 * len(digidat)) - n1
        fd['midpt'] = trmed - 0.5 + (numer / digidat.count(trmed))
        
        fd["mode"] = stats.mode(digidat, nan_policy='omit')[0]#np.digitize(dat, bindices)) ##mode - the mode of the pixel distribution
        
    header = []
    outputs = []

    for x in farray:
        try:
            outputs.append(fd[x])
            header.append(x)
        except KeyError:
            ##ignore this value because its not a valid field
            continue

    print(header)
    print(outputs)
    

    
def create_parser():
    prog        = r"""imstat.py"""
    usage       = r"""imstat.py <filename> --fields=min,max,npix"""
    description = r"""finds and returns image statistics"""
    epilog      = "Version: " + __version__
    
    parser = argparse.ArgumentParser(prog=prog, usage=usage, description=description, epilog=epilog)
    parser.add_argument('instring', help='user input string')
    parser.add_argument('--fields', type=str, help='valid fields: image,npix,mean,stddev,min,max,skew,kurtosis,mode,midpt', default='image,npix,mean,stddev,min,max')
    parser.add_argument('--binwidth', type=float, help="width of the histogram bins used to estimate midpt and mode", default=0.1)    
    
    return parser

if __name__ == '__main__':
    parser   = create_parser()
    args     = parser.parse_args()
    instring = args.instring
    fields = args.fields
    binwidth=args.binwidth
    
    main(instring, fields, binwidth)
    