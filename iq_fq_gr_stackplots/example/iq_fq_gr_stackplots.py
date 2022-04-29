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
FIGSIZE = (12,12)
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


def iq_fq_gr_stackplot(d, output_folders):
    d_keys = list(d.keys())
    if not isinstance(PLOT_STYLE, type(None)):
        plt.style.use(bg_mpl_style)
    #     colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    # else:
    #     colors = list(COLORS.values())
    fig, axs = plt.subplots(dpi=DPI, figsize=FIGSIZE, ncols=3, nrows=1)
    for i in range(len(d_keys)):
        keys = list(d[d_keys[i]].keys())
        if d_keys[i] == "gr":
            xlabel = r"$r$ $[\mathrm{\AA}]$"
            ylabel = r"$G$ $[\mathrm{\AA}^{-2}]$"
            colors = colors = plt.cm.Greens(np.linspace(1, 0.5, len(keys)))
        elif d_keys[i] == "iq":
            xlabel = r"$Q$ $[\mathrm{\AA}^{-1}]$"
            ylabel = r"$I$ $[\mathrm{arb. u.}]$"
            colors = colors = plt.cm.Reds(np.linspace(1, 0.5, len(keys)))
        elif d_keys[i] == "fq":
            xlabel = r"$Q$ $[\mathrm{\AA}^{-1}]$"
            ylabel = r"$F$ $[\mathrm{\AA}^{-1}]$"
            colors = colors = plt.cm.Blues(np.linspace(1, 0.5, len(keys)))
        for j in range(len(keys)):
            x, y = d[d_keys[i]][keys[j]][:,0], d[d_keys[i]][keys[j]][:,1]
            xmin, xmax = np.amin(x), np.amax(x)
            ymin, ymax = np.amin(y), np.amax(y)
            xrange, yrange = xmax - xmin, ymax - ymin
            if j == 0:
                ymin_global = ymin * 1.1
                yoffset = ymax * STACKFACTOR
                axs[i].plot(x, y, c=colors[j], lw=LINEWIDTH)
            elif 0 < j < len(keys) - 1:
                yoffset += abs(ymin) * STACKFACTOR
                axs[i].plot(x, y + yoffset, c=colors[j], lw=LINEWIDTH)
                yoffset += ymax * STACKFACTOR
            else:
                yoffset += abs(ymin) * STACKFACTOR
                axs[i].plot(x, y + yoffset, c=colors[j], lw=LINEWIDTH)
                yoffset += ymax * 1.1
                ymax_global = yoffset
        axs[i].set_xlim(XMIN, XMAX)
        yrange_global = ymax_global - ymin_global
        axs[i].set_ylim(ymin_global, ymax_global)
        axs[i].set_xlabel(xlabel, fontsize=FONTSIZE_LABELS)
        axs[i].set_ylabel(ylabel, fontsize=FONTSIZE_LABELS)
        axs[i].tick_params(left=False, labelleft=False, right=False, labelright=False)
        axs[i].xaxis.set_major_locator(MultipleLocator(MAJOR_INDEX_X))
        axs[i].xaxis.set_minor_locator(MultipleLocator(MAJOR_INDEX_X / 5))
    for e in output_folders:
        plt.savefig(f"{e}/iq_fq_gr_stackplot.{e}", bbox_inches="tight")
    plt.close()

    return None


def main():
    iq_path = Path.cwd() / "iq"
    fq_path = Path.cwd() / "fq"
    gr_path = Path.cwd() / "gr"
    data_paths = [iq_path, fq_path, gr_path]
    exit = False
    for p in data_paths:
        if not p.exists():
            p.mkdir()
            print(f"{80*'-'}\nA folder called '{p.name}' has been created. "
                  f"\nPlease place your .{p.name} data files here and rerun "
                  f"the program.")
            exit = True
    if exit is True:
        sys.exit()
    data_files = {}
    for p in data_paths:
        data_files[p.name] = list(p.glob(f"*.{p.name}"))
    for k in data_files.keys():
        if len(data_files[k]) == 0:
            print(f"{80*'-'}\nNo .{k} files were found in the '{k}' folder.")
            exit = True
    if exit is True:
        print(f"{80*'-'}\nPlease place your data files in the appropriate "
              f"folder(s) and rerun the program.")
        sys.exit()
    # data_files_exts = {}
    # if len(data_files_exts) > 1:
    #     print(f"{80*'-'}\n{len(data_files_exts)} file extensions were found in "
    #           f"the '{data_path.name}' folder.\n{80*'-'}\nPlease ensure that "
    #           f"only 1 file extension is present in the '{data_path.name}' "
    #           f"folder and\nrerun program.")
    #     sys.exit()
    output_folders = ["pdf", "png", "svg"]
    for e in output_folders:
        if not (Path.cwd() / e).exists():
            (Path.cwd() / e).mkdir()
    print(f"{80*'-'}\nExtracting data from files...\n\tiq")
    d_iq = d_xy_extract(data_files["iq"])
    print("\tfq")
    d_fq = d_xy_extract(data_files["fq"])
    print("\tgr")
    d_gr = d_xy_extract(data_files["gr"])
    d = dict(iq=d_iq, fq=d_fq, gr=d_gr)
    print(f"Done extracting data from files.\n{80*'-'}\nPlotting data in "
          f"stackplot...")
    iq_fq_gr_stackplot(d, output_folders)
    print(f"Done plotting data files.\n{80*'-'}\nPlease see the "
          f"{output_folders} folders.")


    return None


if __name__ == "__main__":
    main()

# End of file.
