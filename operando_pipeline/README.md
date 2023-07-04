# *Operando* pipeline
The iPython Notebook (.ipynb) available here offers a pipeline for processing
*operando* (and *in situ*) synchrotron x-ray scattering data.

The pipeline includes:
- Calibration and creation of a 'static mask' (beamstop, beamstop arm, dead 
  pixels).
- Azimuthal integration of calibrant and background.
- Automasking of data files ('dynamic mask').
- Azimuthal integration of data files using 'static' and 'dynamic' masks.
- Plotting of azimuthally integrated background and data files together.
- Estimation of uncertainties for calibrant, background, and data files.
- Normalization/scaling of data files and background to account for synchrotron 
  x-ray intensity fluctuations.
- Plotting of normalized azimuthally integrated background and data files 
  together.
- Overview plot of normalized azimuthally integrated data files.
- Determination of maximum value of background scale factor to result in no 
  negative intensities for background-subtracted files.
- Background-subtraction for data files.
- Plotting background-subtracted data files together.
- Overview plot of background-subtracted data files.

## Setup and installation
Create a Python 3.9 Conda environment:
```
conda create -n py39 -c conda-forge python=3.9
```
Activate the py39 Conda environment:
```
conda activate py39
```
Install the required packages found in the requirements.txt file:
```
conda install -n py39 -c conda-forge --file requirements.txt
```
Launch iPython notebook using Jupyter:
```
jupyter-lab
```
or
```
jupyter-notebook
```
Happy data processing!
