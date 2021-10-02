import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

DPI = 300
FIGSIZE = (12,4)
FONTSIZE = 16

# Billinge group colors
bg_blue, bg_red, bg_green = '#0B3C5D', '#B82601', '#1c6b0a'
bg_lightblue, bg_darkblue, bg_yellow = '#328CC1', '#062F4F', '#D9B310'
bg_darkred, bg_bordeaux, bg_olivegreen = '#984B43', '#76323F', '#626E60'
bg_yellowgrey, bg_brownorange = '#AB987A', '#C09F80'

COLOR = bg_blue

def asc_to_csv_converter_plotter():
    if not (Path.cwd() / 'asc').exists():
        print(f"{90*'-'}\nPlease make a folder called 'asc' and place your files there.\
                \n{90*'-'}")
    files = list((Path.cwd() / 'asc').glob("*.asc"))
    if len(files) == 0:
        print(f"{90*'-'}\nPlease place your files in the 'asc' folder.\
                \n{90*'-'}")
    print(f"{90*'-'}\nConverting asc files to csv files and plotting...")
    folders = ['csv', 'png', 'pdf']
    for folder in folders:
        if not (Path.cwd() / folder).exists():
            (Path.cwd() / folder).mkdir()
    for e in files:
        filename = e.stem
        with open(e) as f:
            lines = f.readlines()
        for i in range(len(lines)):
            if "*START" in lines[i]:
                start_tt = float(lines[i].split()[-1])
            elif "*STOP" in lines[i]:
                stop_tt = float(lines[i].split()[-1])
            elif "*STEP" in lines[i]:
                step_tt = float(lines[i].split()[-1])
            elif "*COUNT" in lines[i]:
                start_int = i+1
            elif "*END" in lines[i]:
                end_int = i
        tt = np.arange(start_tt, stop_tt+step_tt, step_tt)
        int_exp = []
        for i in range(start_int, end_int):
            for j in range(len(lines[i].split(","))):
                int_exp.append(float(lines[i].split(",")[j]))
        int_exp = np.array(int_exp)
        tt_int_exp = np.column_stack((tt, int_exp))
        np.savetxt(f"csv/{filename}.csv", tt_int_exp, delimiter=",", fmt="%.3f")
        plt.figure(dpi=DPI, figsize=FIGSIZE)
        plt.plot(tt, int_exp, c=COLOR)
        plt.xlim(np.amin(tt), np.amax(tt))
        plt.xlabel(r"$2\theta$ $[\degree]$", fontsize=FONTSIZE)
        plt.ylabel(r"$I$ $[\mathrm{counts}]$", fontsize=FONTSIZE)
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        plt.savefig(f"png/{filename}.png", bbox_inches='tight')
        plt.savefig(f"pdf/{filename}.pdf", bbox_inches='tight')
        plt.close()
    print(f"\nras files have been converted to csv files that are saved to the csv folder.\
            \nPlots have been saved to the png and pdf folders.\n{90*'-'}")
    return None

def main():
    asc_to_csv_converter_plotter()

    return None


if __name__ == "__main__":
    main()

# End of file.
