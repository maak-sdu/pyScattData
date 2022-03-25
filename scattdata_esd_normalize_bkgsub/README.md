# scattdata_esd_normalize_bkgsub

This code is made for adding estimate standards deviations (esd), normlizing,
and background subtracting scattering data. The files are expected to have the
independent variable in the first column and the dependent variable in the
second coloumn.

## Directory structure and user inputs
Running the code initially, will create two subdirectories (if not already
existing):  
bkg  
data

The user is asked to put the data files in the 'data' folder and the background
file in the bkg folder, before rerunning the code.

Rerunning the code, the user will be asked to provide the sample-to-detector-
distance (sdd) in millimeters. This goes into the calculation of the estimated
standard deviations (esd).

Two new subdirectories will created:  
bkg_esd  
data_esd

In these folders, the bkg and data files containing esd will be saved. The file
extension will be the same as the original 
