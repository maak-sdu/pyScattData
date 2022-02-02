import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import codecs

DPI = 300
FIGSIZE = (12,4)
FONTSIZE_LABELS = 16
LINEWIDTH = 1

TICKINDEX_MAJOR_X = 10
TICKINDEX_MINOR_X = TICKINDEX_MAJOR_X / 5
# TICKINDEX_MAJOR_Y = 1
# TICKINDEX_MINOR_Y = TICKINDEX_MAJOR_Y / 5

COLORS = dict(bg_blue='#0B3C5D', bg_red='#B82601', bg_green='#1c6b0a',
              bg_lightblue='#328CC1', bg_darkblue='#062F4F', bg_yellow='#D9B310',
              bg_darkred='#984B43', bg_bordeaux='#76323F', bg_olivegreen='#626E60',
              bg_yellowgrey='#AB987A', bg_brownorange='#C09F80')
COLOR = COLORS["bg_blue"]


def ras_to_csv_converter_plotter(ras_files):
    for e in ras_files:
        filename = e.stem
        print(f"\t{filename}")
        tt, int_exp = [], []
        with codecs.open(e, 'r', 'charmap') as f:
            lines = f.readlines()
        for i in range(0, len(lines)):
            if '*RAS_INT_START' in lines[i]:
                start = i + 1
            elif '*RAS_INT_END' in lines[i]:
                end = i
        for i in range(start, end):
            tt.append(float(lines[i].split()[0]))
            int_exp.append(float(lines[i].split()[1]))
        tt, int_exp = np.array(tt), np.array(int_exp)
        tt_int_exp = np.column_stack((tt, int_exp))
        np.savetxt(f"csv/{filename}.csv", tt_int_exp, delimiter=",", fmt="%.3f")
        fig, ax = plt.subplots(dpi=DPI, figsize=FIGSIZE)
        plt.plot(tt, int_exp, c=COLOR, lw=LINEWIDTH)
        plt.xlim(np.amin(tt), np.amax(tt))
        plt.xlabel(r"$2\theta$ $[\degree]$", fontsize=FONTSIZE_LABELS)
        plt.ylabel(r"$I$ $[\mathrm{counts}]$", fontsize=FONTSIZE_LABELS)
        ax.xaxis.set_major_locator(ticker.MultipleLocator(TICKINDEX_MAJOR_X))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(TICKINDEX_MINOR_X))
        # ax.yaxis.set_major_locator(ticker.MultipleLocator(TICKINDEX_MAJOR_Y))
        # ax.yaxis.set_minor_locator(ticker.MultipleLocator(TICKINDEX_MINOR_Y))
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        plt.savefig(f"png/{filename}.png", bbox_inches='tight')
        plt.savefig(f"pdf/{filename}.pdf", bbox_inches='tight')
        plt.close()

    return None

def main():
    ras_path = Path.cwd() / 'ras'
    if not ras_path.exists():
        ras_path.mkdir()
        print(f"{80*'-'}\nA folder called 'ras' has been created.\nPlease "
              f"place your files there and rerun the code.\n{80*'-'}")
        sys.exit()
    ras_files = list((Path.cwd() / 'ras').glob("*.ras"))
    if len(ras_files) == 0:
        print(f"{80*'-'}\nNo .ras files were found in the 'ras' folder.\n"
              f"Please place your files in the 'ras' folder and rerun the code."
              f"\n{80*'-'}")
        sys.exit()
    folders = ['csv', 'png', 'pdf']
    for folder in folders:
        if not (Path.cwd() / folder).exists():
            (Path.cwd() / folder).mkdir()
    print()
    print(f"{80*'-'}\nPlease see the top of this .py file for plot settings.\n"
          f"{80*'-'}\nConverting .ras files to .csv files and plotting...")
    ras_to_csv_converter_plotter(ras_files)
    print(f"\n{80*'-'}\nThe .ras files have been converted to .csv files saved "
          f"to the csv folder.\nPlots have been saved to the png and pdf "
          f"folders.\n{80*'-'}")

    return None


if __name__ == "__main__":
    main()

# End of file.
