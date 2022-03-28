# scattdata_esd_normalize_bkgsub

This code is made for adding estimated standards deviations (esd), normalizing,
and subtracting background scattering data. The files are expected to have the
independent variable in the first column and the dependent variable in the
second coloumn, potentially with a header.

## Directory structure and comma-to-dot
Running the code initially, will create two subdirectories (if not already
existing):  
```
bkg  
data
```

The user is asked to put the data files in the `data` folder and the background
file in the `bkg` folder, before rerunning the code.

Rerunning the code, the user will be asked to provide the index/integer for the
part of the filename that contains the scan number, as this will be used to sort
the files during the execution of the program.

Potentially, an additional splitting is needed for the part of the filename
containing the scan number. If so, the user is prompted again in a similar way.

If the data files contain commas instead of dots, two new subdirectories will be
created:  
```
bkg_comma_to_dot  
data_comma_to_dot
```

Text files with commas instead of dots will be written to these folders. All
files will keep the filename of the corresponding parent file with commas.

## Estimating standard deviations (esds)
Next, the user will be asked to state the wavelength in Ångström, followed by
the sample-to-detector-distance (sdd) in mm. These goes into the calculation of
the estimated standards deviations (esds).

The wavelength and sdd values are saved to a `wl_sdd.txt` file in the parent
directory. If the code is re-executed, the values in the file will be read. The
program will ask the user if these values are okay. If not, the user will be
asked to prompt new values, which will overwrite the old values in the
`wl_sdd.txt` file.

Next, the user will be asked to provide the quantity and unit of the independent
variable  
```
Q in inverse Ångström  
Q in inverse nm  
2theta in degrees
```
This input is needed for the esd calculation and for axis labels in the plots.

Two new subdirectories will created:  
```
bkg_esd  
data_esd
```
In these folders, the bkg and data files containing esd will be saved, i.e.
three-column files with the independent variable in the first column, the
dependent variable in the second column, and the esd in the third column.
The file extension will be the same as for the original files.

## Normalization (scaling)
After the addition of esds, the data is ready for normalization. However, user
inputs for the x-range to obtain normalization factors within are needed. A plot
window will show, in which the user can zoom to determine an x-region to obtain
the normalization factors within.

After closing the plot window, the stack plot will be saved to the `pdf` and
`png` directories created, and the user will be asked to provide a minimum
x-range to scale within, followed by a maximum range. The user should provide a
region, where the sample signal is expected to be constant, i.e. have no varying
contribution from the sample.

After prompting the min. and max. values to obtain normalization factors within,
the plot will be saved to the `pdf` and `png` folders, and the files
containing normalized data will be written to two new directories:
```
bkg_esd_normalized   
data_esd_normalized
```
Next, a plot window will show the normalized files, including the background.
Upon closing the plot window, the stack plot will be saved to the `pdf` and
`png` folders.

## Background subtraction and overview plot
After normalization of the data, the background is to be subtracted before doing
an overview plot. Despite the background being scaled together with the data,
further scaling of the background prior to subtraction of the data occurs to
ensure that no negative intensities occur for the background subtracted data.

The program finds the largest factor (<=1), for which no negative intensities
will occur for any of the data files. This scale factor is used for the
background subtraction for all the data files.

A plot window will appear and show the resulting background subtracted data
files in a stack plot. Upon closure, the stack plot will be saved to the `pdf`
and `png` folders.

Finally, a plot window showing an overview plot will appear. The scan number
will appear on the x-axis, and the independent variable on the y-axis, and the
intensity given by a contour, which can be interpreted from the color bar to the
right. After closing the plot window, the plot is saved to the `pdf` and `png`
folders.

At this point, the execution of the program is done, and the data should be
ready for your analysis. Good luck!
