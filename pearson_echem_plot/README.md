# pearson_echem_plot
This code will conduct Pearson correlation analysis for a series of data files,
e.g. files containing scattering data like .gr files containing pair
distribution function (PDF) data.

In addition, the code will also plot electrochemical data from a .txt file,
which should only contain two columns with time and voltage, respectively.
All data files should be placed in a subdirectory called 'data'.

Plots of the correlation matrix, the electrochemistry, and a combined plot will
be saved to the 'pdf' and 'png' folders created. The Pearson correlation matrix
will also be saved to the 'txt' folder created.
