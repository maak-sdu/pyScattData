# diffraction_plot
This code is made for plotting diffraction data. All data files in the 'data'
folder will be plotted as the intensity as a function of 2theta in degrees, Q in
inverse Å, or Q in inverse nm. The plots will be saved to .pdf and .png files.
The x-axis format is provided by the user. The code uses loadData() from
diffpy.utils.parsers.loaddata, which can read xy- and xye-like (multi-coloumn)
data files, including headers.
