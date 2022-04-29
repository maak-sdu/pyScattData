import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from diffpy.utils.parsers.loaddata import loadData
from matplotlib.ticker import MultipleLocator
try:
    from bg_mpl_stylesheet.bg_mpl_stylesheet import bg_mpl_style
    PLOT_STYLE = "found"
except ModuleNotFoundError:
    PLOT_STYLE = None


DPI = 600
FONTSIZE_LABELS = 20
FONTSIZE_TICKS = 16
FONTSIZE_LEGEND = 20
FONTSIZE_TEXT = 16
RLABEL = r"$r$ $[\mathrm{\AA}]$"
GLABEL = r"$G$ $[\mathrm{\AA}^{-2}]$"
GOBSLABEL = r"$G_{\mathrm{obs}}$"
GCALCLABEL = r"$G_{\mathrm{calc}}$"
GDIFFLABEL = r"$G_{\mathrm{diff}}$"
SAMPLELABELS = ["3 nm", "5 nm", "3 nm (Li)", "5 nm (Li)"]
LINEWIDTH = 1
LINEWIDTH_LEGEND = 2
SCATTERSIZE = 1
XINDEX_MAJOR = 5
XINDEX_MINOR = XINDEX_MAJOR / 5
YINDEX_MAJOR = 1
YINDEX_MINOR = YINDEX_MAJOR / 5
COLORS = dict(bg_blue='#0B3C5D', bg_red='#B82601', bg_green='#1c6b0a',
              bg_lightblue='#328CC1', bg_darkblue='#062F4F', bg_yellow='#D9B310',
              bg_darkred='#984B43', bg_bordeaux='#76323F', bg_olivegreen='#626E60',
              bg_yellowgrey='#AB987A', bg_brownorange='#C09F80')


def dict_extract(files):
    d = {}
    for i in range(len(files)):
        d[i] = loadData(str(files[i]))

    return d


def dict_rw_extract(files):
    d = {}
    for i in range(len(files)):
        with files[i].open(mode="r") as f:
            lines = f.readlines()
        for l in lines:
            if "Rw" in l:
                d[i] = l.split()[-1]
                break

    return d


def fit_res_plot(d_fit, d_res, output_folders):
    keys = d_fit.keys()
    if not isinstance(PLOT_STYLE, type(None)):
        plt.style.use(bg_mpl_style)
        colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    else:
        colors = list(COLORS.values())
    fig, axs = plt.subplots(ncols=1,
                            nrows=len(keys),
                            dpi=DPI,
                            figsize=(8, 2*len(keys)),
                            sharex=True,
                            sharey=True,
                            gridspec_kw=dict(hspace=0)
                            )
    for i in range(len(keys)):
        x, ycalc, y = d_fit[i][:,0], d_fit[i][:,1], d_fit[i][:,2]
        xmin, xmax = np.amin(x), np.amax(x)
        xrange = xmax - xmin
        ydiff = y - ycalc
        ymin, ymax = np.amin(y), np.amax(y)
        ydiffmin, ydiffmax = np.amin(ydiff), np.amax(ydiff)
        ydiff_offset = ydiff - 1.1 * (abs(ymin) + abs(ydiffmax))
        if len(keys) > 1:
            axs[i].scatter(x, y, s=SCATTERSIZE, c=colors[0], label=GOBSLABEL)
            axs[i].plot(x, ycalc, lw=LINEWIDTH, c=colors[1], label=GCALCLABEL)
            axs[i].plot(x, ydiff_offset, lw=LINEWIDTH, c=colors[2], label=GDIFFLABEL)
            axs[i].set_xlim(xmin, xmax)
            axs[i].xaxis.set_major_locator(MultipleLocator(XINDEX_MAJOR))
            axs[i].xaxis.set_minor_locator(MultipleLocator(XINDEX_MINOR))
            axs[i].yaxis.set_major_locator(MultipleLocator(YINDEX_MAJOR))
            axs[i].yaxis.set_minor_locator(MultipleLocator(YINDEX_MINOR))
            axs[i].tick_params(axis="both", labelsize=FONTSIZE_TICKS)
            axs[-1].set_ylabel('.', color=(0, 0, 0, 0))
        else:
            axs.scatter(x, y, s=SCATTERSIZE, c=colors[0], label=GOBSLABEL)
            axs.plot(x, ycalc, lw=LINEWIDTH, c=colors[1], label=GCALCLABEL)
            axs.plot(x, ydiff_offset, lw=LINEWIDTH, c=colors[2], label=GDIFFLABEL)
            axs.set_xlim(xmin, xmax)
            axs.xaxis.set_major_locator(MultipleLocator(XINDEX_MAJOR))
            axs.xaxis.set_minor_locator(MultipleLocator(XINDEX_MINOR))
            axs.yaxis.set_major_locator(MultipleLocator(YINDEX_MAJOR))
            axs.yaxis.set_minor_locator(MultipleLocator(YINDEX_MINOR))
            axs.tick_params(axis="both", labelsize=FONTSIZE_TICKS)
            axs.set_ylabel('.', color=(0, 0, 0, 0))
        if i == 0:
            blue_marker = plt.scatter([], [], marker='o', facecolors='none',
                                      edgecolors=colors[0])
            blue_marker.remove()
            red_line = Line2D([], [], color=colors[1], linewidth=LINEWIDTH_LEGEND)
            green_line = Line2D([], [], color=colors[2], linewidth=LINEWIDTH_LEGEND)
            if len(keys) == 1:
                anchor_y = 1.2
            elif len(keys) == 2:
                anchor_y = 1.025
            elif len(keys) == 3:
                anchor_y = 1.0
            elif len(keys) == 4:
                anchor_y = 0.97
            else:
                anchor_y = 0.935
            fig.legend(handles=[(blue_marker), (red_line), (green_line)],
                       labels=['$G_{\mathrm{obs}}$', '$G_{\mathrm{calc}}$',
                               '$G_{\mathrm{diff}}$'],
                       ncol=3,
                       facecolor="white",
                       frameon=False,
                       fontsize=FONTSIZE_LEGEND,
                       loc="upper center",
                       bbox_to_anchor=(0.5, anchor_y)
                       )
    for i in range(len(keys)):
        rw = float(d_res[i])
        s = f"{SAMPLELABELS[i]}\n" + r"$R_{\mathrm{w}}=$" + fr"$\;{rw:.2f}$"
        if len(keys) > 1:
            xlim, ylim = axs[i].get_xlim(), axs[i].get_ylim()
            xrange = float(xlim[1]) - float(xlim[0])
            yrange = float(ylim[1]) - float(ylim[0])
            axs[i].text(1.03 * xrange,
                        0.225 * yrange,
                        s,
                        fontsize=FONTSIZE_TEXT,
                        ha="right")
        else:
            xlim, ylim = axs.get_xlim(), axs.get_ylim()
            xrange = float(xlim[1]) - float(xlim[0])
            yrange = float(ylim[1]) - float(ylim[0])
            axs.text(1.03 * xrange,
                     0.225 * yrange,
                     s,
                     fontsize=FONTSIZE_TEXT,
                     ha="right")
    plt.xlabel(RLABEL, fontsize=FONTSIZE_LABELS)
    fig.text(0.04, 0.5, GLABEL, va='center', ha='center',
             rotation='vertical', fontsize=FONTSIZE_LABELS)
    for e in output_folders:
        plt.savefig(f"{e}/fit_res_plot_stack.{e}", bbox_inches="tight")

    return None


def main():
    fit_path, res_path = Path.cwd() / "fit", Path.cwd() / "res"
    data_paths = [fit_path, res_path]
    exit = False
    for p in data_paths:
        if not p.exists():
            p.mkdir()
            print(f"{80*'-'}\nA folder called '{p.name}' has been created.\n"
                  f"Please place your .{p.name} files here and rerun the "
                  f"program.")
            exit = True
    if exit is True:
        sys.exit()
    fit_files = list(fit_path.glob("*.fit"))
    res_files = list(res_path.glob("*.res"))
    if len(fit_files) == 0:
        print(f"{80*'-'}\nNo .{fit_path.name} files were found in the "
              f"'{fit_path.name}' folder.\nPlease place your .{fit_path.name} "
              f"files here and rerun the program.")
        exit = True
    if len(res_files) == 0:
        print(f"{80*'-'}\nNo .{res_path.name} files were found in the "
              f"'{res_path.name}' folder.\nPlease place your .{fit_path.name} "
              f"files here and rerun the program.")
        exit = True
    if len(fit_files) != len(res_files):
        print(f"{80*'-'}\n{len(fit_files)} .{fit_path.name} files were found "
              f"in the '{fit_path.name}' folder.\n{len(res_files)} "
              f".{res_path.name} files were found  in the '{res_path.name}' "
              f"folder.\n{80*'-'}\nPlease review the '{fit_path.name}' and "
              f"'{res_path.name}' folders to ensure files are properly placed "
              f"\nand rerun the program.")
        exit = True
    if exit is True:
        sys.exit()
    print(f"{80*'-'}\n.{fit_path.name} and .{res_path.name} files will be "
          f"paired the following way:")
    for i in range(len(fit_files)):
        print(f"\t{i}\t{fit_files[i].name}\t{res_files[i].name}")
    output_folders = ["pdf", "png", "svg"]
    for folder in output_folders:
        p = Path.cwd() / folder
        if not p.exists():
            p.mkdir()
    print(f"{80*'-'}\nExtracting data from .{fit_path.name} and "
          f".{res_path.name} files...")
    d_fit = dict_extract(fit_files)
    d_res = dict_rw_extract(res_files)
    print(f"Done extracting data.\n{80*'-'}\nPlotting data...")
    fit_res_plot(d_fit, d_res, output_folders)
    print(f"Done plotting data.\n{80*'-'}\nPlease see the {output_folders} "
          f"folders.")

    return None


if __name__ == "__main__":
    main()

# End of file.
