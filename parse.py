#!/usr/bin/env python
# coding: utf-8

"""parse.py

used to parse input strings for use in other functions

12 July 2024: took out the file dir and replaced it with os.getcwd()
26 July 2024: removed unnecessary or redundant code

notes: MEF files are not supported in this script. only fits files will work

version 2 - July 10, 2024

"""

import os
import numpy as np
from astropy.io import fits
import argparse

__version__ = "20240726"
__author__="clarkacohido"


def fparse(inputstring):

    fields = inputstring.split()
    final = {}

    imname = fields[0]
    
    ##find brackets after the image name containing the desired bounds
    if imname.find('[') == -1:
        finalim = imname
        try:
            fits.open(finalim)
        except Exception as e:
            print(e)
            print('File (' + finalim + ') not found.')
            return
    else:
        finalim = imname[:imname.find('[')]
        try:
            fits.open(finalim)
        except Exception as e:
            print(e)
            print('File (' + finalim + ') not found.')
            return

    final['image'] = finalim
        

    if imname.find('[') != -1:
        
        try:
            ranges = imname[imname.find('[')+1:imname.find(']')]

            xandy = ranges.split(',')
            xrange = xandy[0].split(':')
            yrange = xandy[1].split(':')

            ##image region
            final['x min'] = int(xrange[0])-1
            final['x max'] = int(xrange[1])
            
            final['y min'] = int(yrange[0])-1
            final['y max'] = int(yrange[1])
            
        except Exception as e:
            print('error: ' + str(e))
            
    fitsfile = fits.open(final["image"])
    fitsdata = fitsfile[0].data

    try:
        fitsdata = fitsdata[final['y min']:final['y max'], final['x min']:final['x max']]
    except Exception as e:
        ##ignore because no x/y bounds were specified
        pass

    final['data'] = fitsdata
    return(final)

    
def create_parser():
    prog        = r"""parse.py"""
    usage       = r"""parse.py <filename[xmin:xmax,ymin:ymax]>"""
    description = r"""used to parse string inputs for use in other functions"""
    epilog      = "Version: " + __version__
    
    parser = argparse.ArgumentParser(prog=prog, usage=usage, description=description, epilog=epilog)
    parser.add_argument("inputstring", help="string that is being broken down into a dictionary of components")
    
    return parser
    

if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    inputstring = args.inputstring
    
    
    main(inputstring)

