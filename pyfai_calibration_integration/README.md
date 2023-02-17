# pyFAI notebook

## Setup an installation
Create a dedicated `conda` environment called `pyfai_env` and install
`Python3.9`, `pyFAI`, and `JupyterLab` from the `conda-forge` channel.
```
conda create -n pyfai_env -c conda-forge python=3.9 pyfai jupyterlab
```
Activate the `pyfai_env` conda environment.
```
conda activate pyfai_env
```
Navigate to the topmost level on your drive, from which you will access files.
```
cd path/to/topmost/level/needed
```
Initialize a `jupyter` session using `JupyterLab` or `Jupyter Notebook`.
```
jupyter-lab
```
or
```
jupyter-notebook
```
If you have Visual Studio Code (VSCode) set up with `Python` and `Jupyter`
extensions, you can also run the `.ipynb` files from VSCode.
```
code
```
When you have opened the `.ipynb` file, make sure that you are running the
kernel using your `pyfai_env` conda environment.

## pyFAI: Fast Azimuthal Integration using Python
PyFAI is a python libary for azimuthal integration of X-ray/neutron/electron
scattering data acquired with area detectors. For this, images needs to be
re-binned in polar coordinate systems. Additional tools are provided to
calibrate the experimental setup, i.e. define where the detector is positioned
in space considering the sample and the incident beam.

When running this notebook, the calibration gui (graphical user interface),
`pyFAI-calib2` will run. Subsequently, the azimuthal integration gui,
`pyFAI-integrate` will run. Finally, integrated files will be plotted.

For pyFAI documentation, please see
https://pyfai.readthedocs.io/en/master/index.html.

Various cookbook recipes and tutorials can be found at
https://pyfai.readthedocs.io/en/master/usage/index.html.
