import sys
from pathlib import Path
import matplotlib.pyplot as plt
from diffpy.utils.parsers.loaddata import loadData

FIGSIZE = (10,4)
DPI = 300
FONTSIZE = 16
R_MAX_VALS = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
PLOTNAME = 'Ni_PDFcalc'
LABELS = ['Ni', 'Ni_tet-hole-occ']

COLORS = ['#0B3C5D', '#B82601', '#1c6b0a', '#328CC1', '#062F4F',
              '#D9B310', '#984B43', '#76323F', '#626E60', '#AB987A',
              '#C09F80']
# COLORS = [blue, red, green, lightblue, darkblue,
#               yellow, darkred, bordeaux, olivegreen, yellowgreen,
#               brownorange]

folders = ['png', 'pdf']
for folder in folders:
    if not (Path.cwd() / folder).exists():
        (Path.cwd() / folder).mkdir()
cgrpath = Path.cwd() / 'cgr'
if not cgrpath.exists():
    cgrpath.mkdir()
    print(f"{90*'-'}\nA folder called 'cgr' has been made.\
            \nPlease place your .cgr files there and rerun the code.\
            \n{90*'-'}")
    sys.exit()
files = list((Path.cwd() / 'cgr').glob('*.cgr'))
if len(files) == 0:
    print(f"{90*'-'}\nNo .cgr files found in the 'cgr' folder.\
            \nPlease place your .cgr files there and rerun the code..\
            \n{90*'-'}")
    sys.exit()
if len(files) != len(LABELS):
    print(f"{90*'-'}\nThe number of labels provided does not match the number of files.\
            \nConsider reviewing the labels in the top of the .py file\
            \nand the .cgr files in the cgr folder.\
            \n{90*'-'}")
    sys.exit()
r, g = [], []
for file in files:
    data = loadData(file)
    r.append(data[:,0])
    g.append(data[:,1])
print(f"{90*'-'}\nPlotting...")
for rmax_val in R_MAX_VALS:
    print(f"\tNi_PDFcalc_rmax={rmax_val}")
    fig, axs = plt.subplots(len(r), dpi=DPI, figsize=FIGSIZE,
                            sharex=True, sharey=False)
    fig.add_subplot(111, frameon=False)
    plt.tick_params(labelcolor='none', which='both',
                    top=False, bottom=False, left=False, right=False)
    plt.xlabel("$r$ $[\mathrm{\AA}]$", fontsize=FONTSIZE)
    plt.ylabel("$G$ $[\mathrm{\AA}^{-2}]$", fontsize=FONTSIZE)
    for i in range(0, len(r)):
        axs[i].plot(r[i], g[i], c=COLORS[i], lw=0.5, label=LABELS[i])
        axs[i].set_xlim(0.1, rmax_val)
        axs[i].tick_params(axis='both', which='major', labelsize=0.75*FONTSIZE)
        axs[i].legend(fontsize=0.6*FONTSIZE)
        for folder in folders:
            plt.savefig(f"{folder}/{PLOTNAME}_rmax={rmax_val}.{folder}", bbox_inches='tight')
print(f"\nPlots have been saved to the png and pdf folders.\n{90*'-'}")

# End of file.
