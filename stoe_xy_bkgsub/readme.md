# stoe_xy_bkgsub
## Background-subtraction for STOE STADI P *operando* PXRD data

The STOE STADI P diffractometer at the Department of Chemistry, Aarhus 
University  is  
equipped with an Ag x-ray source and can be used for *operando* powder x-ray 
diffraction  
(PXRD).

Compared to synchrotron x-ray data, the STOE data suffer from a lower 
signal-to-noise ratio.  
This results in difficult background-subtraction, which however is a good idea, 
when one is to  
visualize the signal of interest.

To ease the background subtraction, one can try to bin the data. This means that
intensity  
values will be summed, and the $2\theta/Q$-values will be averaged. The payoff 
is that we get better  
counting statistics for the intensities, i.e., higher signal-to-noise ratio. 
The drawback is a lower  
$2\theta/Q$-resolution by a factor of *binsize*.

**NB**: for the background-subtraction to work, please only include files 
containing actual data,  
i.e., please leave out any frames only containing background.

The code in this iPython notebook will:
- plot experimental data and background.
- bin data with a user-defined *binsize* to improve signal-to-noise ratio.
- plot the binned data and background.
- save the binned data and background to `.txt` files.
- scale the binned background to the binned data.
- plot the scaled, binned data and background.
- subtract the scaled, binned background from the binned data.
- plot the background-subtracted, binned data (both as stack and overview 
plots)
- save the background-subtracted data to a `.txt` file.
