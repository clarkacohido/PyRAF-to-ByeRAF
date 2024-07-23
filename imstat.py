#!/usr/bin/env python
# coding: utf-8

"""imstat

this script is meant to replicate the functionality of the imstatistics task in IRAF

PARAMETERS:
    image
        the imput image or image region that is computed

    fields='image,npix,mean,stddev,min,max'
        statistical quantities that will be printed or returned
        valid fields:
            image - image name
            npix - number of pixels in the image or image region
            mean - average pixel value
            midpt - estimate of the median pixel distribution
            mode - mode of the digitized pixel distribution
            stddev - standard deviation of the pixel distribution
            skew - skew of the pixel distribution
            kurtosis - kurtosis of the pixel distribution
            min - minimum pixel value
            max - maximum pixel value
        
            the npix, mean, midpt, stddev, min, and max fields are 
            calculated using numpy functions. the mode, skew, and 
            kurtosis functions use scipy stats. for the midpt and mode
            are calculated by digitizing the pixel data of the image
            region and calculating the mode and interpolated median of
            the digitized data

    lower = '-inf'
        minimum good data cutoff. no pixels are cutoff by default

    upper = 'inf'
        maximum good data cutoff. no pixels are cutoff by default

    nclip = 0
        number of iterative clipping cycles. no clipping is performed by 
        default

    lsigma = 3.0
        low side clipping factor. units are in standard deviations (sigma)
        
    usigma = 3.0
        high side clipping factor. units are in sigma

    binwidth = 0.1
        bin width used for creating digitized data in midpt and mode 
        calculation. units are in sigma

    format = 'yes'
        label the output columns

    Stdout = False
        when enabled the function will return the values as an object the
        dtype of the object can be changed by the returnType parameter. by
        default a string is returned

    returnType = 'str'
        data type of the output that gets returned when Stdout = True
        valid fields:
            'str' - string (default). if format = 'yes' then the output will
            be an array containing a string of all fields and a string with
            the calculated values in corresponding order
            
            'arr' - array of values where each field is an array element. if
            format = 'yes' the output will be a a 2d array containing the an
            array of the fields and an array of the corresponding values
            
            'dict' - a dictionary where the fields are keys containing the
            corresponding values


version 1 - July 12, 2024

12Jul 2024: Implemented fields parameter
19Jul 2024: Implemented the binwidth, upper, and lower parameters
22Jul 2024: Implemented sigma clipping
23Jul 2024: Made correction to midpt and mode functions. added documentation
24Jul 2024: Implemented format Stdout and returnType parameters


bugs:
24Jul 2024: Stdout is not interpreting 'False' or '0' correctly from user input.  this issue only occurs when executing in the command line not in a python environment


"""

import numpy as np
from scipy import stats
from statistics import stdev

import argparse
from parse import fparse

__version__ = '20240726'
__author__ = 'clarkacohido'

def main(instring, 
           fields ='image,npix,mean,stddev,min,max',
            lower = float('-inf'),
            upper = float('inf'),
            nclip = 0,
            lsigma = 3.0,
            usigma = 3.0,
            binwidth = 0.1,
            format = 'yes',
            Stdout = False,
            returnType='str'
            ):
            
    ###parsed string (should be a dictionary)
    ps = fparse(instring)

    if ps == False:
        print('file not found')
        return

    ###field array
    farray = list(fields.split(','))

    ###fits data (already masked based on x/y lims in the input)
    dat = np.where((ps['data'] >= lower) & (ps['data'] <= upper), ps['data'], np.nan)
    
    ###sigma clipping
    for i in range(nclip):
        sig = np.nanstd(dat) ##stddev - the standard deviation of the pixel distribution
        mean = np.nanmean(dat) ##mean - the mean of the pixel distribution
        dat = np.where((dat >= mean - (lsig * sig)) & (dat <= mean + (usig * sig)), dat, np.nan)
    

    ###field dictionary
    fd = {}
    fd["stddev"] = np.nanstd(dat) ##stddev - the standard deviation of the pixel distribution
    fd["mean"] = np.nanmean(dat) ##mean - the mean of the pixel distribution
    fd['image'] = ps['image']
    fd["npix"] = np.count_nonzero(~np.isnan(dat))##npix - the number of pixels used to do the statistics
    fd["skew"] = stats.skew(dat.flatten(), nan_policy="omit", keepdims=True)[0] ##skew - the skew of the pixel distribution
    fd["kurtosis"] = stats.kurtosis(dat.flatten(), nan_policy="omit", keepdims=True)[0] ##kurtosis - the kurtosis of the pixel distribution
    fd["min"] = np.nanmin(dat) ##min - the minimum pixel value
    fd["max"] = np.nanmax(dat) ##max - the maximum pixel value
    #fd["midpt"] = np.nanmedian(dat.flatten()) ##midpt - estimate of the median of the pixel distribution

    bins = np.arange(fd['min'], fd['max'], binwidth*fd['stddev'])
    
    ##returns indices of bins where the data point would be
    ibindat = np.digitize(dat, bins)
    digidat = []
    
    for n in ibindat.flatten():
        digidat.append(bins[n-1]) ## -1 because it gives the bin number, not the index so its starts from 1 instead of 0
        
    fd["mode"] = stats.mode(digidat, nan_policy='omit')[0]##mode - the mode of the pixel distribution

    
    ##this is the 'true' median used to calculate the interpolated median:
    #trmed = bins[int(np.nanmedian(ibindat))-1] ## -1 because it gives the bin number, not the index so its starts from 1 instead of 0
    trmed = np.nanmedian(digidat)
    
    
    n1 = len([n for n in digidat if n < trmed])
    n2 = len([n for n in digidat if n == trmed])
    
    if n2 == 0:
        fd['midpt'] = trmed
    else:
        numer = (0.5 * len(digidat)) - n1
        fd['midpt'] = trmed - 0.5 + (numer / n2)
        

    headerAr = []
    header = ''
    
    valueAr = []
    value = ''
    
    
    
    for x in farray:
            try:
                valueAr.append(fd[x]) ##must be first in order to catch key exception
                headerAr.append(x)
                
                ##these are the values that will be printed
                valuePrint = str(value) + str(fd[x]) + '    '
                headerPrint = header + x + '    '
                
                ##these are the strings that will be returned in the output dictrionary
                value = str(value) + str(fd[x]) + ','
                header = header + x + ','
    
            except KeyError:
                ##ignore because there is a keyError (like if theres an invalid field)
                print('invalid field(s): ' + x)
    
    
    
    ##output dictionary for the returnType parameter
    dictOut = {}
    
    if format.lower() == 'yes':
        dictOut['str'] = [header, value]
        dictOut['arr'] = [headerAr, valueAr]
        print(headerPrint)
        print(valuePrint)
    elif format.lower() == 'no':
        dictOut['str'] = value
        dictOut['arr'] = valueAr
        print(valuePrint)
    else:
        print('unknown parameter: ' + format)
    
    ##temporary dictionary made to combine the headers (keys) and values and adds it to the output dictionary
    temp = {}
    
    for i in range(len(valueAr)):
        temp[headerAr[i]] = valueAr[i]
        
    dictOut['dict'] = temp
    
    
    try:     
        if Stdout != False:
            return(dictOut[returnType])
    except KeyError:
        print('Unrecognized returnType')







    
def create_parser():
    prog        = r"""imstat.py"""
    usage       = r"""imstat.py <filename> --<parameter>=<value>"""
    description = r"""finds and returns image statistics"""
    epilog      = "Version: " + __version__
    
    parser = argparse.ArgumentParser(prog=prog, usage=usage, description=description, epilog=epilog)
    parser.add_argument('instring', help='user input string')
    parser.add_argument('--fields', type=str, help='which fields need to be returned. valid fields: image,npix,mean,stddev,min,max,skew,kurtosis,mode,midpt', default='image,npix,mean,stddev,min,max')
    parser.add_argument('--lower', type=float, help="lowest acceptable pixel value", default=float('-inf'))
    parser.add_argument('--upper', type=float, help="highest acceptable pixel value", default=float('inf'))
    parser.add_argument('--nclip', type=int, help="number of clipping cycles. by default no clipping is done", default=0)
    parser.add_argument('--lsig', type=float, help="low side clipping factor in number of sigmas", default=3.0)
    parser.add_argument('--usig', type=float, help="high side clipping factor in number of sigmas", default=3.0)
    parser.add_argument('--binwidth', type=float, help="width of the histogram bins used to estimate midpt and mode", default=0.1)
    parser.add_argument('--format', type=str, help="label the output columns. if format = 'no' there are no column labels printed. by default format='yes'", default='yes')
    parser.add_argument('--Stdout', type=bool, help="returns values as an array of strings when enabled. default Stdout=False ", default=False)
    parser.add_argument('--returnType', type=str, help="type of data that gets returned when Std=True. valid data types: str,arr,dict ", default='str')
    
    return parser

if __name__ == '__main__':
    parser   = create_parser()
    args     = parser.parse_args()
    instring = args.instring
    fields = args.fields
    lower=args.lower
    upper=args.upper
    nclip=args.nclip
    lsig=args.lsig
    usig=args.usig
    binwidth=args.binwidth
    format=args.format
    Stdout=args.Stdout
    returnType=args.returnType
    
    main(instring, fields, lower, upper, nclip, lsig, usig, binwidth, format, Stdout, returnType)
    