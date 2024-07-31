PyRAF-to-ByeRAF

This project is a library of functions that replicate some of the tasks in PyRAF using only Python libraries. The purpose is to try to reduce the dependancy on PyRAF and IRAF since IRAF has been discontinued.

The scripts in the library are executable .py files which can be run either in the terminal using ipython or in any Python IDE.

Usage:
parse.py - This script is used by other functions to parse input strings. For example image.fits[1:100,1:100] will be interpreted as pixels rows 1 - 100 and pixel columns 1 - 100 of the image.fits file.

imstat.py - This script is made to imitate the imstatistics task in PyRAF. When used, the script will take the specified image or pixel region and return statistics about that region based on the set parameters.
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

  
