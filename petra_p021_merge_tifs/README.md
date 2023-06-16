# Merging .tif files from *exsitu* total scattering

This code is written for merging subframes from total scattering 
experiments conducted on beamline P02.1, PETRA III, DESY.

During the total scattering experiment, a single exposure exposure is split into
multiple subframes, which are to be merged by this code.

Two different iPython notebooks (``.ipynb``) are available for *ex situ* and 
*operando* experiments, respectively, as different naming schemes are used for
the ``.tif`` files from the two types of x-ray total scattering experiments.
Please see the iPython notebooks for information on the naming schemes.

## Running the code
The code should be run from a directory containing the `.tif` files that are to
be merged.

Only three modules are used in the code. The ``pathlib`` module is a part of the
standard library and comes with your Python installation. In addition, the 
``numpy`` and ``scikit-image`` modules are used. For the code to function, these 
modules need to be installed if not already.

If you are using a conda distribution and you need a new environment using e.g.
Python 3.11, you can create such one:
```
conda create -n py311 -c conda-forge python=3.11 numpy scikit-image jupyterlab
```
The newly created conda environment can then be activated:
```
conda activate py311
```
Then, the code can be run through Jupyter (lab or notebook)
```
jupyter-lab
```
or
```
jupyter-notebook
```
Alternatively, the code can be run directly from the command line:
from the command line:
```
ipython petra_p021_merge_tifs_exsitu.ipynb
```
or 
```
ipython petra_p021_merge_tifs_operando.ipynb
```
Good luck and happy merging!
