# fgr_res_to_gr

This code will extract the difference curve (residual) from all .fgr files,
in a directory called 'fgr'. An .fgr file is the output file when fitting atomic
pair distribution function (PDF) data in the PDFgui software. The extracted
residual will be saved to a .gr file (without header), as if it were a PDF.

Apart from plotting the residuals on their own, possible use of the residuals
include structureMining at pdfitc.org, e.g. if the residual originates from a
single phase refinement of two-phase data. Then, the residual should contain the
structural information on the secondary phase, which the structureMining app at
pdfitc.org hopefully can provide information on.
