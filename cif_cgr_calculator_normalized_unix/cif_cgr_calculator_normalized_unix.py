from diffpy.srreal.pdfcalculator import PDFCalculator
from diffpy.structure import loadStructure
from diffpy.structure.parsers.p_cif import _fixIfWindowsPath
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

QMIN_I = 0.1
QMAX_I = 24.0
QBROAD_I = 0.0
QDAMP_I = 0.0325

RMIN_I = 1.0
RMAX_I = 10.0
RSTEP_I = 0.01

UISO_I = 0.005

COLORS = ['#0B3C5D', '#B82601', '#1c6b0a', '#328CC1', '#062F4F',
              '#D9B310', '#984B43', '#76323F', '#626E60', '#AB987A',
              '#C09F80']
# COLORS = [blue, red, green, lightblue, darkblue,
#               yellow, darkred, bordeaux, olivegreen, yellowgreen,
#               brownorange]

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
    header_I = f"Scaled cgr file calculated from {cif.name} with the following parameters:\
               \nqmin = {QMIN_I}\nqmax = {QMAX_I}\nqdamp = {QDAMP_I}\
               \nqbroad = {QBROAD_I}\nrmin = {RMIN_I}\nrmax = {RMAX_I}\
               \nrstep = {RSTEP_I}\nuiso = {UISO_I}\nL r($\AA$)  G($\AA^{-2}$)"
    stru = loadStructure(f"{cif.parent.name}/{cif.name}")
    stru.Uisoequiv = UISO_I
    pdfcalc = PDFCalculator()
    r, g = pdfcalc(stru,
                   qmin=QMIN_I, qmax=QMAX_I, qbroad=QBROAD_I, qdamp=QDAMP_I,
                   rmin = RMIN_I, rmax=RMAX_I, rstep=RSTEP_I)
    gmax = np.amax(g)
    gscaled = (1 / gmax) * g
    plt.plot(r, gscaled, c='r')
    plt.xlim(RMIN_I, RMAX_I)
    plt.xlabel(r"$r$" "$[\mathrm{\AA}]$")
    plt.ylabel(r"$G_{\mathrm{calc}}$" "$[\mathrm{\AA}^{-2}]$")
    for folder in folders:
        plt.savefig(f'{folder}/{cif.stem}.{folder}', bbox_inches='tight')
print(f"\nPlots have been saved to the pdf and png folders.\
        \nNormalized PDFs have been saved to .cgr files in the cgr folder.\n{90*'-'}")

# End of file.
