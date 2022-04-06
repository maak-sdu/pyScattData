# xy_overview
This code can be used to generate one or more overview plots for xy data.
The data files are expected to be alpha numerically ordered such that they are
read by the program in the right order. The order in which data files are read
can be seen from the terminal print.

## Flow of the program

### Directory structure
First time, the code is run, it will look for a directory called 'data'. If this
does not exists, a folder called 'data' will be created and the user will be
asked to put the data files there and rerun the code.

If the 'data' folder already exists but is empty, the user will be told this,
to add data files, and rerun the code.

If multiple file extensions are found in the 'data' folder, the user is told to
review the files in the data folder and rerun the code.

### Naming files to have them read in the right order
If data files have been properly placed in the data directory, the code will
stack the files in an array that will be ready for plotting. The filenames are
printed to the terminal in the order that they are read by the program. Hence,
the user can confirm that files are read in the right order. If not, please name
the data files alpha numerically such that will be read in the read order.

### User inputs
The user will be prompted for colormap (cmap) and data type (xytype). These does
not affect the execution of the program, but solely the appearance of the plots.
The values will be saved to a 'user_inputs.txt' file. If

### Plot of all data
Initially, an overview plot using x and y limits read from the data values, and
the whole data range is plotted. Plots are saved to the created 'pdf', 'png',
and 'svg' folders.

### Plot(s) with customary limits
Thereafter, the user will be asked for whether a plot with customary limits is
desired. If so, the user will be prompted for minimum and maximum x- and
y-values. The x-limits shape the matrix that is plotted, and the y-limits set
the color scale of the color bar. Again, plots are saved to the output folders.

Again, the user is asked whether an additional customary plot is desired. This
continues until the point where this is not the case and the program ends.
