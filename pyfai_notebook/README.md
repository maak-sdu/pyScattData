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
