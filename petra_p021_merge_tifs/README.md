# petra_p021_merge_tifs

This code is written for merging .tif files from beamtimes at beamline P02.1,
PETRA III, DESY, Hamburg, Germany. The reason for is that during an x-ray total
scattering experiment for pair distribution function analysis a 'scan' may
consist of multiple subframes (.tif files), 60 s each, which will have to be
merged/summed/stacked. This code is capable of doing the job.

Expected syntax:    basename_cyclenumber-sequentialnumber.tif

Example:            N1_PDF_CeO2_0-00003.tif
  basename:         N1_PDF_CeO2
  cyclennumber:     0
  sequentialnumber: 00003

The files are sorted into a nested dictionary in Python. First, they will be
sorted according to the 'basename'. Then, they will be sorted according to the
'cycle number', such that all subframes of a cycle number will be merged.

When running the code, the user will be asked to provide the absolute path to
the input files, i.e. the absolute path to the directory containing all the
input (.tif) files. The user can just copy and paste the absolute file path from
the file explorer, if wished.

Likewise, the user is also asked to provide the absolute path for the output
files. In the provided output directory, a folder called 'tif_sum' will be
created. In the 'tif_sum' folder, subdirectories for all basenames
(i.e. samples) will be created. The merged .tif files will be saved to these
folders.

**_Ex-situ_ PDF data for multiple cycles**
Regarding merging of _ex-situ_ PDF data, where multiple cycles are to be merged,
two possible workarounds are suggested:

**Workaround 1**
Make a new folder and copy all input files to this folder. Then, rename all
files of a particular basename to have the same cycle number (e.g. 0). The
merged .tif file will then have the first and last sequential number in the
name.

Before renaming:
N1_PDF_Kapton_0-01186.tif  
N1_PDF_Kapton_0-01187.tif  
N1_PDF_Kapton_0-01188.tif  
N1_PDF_Kapton_0-01189.tif  
N1_PDF_Kapton_1-01218.tif  
N1_PDF_Kapton_1-01219.tif  
N1_PDF_Kapton_1-01220.tif  
N1_PDF_Kapton_1-01221.tif  

After renaming:

N1_PDF_Kapton_0-01186.tif  
N1_PDF_Kapton_0-01187.tif  
N1_PDF_Kapton_0-01188.tif  
N1_PDF_Kapton_0-01189.tif  
N1_PDF_Kapton_0-01218.tif  
N1_PDF_Kapton_0-01219.tif  
N1_PDF_Kapton_0-01220.tif  
N1_PDF_Kapton_0-01221.tif  

After merging, consider to rename such that the file is not misleading regarding
the sequential numbers that were actually merged:

N1_PDF_Kapton_0_01186-01189_01218-01221.tif

Alternatively:

N1_PDF_Kapton_0.tif

**Workaround 2**
Initial execution of the code will merge all scans of a given subframe. Make a
new folder and copy the merged .tif files to this new (input) folder. Rename all
the .tif files, such that they have the same cycle number (e.g. 0), and replace
the underscore between the cycle and sequential numbers with a dash
(i.e. cycle_seq -> cycle-seq).

Before renaming:

N1_PDF_Kapton_0_01186-01189.tif  
N1_PDF_Kapton_1_01218-01221.tif  

After renaming:

N1_PDF_Kapton_0-01186-01189.tif  
N1_PDF_Kapton_0-01218-01221.tif  

After merging, consider to rename such that the file is not misleading regarding
the sequential numbers that were actually merged:

N1_PDF_Kapton_0_01186-01189_01218-01221.tif

Alternatively:

N1_PDF_Kapton_0.tif
