# pdfgui_fit_plot

This code will plot the fit of pair distribution function (PDF) data from a
refinement using the PDFgui software. The experimental data is expected to
appear in a .gr file, the fitted data including difference curve in a .fgr file,
and the weighted residual value, Rw, in a .res file.

The code will make a plot for all files in the 'fgr', 'gr', and 'res' folders.
Therefore, please be aware to name file probably, e.g. using the same file name
apart from the file extension:

> filename.fgr

> filename.gr

> filename.res

Alternatively, consider to prefix enumerate files that should be plotted
together:

> 00_fgr_file.fgr

> 00_gr_file.gr

> 00_res_file.res
