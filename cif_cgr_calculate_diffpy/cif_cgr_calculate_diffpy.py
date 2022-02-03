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
COLORS = dict(bg_blue='#0B3C5D', bg_red='#B82601', bg_green='#1c6b0a',
              bg_lightblue='#328CC1', bg_darkblue='#062F4F', bg_yellow='#D9B310',
              bg_darkred='#984B43', bg_bordeaux='#76323F', bg_olivegreen='#626E60',
              bg_yellowgrey='#AB987A', bg_brownorange='#C09F80')
COLOR = COLORS["bg_red"]


def cif_cgr_calculator_plotter(cifs, folders):
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
        g_norm = g / max(g)
        np.savetxt(f"cgr/{cif.stem}.cgr", np.column_stack((r, g)), header=header_I,
                    fmt=['%.2f', '%.8f'])
        plt.figure(dpi=DPI, figsize=FIGSIZE)
        plt.plot(r, g, c=COLOR, lw=LINEWIDTH)
        plt.xlim(RMIN_I, RMAX_I)
        plt.xlabel(r"$r$ $[\mathrm{\AA}]$", fontsize=FONTSIZE)
        plt.ylabel(r"$G_{\mathrm{calc}}$ $[\mathrm{\AA}^{-2}]$", fontsize=FONTSIZE)
        for folder in folders:
            plt.savefig(f'{folder}/{cif.stem}.{folder}', bbox_inches='tight')
        plt.close()
        plt.figure(dpi=DPI, figsize=FIGSIZE)
        plt.plot(r, g_norm, c=COLOR, lw=LINEWIDTH)
        plt.xlim(RMIN_I, RMAX_I)
        plt.xlabel(r"$r$ $[\mathrm{\AA}]$", fontsize=FONTSIZE)
        plt.ylabel(r"$G_{\mathrm{calc}}$ $[\mathrm{\AA}^{-2}]$", fontsize=FONTSIZE)
        for folder in folders:
            plt.savefig(f'{folder}/{cif.stem}_normalized.{folder}', bbox_inches='tight')
        plt.close()
    outputstring = f"{80*'-'}\nDone calculating and plotting.\
                     \n.cgr files saved to the 'cgr' folder.\
                     \nPlots have been saved to the"
    if len(folders) == 1:
        outputstring += f" {folders[0]} directory.\n{80*'-'}"
    elif len(folders) == 2:
        outputstring += f" {folders[0]} and {folders[-1]} directories.\n{80*'-'}"
    else:
        for i in range(0, len(folders)-1):
            outputstring += f" {folders[i]},"
        outputstring += f" and {folders[-1]} directories.\n{80*'-'}"
    print(outputstring)

    return None


def main():
    print(f"{80*'-'}\
            \nPlease see the top of this .py file to review values used to calculate .cgr\
            \nfiles together with the plot settings used.")
    cif_path = Path.cwd() / "cif"
    if not cif_path.exists():
        cif_path.mkdir()
        print(f"{80*'-'}\nA folder called 'cif' has been created.\
                \nPlease place your .cif files here and rerun the code.\
                \n{80*'-'}")
        sys.exit()
    cifs = (Path.cwd() / 'cif').glob('*.cif')
    if len(list(cifs)) == 0:
        print(f"{80*'-'}\nNo .cif files found in the 'cif' folder.\
                \nPlease place your .cif here and rerun the code.\
                \n{80*'-'}")
        sys.exit()
    cifs = (Path.cwd() / 'cif').glob('*.cif')
    folders = ['png', 'pdf']
    for folder in folders:
        if not (Path.cwd() / folder).exists():
            (Path.cwd() / folder).mkdir()
    if not (Path.cwd() / 'cgr').exists():
        (Path.cwd() / 'cgr').mkdir()
    print(f"{80*'-'}\nCalculating .cgr files and plotting for...")
    cif_cgr_calculator_plotter(cifs, folders)

    return None


if __name__ == "__main__":
    main()

# End of file.
