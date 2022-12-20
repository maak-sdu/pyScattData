# pyScattData
Processing, analysis, and plotting of scattering data.

If you encounter any bugs or have suggestions for new code or functionalities,
please post an issue here on GitHub. If you refer to a specific script, please
include that in the title of the issue.

Go explore the Bragg peaks and whatever might be hidden underneath them!

## Setup and installation
The following guidelines assume that the user runs a conda distribution, i.e.,
Anaconda or Miniconda. If these guidelines are followed, all dependencies for
the `pyScattData` code will be installed.

### Create a new `pyscattdata` conda environment
- It is highly recommended to run the code in a conda environment dedicated to
  the pyScattData library. If the user does not already have that, such a conda
  environment, called `pyscattdata` and using the latest Python 3 version, can
  be created from:
  ```shell
  conda create -n pyscattdata python=3
  ```

### Activate `pyscattdata` conda environment
- When the user has a `pyscattdata` conda environment, the user should activate
  the pyscattdata conda environment:
  ```shell
  conda activate pyscattdata
  ```

### Install dependencies
- Navigate to the main `pyScattData` directory. Using conda, dependencies
  present in the `run.txt` file in the `requirements` directory will be
  installed from the `conda-forge` channel, when running (NB: this might take
  some time - consider to go for a coffee...):
  ```shell
  conda install -c conda-forge --file requirements/run.txt
  ```
- Using pip, additional dependencies present in the `pip_requirements.txt` file
  in the `requirements` directory will be installed, when running:
  ```shell
  pip install -r requirements/pip_requirements.txt
  ```
- If running on a Unix-based OS (MacOS or Linux), additional dependencies
  present in the `diffpy_extras.txt` file in the `requirements` directory will
  be installed, when running:
  ```shell
  pip install -r requirements/diffpy_extras.txt
  ```
  Unfortunately, these diffpy packages are not available for Windows users.

Now, all `pyScattData` dependencies are installed for the `pyscattdata` conda
environment. You are now ready to run the code present in the `pyScattData`
repository.
