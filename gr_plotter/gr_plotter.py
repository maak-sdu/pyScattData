import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from pathlib import Path
from diffpy.utils.parsers.loaddata import loadData

DPI = 300
FIGSIZE = (12,4)
FONTSIZE = 20

# Billinge group colors
bg_blue = '#0B3C5D'
bg_red = '#B82601'
bg_green = '#1c6b0a'
bg_lightblue = '#328CC1'
bg_darkblue = '#062F4F'
bg_yellow = '#D9B310'
bg_darkred = '#984B43'
bg_bordeaux = '#76323F'
bg_olivegreen = '#626E60'
bg_yellowgrey = '#AB987A'
bg_brownorange = '#C09F80'

COLOR = bg_blue

def gr_plotter():
    if not (Path.cwd() / 'gr').exists():
        print(f"{90*'-'}\nPlease create a folder called 'gr' and place your .gr files there.\
                \n{90*'-'}")
        sys.exit()
    files = list((Path.cwd() / 'gr').glob('*.gr'))
    if len(files) == 0:
        print(f"{90*'-'}\nPlease place your .gr files in the 'gr' folder.\
                \n{90*'-'}")
        sys.exit()
    file_exts = []
    for e in files:
        if e.suffix not in file_exts:
            file_exts.append(e.suffix)
    if len(file_exts) > 1:
        print(f"{90*'-'}\nPlease only include .gr files in the 'gr' folder.\
                \n{90*'-'}")
        sys.exit()
    print(f"{90*'-'}\nPlotting .gr files...")
    folders = ['png', 'pdf']
    for e in folders:
        if not (Path.cwd() / e).exists():
            (Path.cwd() / e).mkdir()
    for e in files:
        data = loadData(e)
        r, g = data[:,0], data[:,1]
        plt.figure(dpi=DPI, figsize=FIGSIZE)
        plt.plot(r, g, c=COLOR, label='$G_{\mathrm{exp}}$')
        plt.legend()
        # plt.plot(r, g, c=COLOR, marker='o', mfc='none', ls='none', ms=3, mew=0.3,
        #          label='$G_{\mathrm{exp}}$')
        # blue_marker = plt.scatter([], [], marker='o', fc='none', ec=bg_blue)
        # blue_marker.remove()
        # legend = plt.legend(handles=[(blue_marker)], labels=['$G_{\mathrm{exp}}$'])
        plt.xlabel(r"$r$ $[\mathrm{\AA}]$", fontsize=FONTSIZE)
        plt.ylabel(r"$G$ $[\mathrm{\AA}^{-2}]$", fontsize=FONTSIZE)
        plt.xlim(np.amin(r), np.amax(r))
        plt.savefig(f"png/{e.stem}.png", bbox_inches='tight')
        plt.savefig(f"pdf/{e.stem}.pdf", bbox_inches='tight')
        plt.close()
    print(f"Done .gr files.\nPlots have been saved to the png and pdf folders.\
            \n{90*'-'}")

    return None

def main():
    gr_plotter()

    return None


if __name__ == "__main__":
    main()

# End of file.
