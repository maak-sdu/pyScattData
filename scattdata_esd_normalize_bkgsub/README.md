# scattdata_esd_normalize_bkgsub

This code is made for adding estimate standards deviations (esd), normalization,
and background subtracting scattering data. The files are expected to have the
independent variable in the first column and the dependent variable in the
second coloumn, potentially with a header.

## Directory structure and user inputs
Running the code initially, will create two subdirectories (if not already
existing):  
bkg  
data

The user is asked to put the data files in the 'data' folder and the background
file in the bkg folder, before rerunning the code.

Rerunning the code, the user will be asked to provide the index/integer for the
part of the filename that contains the scan number, as this will be used to sort
files during the execution of the program.

Potentially, an additional splitting is needed for the part of the filename
containing the scan number. If so, the user is prompted again in a similar way.

If the data files contain commas instead of dots, two new subdirectories will be
created:  
bkg_comma_to_dot  
data_comma_to_dot

Text files with commas instead of dots will be written to these folders. All
files will keep the filename of the corresponding parent file with commas.

Next, the user will be asked to state the wavelength in Ångström, followed by
the sample-to-detector-distance (sdd) in mm. These goes into the calculation of
the estimated standards deviations (esd).

The wavelength and sdd values are save to a wl_sdd.txt file in the parent
directory. If the code is re-executed, the values in the file will be read. The
program will ask the user if these values are okay. If not, the user will be
asked to prompt new values, which will be saved to the wl_sdd.txt file replacing
the old ones.

Next, the user will be asked to provide the quantity and unit of the independent
variable  
Q in inverse Ångström.  
Q in inverse nm.  
2theta in degrees.  

This input is needed for the esd calculation and for axis labels in the plots.

Two new subdirectories will created:  
bkg_esd  
data_esd

In these folders, the bkg and data files containing esd will be saved. The file
extension will be the same as for the original files.

To be continued...
