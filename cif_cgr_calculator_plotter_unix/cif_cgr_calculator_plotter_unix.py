import sys
from pathlib import Path
from diffpy.srreal.pdfcalculator import PDFCalculator
from diffpy.structure import loadStructure
import matplotlib.pyplot as plt
import numpy as np

QMIN_I = 0.1
QMAX_I = 24.0
QBROAD_I = 0.0
QDAMP_I = 0.0325

RMIN_I = 1.0
RMAX_I = 10.0
RSTEP_I = 0.01

UISO_I = 0.005

DPI = 300
FIGSIZE = (12,4)
FONTSIZE = 20
LINEWIDTH = 1
COLOR = 'red'

if not (Path.cwd() / 'cif').exists():
    print(f"{90*'-'}\nPlease create a folder called 'cif' and place your .cif files here.\
            \n{90*'-'}")
    sys.exit()
cifs = (Path.cwd() / 'cif').glob('*.cif')
if len(list(cifs)) == 0:
    print(f"{90*'-'}\nPlease place your .cif files in the cif folder.\
            \n{90*'-'}")
    sys.exit()
cifs = (Path.cwd() / 'cif').glob('*.cif')
folders = ['png', 'pdf']
for folder in folders:
    if not (Path.cwd() / folder).exists():
        (Path.cwd() / folder).mkdir()
if not (Path.cwd() / 'cgr').exists():
    (Path.cwd() / 'cgr').mkdir()
print(f"{90*'-'}\nCalculating and plotting for...")
for cif in cifs:
    print(f"\t{cif.name}")
    header_I = f"cgr file calculated from {cif.name} with the following parameters:\
               \nqmin = {QMIN_I}\nqmax = {QMAX_I}\nqdamp = {QDAMP_I}\
               \nqbroad = {QBROAD_I}\nrmin = {RMIN_I}\nrmax = {RMAX_I}\
               \nrstep = {RSTEP_I}\nuiso = {UISO_I}\nL r($\AA$)  G($\AA^{-2}$)"
    stru = loadStructure(f"{cif.parent.name}/{cif.name}")
    stru.Uisoequiv = UISO_I
    pdfcalc = PDFCalculator()
    r, g = pdfcalc(stru,
                   qmin=QMIN_I, qmax=QMAX_I, qbroad=QBROAD_I, qdamp=QDAMP_I,
                   rmin = RMIN_I, rmax=RMAX_I+RSTEP_I, rstep=RSTEP_I)
    np.savetxt(f"cgr/{cif.stem}.cgr", np.column_stack((r, g)), header=header_I,
                fmt=['%.2f', '%.8f'])
    plt.figure(dpi=DPI, figsize=FIGSIZE)
    plt.plot(r, g, c=COLOR, lw=LINEWIDTH)
    plt.xlim(RMIN_I, RMAX_I)
    plt.xlabel(r"$r$" "$[\mathrm{\AA}]$", fontsize=FONTSIZE)
    plt.ylabel(r"$G_{\mathrm{calc}}$" "$[\mathrm{\AA}^{-2}]$", fontsize=FONTSIZE)
    plt.text(2.16, 17, r'$\downarrow$', c='tab:blue', fontsize=FONTSIZE*2)
    plt.text(3.19, 3.95, r'$\downarrow$', c='tab:orange', fontsize=FONTSIZE*2)
    plt.text(3.98, 17.25, r'$\downarrow$', c='tab:green', fontsize=FONTSIZE*2)
    plt.text(4.66, 5.5, r'$\downarrow$', c='tab:purple', fontsize=FONTSIZE*2)
    plt.text(5.24, 11.5, r'$\downarrow$', c='tab:blue', fontsize=FONTSIZE*2)
    plt.text(5.775, 0, r'$\downarrow$', c='tab:cyan', fontsize=FONTSIZE*2)
    for folder in folders:
        plt.savefig(f'{folder}/{cif.stem}.{folder}', bbox_inches='tight')
print(f"{90*'-'}")
# End of file.
