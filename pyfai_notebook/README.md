# pyFAI notebook

## Setup an installation
Create dedicated `conda` environment called `pyfai_env` and install `Python3.9`,
`pyFai`, and `jupyterlab` from the `conda-forge` channel.
```
conda create -n pyfai_env -c conda-forge python=3.9 pyfai jupyterlab
```
Activate `pyfai_env` conda environment.
```
conda activate pyfai_env
```
Navigate to the topmost on your drive from where you will access files.
```
cd path/to/topmost/level/needed
```
Initialize a `jupyter` session using `jupyter-lab` or `jupyter-notebook`.
```
jupyter-lab
```
or
```
jupyter-notebook
```
If you Visual Studio Code (VSCode) set up with `Python` and `Jupyter`  
extensions, you can also run the `.ipynb` files from VSCode.
```
code
```
When you have opened the `.ipynb` file, make sure that you are running the
kernel using your `pyfai_env` conda environment.
