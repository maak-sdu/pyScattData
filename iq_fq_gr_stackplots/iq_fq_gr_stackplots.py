import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from diffpy.utils.parsers.loaddata import loadData
from matplotlib.ticker import MultipleLocator
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
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


SCATTLABEL_DICT = {"gr": dict(x = r"$r$ $[\mathrm{\AA}]$",
                              y = r"$G$ $[\mathrm{\AA}^{-2}]$"),
                   "fq[A^-1]": dict(x = r"$Q$ $[\mathrm{\AA}^{-1}]$",
                                    y = r"$F$ $[\mathrm{\AA}^{-1}]$"),
                   "fq[nm^-1]": dict(x = r"$Q$ $[\mathrm{nm}^{-1}]$",
                                     y = r"$F$ $[\mathrm{\nm}^{-1}]$"),
                   "sq[A^-1]": dict(x = r"$Q$ $[\mathrm{\AA}^{-1}]$",
                                    y = r"$S$ $[\mathrm{arb. u.}]$"),
                   "sq[nm^-1]": dict(x = r"$Q$ $[\mathrm{nm}^{-1}]$",
                                     y = r"$S$ $[\mathrm{arb. u.}]$"),
                   "iq[A^-1]": dict(x = r"$Q$ $[\mathrm{\AA}^{-1}]$",
                                    y = r"$I$ $[\mathrm{arb. u.}]$"),
                   "iq[nm^-1]": dict(x = r"$Q$ $[\mathrm{nm}^{-1}]$",
                                     y = r"$I$ $[\mathrm{arb. u.}]$"),
                   "iq[2theta]": dict(x = r"$2\theta$ $[\degree]$",
                                      y = r"$I$ $[\mathrm{arb. u.}]$"),
                   "xy": dict(x = r"$x$",
                              y = r"$y$")
                    }


CMAPS = dict(blue = LinearSegmentedColormap.from_list('my_gradient', (
                                                                    (0.000, (0.043, 0.235, 0.365)),
                                                                    (1.000, (1.000, 1.000, 1.000)))),
             red=LinearSegmentedColormap.from_list('my_gradient', (
                                                                    (0.000, (0.722, 0.149, 0.004)),
                                                                    (1.000, (1.000, 1.000, 1.000)))),
             green=LinearSegmentedColormap.from_list('my_gradient', (
                                                                    (0.000, (0.110, 0.420, 0.039)),
                                                                    (1.000, (1.000, 1.000, 1.000)))),
                                                                            )


def d_xy_extract(files):
    d = {}
    for e in files:
        d[e.name] = loadData(str(e))

    return d


def iq_fq_gr_stackplot(d, output_folders):
    d_keys = list(d.keys())
    if not isinstance(PLOT_STYLE, type(None)):
        plt.style.use(bg_mpl_style)
    fig, axs = plt.subplots(dpi=DPI, figsize=FIGSIZE, ncols=3, nrows=1)
    for i in range(len(d_keys)):
        keys = list(d[d_keys[i]].keys())
        if d_keys[i] == "gr":
            xlabel = SCATTLABEL_DICT["gr"]["x"]
            ylabel = SCATTLABEL_DICT["gr"]["y"]
            colors = CMAPS["blue"](np.linspace(0, 0.5, len(keys)))
        elif d_keys[i] == "iq":
            xlabel = SCATTLABEL_DICT["iq[A^-1]"]["x"]
            ylabel = SCATTLABEL_DICT["iq[A^-1]"]["y"]
            colors = CMAPS["red"](np.linspace(0, 0.5, len(keys)))
        elif d_keys[i] == "fq":
            xlabel = SCATTLABEL_DICT["fq[A^-1]"]["x"]
            ylabel = SCATTLABEL_DICT["fq[A^-1]"]["y"]
            colors = CMAPS["green"](np.linspace(0, 0.5, len(keys)))
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
        print(f"{80*'-'}")
        sys.exit()
    data_files = {}
    for p in data_paths:
        if not p.name == "echem":
            data_files[p.name] = list(p.glob(f"*.{p.name}"))
        else:
            data_files[p.name] = list(p.glob(f"*.txt"))
    for k in data_files.keys():
        if len(data_files[k]) == 0 and k != "echem":
            print(f"{80*'-'}\nNo .{k} files were found in the '{k}' folder.")
        elif len(data_files[k]) == 0 and k == "echem":
            print(f"{80*'-'}\nNo {k} files were found in the '{k}' folder.")
            exit = True
    if exit is True:
        print(f"{80*'-'}\nPlease place your data files in the appropriate "
              f"folder(s) and rerun the program.\n{80*'-'}")
        sys.exit()
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
