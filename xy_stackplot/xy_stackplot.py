import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from diffpy.utils.parsers.loaddata import loadData
from matplotlib.ticker import MultipleLocator
try:
    from bg_mpl_stylesheet.bg_mpl_stylesheet import bg_mpl_style
    PLOT_STYLE = "found"
except ModuleNotFoundError:
    PLOT_STYLE = None


DPI = 600
FIGSIZE = (4,12)
FONTSIZE_LABELS = 20
FONTSIZE_TICKS = 16
STACKFACTOR = 0.5
XMIN = 1
XMAX = 10
MAJOR_INDEX_X = 1
LINEWIDTH = 1
COLORS = dict(bg_blue='#0B3C5D', bg_red='#B82601', bg_green='#1c6b0a',
              bg_lightblue='#328CC1', bg_darkblue='#062F4F', bg_yellow='#D9B310',
              bg_darkred='#984B43', bg_bordeaux='#76323F', bg_olivegreen='#626E60',
              bg_yellowgrey='#AB987A', bg_brownorange='#C09F80')



def d_xy_extract(files):
    d = {}
    for e in files:
        d[e.name] = loadData(str(e))

    return d


def xy_stackplot(d, output_folders):
    keys = list(d.keys())
    if not isinstance(PLOT_STYLE, type(None)):
        plt.style.use(bg_mpl_style)
    #     colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    # else:
    #     colors = list(COLORS.values())
    data_ext = keys[0].split(".")[-1]
    if data_ext == "gr":
        xlabel = r"$r$ $[\mathrm{\AA}]$"
        ylabel = r"$G$ $[\mathrm{\AA}^{-2}]$"
        colors = colors = plt.cm.Greens(np.linspace(1, 0.5, len(keys)))
    elif data_ext == "iq":
        xlabel = r"$Q$ $[\mathrm{\AA}^{-1}]$"
        ylabel = r"$I$ $[\mathrm{arb. u.}]$"
        colors = colors = plt.cm.Reds(np.linspace(1, 0.5, len(keys)))
    elif data_ext == "fq":
        xlabel = r"$Q$ $[\mathrm{\AA}^{-1}]$"
        ylabel = r"$F$ $[\mathrm{\AA}^{-1}]$"
        colors = colors = plt.cm.Blues(np.linspace(1, 0.5, len(keys)))
    fig, ax = plt.subplots(dpi=DPI, figsize=FIGSIZE)
    for i in range(len(keys)):
        x, y = d[keys[i]][:,0], d[keys[i]][:,1]
        xmin, xmax = np.amin(x), np.amax(x)
        ymin, ymax = np.amin(y), np.amax(y)
        xrange, yrange = xmax - xmin, ymax - ymin
        if i == 0:
            ymin_global = ymin * 1.1
            yoffset = ymax * STACKFACTOR
            ax.plot(x, y, c=colors[i], lw=LINEWIDTH)
        elif 0 < i < len(keys) - 1:
            yoffset += abs(ymin) * STACKFACTOR
            ax.plot(x, y + yoffset, c=colors[i], lw=LINEWIDTH)
            yoffset += ymax * STACKFACTOR
        else:
            yoffset += abs(ymin) * STACKFACTOR
            ax.plot(x, y + yoffset, c=colors[i], lw=LINEWIDTH)
            yoffset += ymax * 1.1
            ymax_global = yoffset
    ax.set_xlim(XMIN, XMAX)
    yrange_global = ymax_global - ymin_global
    ax.set_ylim(ymin_global, ymax_global)
    ax.set_xlabel(xlabel, fontsize=FONTSIZE_LABELS)
    ax.set_ylabel(ylabel, fontsize=FONTSIZE_LABELS)
    ax.tick_params(left=False, labelleft=False, right=False, labelright=False)
    ax.xaxis.set_major_locator(MultipleLocator(MAJOR_INDEX_X))
    ax.xaxis.set_minor_locator(MultipleLocator(MAJOR_INDEX_X / 5))
    for e in output_folders:
        plt.savefig(f"{e}/{data_ext}_stackplot.{e}", bbox_inches="tight")
    plt.close()

    return None

def main():
    data_path = Path.cwd() / "data"
    if not data_path.exists():
        data_path.mkdir()
        print(f"{80*'-'}\nA folder called '{data_path.name}' has been created. "
              f"\n{80*'-'}\nPlease place your data files here and rerun the "
              f"program.")
        sys.exit()
    data_files = list(data_path.glob("*.*"))
    if len(data_files) == 0:
        print(f"{80*'-'}\nNo files were found in the '{data_path.name}' "
              f"folder.\n{80*'-'}\nPlease place your data files here and rerun "
              f"the program.")
        sys.exit()
    data_files_exts = []
    for e in data_files:
        if not e.suffix in data_files_exts:
            data_files_exts.append(e.suffix)
    if len(data_files_exts) > 1:
        print(f"{80*'-'}\n{len(data_files_exts)} file extensions were found in "
              f"the '{data_path.name}' folder.\n{80*'-'}\nPlease ensure that "
              f"only 1 file extension is present in the '{data_path.name}' "
              f"folder and\nrerun program.")
        sys.exit()
    output_folders = ["pdf", "png", "svg"]
    for e in output_folders:
        if not (Path.cwd() / e).exists():
            (Path.cwd() / e).mkdir()
    print(f"{80*'-'}\nExtracting data from files...")
    d = d_xy_extract(data_files)
    print(f"Done extracting data from files.\n{80*'-'}\nPlotting data in "
          f"stackplot...")
    xy_stackplot(d, output_folders)
    print(f"Done plotting data files.\n{80*'-'}\nPlease see the "
          f"{output_folders} folders.")


    return None


if __name__ == "__main__":
    main()

# End of file.
