import sys
from pathlib import Path
from diffpy.utils.parsers.loaddata import loadData
import matplotlib.pyplot as plt
import numpy as np


DPI = 300
FIGSIZE = (12,4)
FONTSIZE_LABELS = 20
FONTSIZE_TICKS = 14
LINEWIDTH = 1

COLORS = dict(bg_blue='#0B3C5D', bg_red='#B82601', bg_green='#1c6b0a',
              bg_lightblue='#328CC1', bg_darkblue='#062F4F', bg_yellow='#D9B310',
              bg_darkred='#984B43', bg_bordeaux='#76323F', bg_olivegreen='#626E60',
              bg_yellowgrey='#AB987A', bg_brownorange='#C09F80')
COLOR = COLORS["bg_blue"]


def diffraction_plot(data_files, x_type):
    for file in data_files:
        print(f"\t{file.name}")
        data = loadData(file)
        x, y = data[:,0], data[:,1]
        plt.figure(dpi=DPI, figsize=FIGSIZE)
        plt.plot(x, y, lw=LINEWIDTH, c=COLOR)
        plt.xlim(np.amin(x), np.amax(x))
        if x_type == 0:
            x_label = r"$2\theta$ $[\degree]$"
        elif x_type == 1:
            x_label = r"$Q$ $[\mathrm{\AA}^{-1}]$"
        elif x_type == 2:
            x_label = r"$Q$ $[\mathrm{nm}^{-1}]$"
        plt.xlabel(x_label, fontsize=FONTSIZE_LABELS)
        plt.ylabel(r"$I$ $[\mathrm{arb. u.}]$", fontsize=FONTSIZE_LABELS)
        plt.xticks(fontsize=FONTSIZE_TICKS)
        plt.yticks(fontsize=FONTSIZE_TICKS)
        plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
        plt.savefig(f"png/{file.stem}.png", bbox_inches="tight")
        plt.savefig(f"pdf/{file.stem}.pdf", bbox_inches="tight")
        plt.close()

    return None


def main():
    data_path = Path.cwd() / "data"
    if not data_path.exists():
        data_path.mkdir()
        print(f"{80*'-'}\nA folder called 'data' has been collected.\nPlease "
              f"place your data files there and rerun the code.\n{80*'-'}")
        sys.exit()
    data_files = list(data_path.glob("*.*"))
    if len(data_files) == 0:
        print(f"{80*'-'}\nNo data files found in the 'data' folder.\nPlease "
              f"place your data files there and rerun the code.\n{80*'-'}")
        sys.exit()
    plotfolders = ["pdf", "png"]
    for folder in plotfolders:
        if not (Path.cwd() / folder).exists():
            (Path.cwd() / folder).mkdir()
    print(f"{80*'-'}\nPlease see the top of this .py file for plot settings.\n"
          f"{80*'-'}\nQuantity on the x-axis...\n\t0\t2theta in degrees\n\t1\t"
          f"Q in inverse Å\n\t2\tQ in inverse nm")
    x_type = int(input("Please state the quantity on the x-axis: "))
    print(f"{80*'-'}\nPlotting files...")
    diffraction_plot(data_files, x_type)
    print(f"\nDone plotting data files.\nThe plots have been saved to the "
          f"'pdf' and 'png' folders.\n{80*'-'}")

    return None


if __name__ == "__main__":
    main()

# End of file.
