import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from pathlib import Path
from diffpy.utils.parsers.loaddata import loadData

DPI = 300
FIGSIZE = (12,4)
FONTSIZE_LABELS = 20
FONTSIZE_TICKS = 14
LINEWIDTH = 1
XLABEL = r"$r$ $[\mathrm{\AA}]$"
YLABEL = r"$G$ $[\mathrm{\AA}^{-2}]$"

# Billinge group colors
COLORS = dict(bg_blue='#0B3C5D', bg_red='#B82601', bg_green='#1c6b0a',
              bg_lightblue='#328CC1', bg_darkblue='#062F4F', bg_yellow='#D9B310',
              bg_darkred='#984B43', bg_bordeaux='#76323F', bg_olivegreen='#626E60',
              bg_yellowgrey='#AB987A', bg_brownorange='#C09F80')
COLOR = COLORS["bg_blue"]


def gr_plotter(gr_files):
    for e in gr_files:
        print(f"\t{e.name}")
        data = loadData(e)
        r, g = data[:,0], data[:,1]
        plt.figure(dpi=DPI, figsize=FIGSIZE)
        plt.plot(r, g, c=COLOR, lw=LINEWIDTH, label='$G_{\mathrm{exp}}$')
        # plt.scatter(r, g, lw=0.5, s=10, facecolor='none', edgecolor=COLOR, label='$G_{\mathrm{exp}}$')
        # plt.legend()
        # plt.plot(r, g, c=COLOR, marker='o', mfc='none', ls='none', ms=3, mew=0.3,
        #          label='$G_{\mathrm{exp}}$')
        # blue_marker = plt.scatter([], [], marker='o', fc='none', ec=bg_blue)
        # blue_marker.remove()
        # legend = plt.legend(handles=[(blue_marker)], labels=['$G_{\mathrm{exp}}$'])
        plt.xlabel(XLABEL, fontsize=FONTSIZE_LABELS)
        plt.ylabel(YLABEL, fontsize=FONTSIZE_LABELS)
        plt.xlim(np.amin(r), np.amax(r))
        plt.xticks(fontsize=FONTSIZE_TICKS)
        plt.yticks(fontsize=FONTSIZE_TICKS)
        plt.savefig(f"png/{e.stem}.png", bbox_inches='tight')
        plt.savefig(f"pdf/{e.stem}.pdf", bbox_inches='tight')
        plt.close()

    return None


def main():
    gr_path = Path.cwd() / 'gr'
    if not gr_path.exists():
        gr_path.mkdir()
        print(f"{80*'-'}\nA folder called 'gr' has been created.\
                \nPlease place your .gr files there and rerun the code.\
                \n{80*'-'}")
        sys.exit()
    gr_files = list((Path.cwd() / 'gr').glob('*.gr'))
    if len(gr_files) == 0:
        print(f"{80*'-'}\nNo .gr files found in the 'gr' folder.\
                \nPlease place your .gr files in the 'gr' folder and rerun the code.\
                \n{80*'-'}")
        sys.exit()
    folders = ['png', 'pdf']
    for e in folders:
        if not (Path.cwd() / e).exists():
            (Path.cwd() / e).mkdir()
    print(f"{80*'-'}\nPlotting .gr files...")
    gr_plotter(gr_files)
    print(f"{80*'-'}\nDone plotting .gr files.\
            \nPlots have been saved to the png and pdf folders.\
            \n{80*'-'}")

    return None


if __name__ == "__main__":
    main()

# End of file.
