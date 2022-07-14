import sys
from pathlib import Path
import numpy as np
from diffpy.utils.parsers.loaddata import loadData
from scipy.constants import physical_constants
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
try:
    from bg_mpl_stylesheet.bg_mpl_stylesheet import bg_mpl_style
    PLOT_STYLE = "found"
except ModuleNotFoundError:
    PLOT_STYLE = None


# Inputs to load echem
INDEX_TIME = 0
INDEX_VOLTAGE = 1
INDEX_CURRENT = 2

# Inputs to calculate amount of working ion transferred
WORKING_ION_CHARGE = 1
WORKING_ION_START_VALUE = 0
MOLAR_MASS = 79.866
MASS = 0.6 * 11.276 * 10**-3

TOLERANCE_FACTOR = 10**2
VLINES_ECHEM = True


PLOT_DICT = dict(dpi = 600,
                 figsize = (16,12),
                 fontsize_labels = 20,
                 fontsize_ticks = 14,
                 stackfactor=0.5,
                 xmin = 1,
                 xmax = 10,
                 voltage_min = 1,
                 voltage_max = 3,
                 major_tick_index_x = 2,
                 major_tick_index_time = 1,
                 major_tick_index_v = 0.5,
                 linewidth = 1,
                 linewidth_echem = 2,
                 wspace=0.3,
                 )

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
ECHEMLABEL_DICT = {"V_t[h]": dict(x = r"$t$ $[\mathrm{h}]$",
                                  y = r"$V$ $[\mathrm{V}]$"),
                   "Ewe_Li_t[h]": dict(x = r"$t$ $[\mathrm{h}]$",
                                       y = r"$E_{\mathrm{we}}$ vs." + "\n" + r"Li/Li$^{+} [\mathrm{V}]$"),
                   "Ewe_Na_t[h]": dict(x = r"$t$ $[\mathrm{h}]$",
                                       y = r"$E_{\mathrm{we}}$ vs." + "\n" + r"Na/Na$^{+} [\mathrm{V}]$"),
                   "Ewe_Li_x[h]": dict(x = r"$x$ in Li$_{x}$TiO$_{2}$",
                                       # y = r"$E_{\mathrm{we}}$ vs." + "\n" + r"Li/Li$^{+} [\mathrm{V}]$"),
                                       y = r"$E_{\mathrm{we}}$ vs. Li/Li$^{+}$ [V]"),
                   "Ewe_Na_x[h]": dict(x = r"$x$ in Li$_{x}$TiO$_{2}$",
                                       y = r"$E_{\mathrm{we}}$ vs." + "\n" + r"Na/Na$^{+} [\mathrm{V}]$"),
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


def echem_load(echem_file):
    d = {}
    data = loadData(str(echem_file))
    d["time"], d["voltage"] = data[:,INDEX_TIME], data[:,INDEX_VOLTAGE]
    d["current"] = data[:,INDEX_CURRENT]

    return d


def x_from_dict_calculate(d):
    time, current = d["time"], d["current"]
    x = [WORKING_ION_START_VALUE]
    n = MASS / MOLAR_MASS
    f = physical_constants["Faraday constant"][0]
    for i in range(1, len(time)):
        delta_q =  - current[i] * (time[i] - time[i-1]) * 60**2
        delta_x = delta_q / (n * f)
        x.append(x[i-1] + delta_x)
    change_indices = [i for i in range(1, len(current))
                      if current[i] != 0
                      and current[i-1] == 0]
    d["x"], d["change_indices"] = np.array(x), np.array(change_indices)

    return d


def iq_fq_gr_stackplot_echem_plot(d, output_folders):
    d_echem = d["echem"]
    time, voltage = d_echem["time"], d_echem["voltage"]
    current, x = d_echem["current"], d_echem["x"]
    change_indices = d_echem["change_indices"]
    t_changes = [time[e] for e in change_indices]
    t_changes_labels = [f"{x[e]:.3f}" for e in change_indices]
    xticks_labels = [f"{e:.1f}" for e in np.arange(0, 0.8, 0.2)]
    xticks_labels.append(t_changes_labels[0])
    for e in np.arange(0.6, 0.3, -0.2):
        xticks_labels.append(f"{e:.1f}")
    xticks_labels.append(t_changes_labels[1])
    for e in np.arange(0.4, 0.6, 0.2):
        xticks_labels.append(f"{e:.1f}")
    t_xticks = np.array([])
    j = 0
    for i in range(0, len(x)):
        if np.isclose(np.array(xticks_labels[j], dtype=float),
                      x[i],
                      atol=abs(x[0] - x[1]) * TOLERANCE_FACTOR
                      ):
            t_xticks = np.append(t_xticks, time[i])
            j += 1
            if j == len(xticks_labels):
                break
    time_min, time_max = np.amin(time), np.amax(time)
    d_keys = [k for k in d.keys() if not k == "echem"]
    if not isinstance(PLOT_STYLE, type(None)):
        plt.style.use(bg_mpl_style)
    fig, axs = plt.subplots(dpi=PLOT_DICT["dpi"],
                            figsize=PLOT_DICT["figsize"],
                            ncols=4,
                            nrows=1,
                            )
    plt.subplots_adjust(wspace=PLOT_DICT["wspace"])
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
                yoffset = ymax * PLOT_DICT["stackfactor"]
                axs[i].plot(x, y, c=colors[j], lw=PLOT_DICT["linewidth"])
            elif 0 < j < len(keys) - 1:
                yoffset += abs(ymin) * PLOT_DICT["stackfactor"]
                axs[i].plot(x, y + yoffset, c=colors[j], lw=PLOT_DICT["linewidth"])
                yoffset += ymax * PLOT_DICT["stackfactor"]
            else:
                yoffset += abs(ymin) * PLOT_DICT["stackfactor"]
                axs[i].plot(x, y + yoffset, c=colors[j], lw=PLOT_DICT["linewidth"])
                yoffset += ymax * 1.1
                ymax_global = yoffset
        axs[i].set_xlim(PLOT_DICT["xmin"], PLOT_DICT["xmax"])
        yrange_global = ymax_global - ymin_global
        axs[i].set_ylim(ymin_global, ymax_global)
        axs[i].set_xlabel(xlabel, fontsize=PLOT_DICT["fontsize_labels"])
        axs[i].set_ylabel(ylabel, fontsize=PLOT_DICT["fontsize_labels"])
        axs[i].tick_params(left=False,
                           labelleft=False,
                           right=False,
                           labelright=False,
                           labelsize=PLOT_DICT["fontsize_ticks"],
                           )
        axs[i].xaxis.set_major_locator(MultipleLocator(PLOT_DICT["major_tick_index_x"]))
        axs[i].xaxis.set_minor_locator(MultipleLocator(PLOT_DICT["major_tick_index_x"] / 5))
        if i == 0:
            title = "(a)"
        elif i == 1:
            title = "(b)"
        elif i == 2:
            title = "(c)"
        axs[i].set_title(title, fontdict = dict(fontsize=24), pad = 10)
    axs31 = axs[3].twinx()
    axs[3].plot(voltage, time, lw=PLOT_DICT["linewidth_echem"])
    axs[3].set_xlim(PLOT_DICT["voltage_min"], PLOT_DICT["voltage_max"])
    axs[3].set_ylim(time_min, time_max)
    axs31.set_ylim(time_min, time_max)
    # ax21.set_xlabel(d_plot["timelabel"], fontsize=d_plot["fontsize_labels"])
    # ax21.set_ylabel(d_plot["voltagelabel"], fontsize=d_plot["fontsize_labels"])
    axs[3].yaxis.set_major_locator(MultipleLocator(PLOT_DICT["major_tick_index_time"]))
    # axs[3].yaxis.set_minor_locator(MultipleLocator(PLOT_DICT["major_tick_index_time"] / 5))
    axs[3].xaxis.set_major_locator(MultipleLocator(PLOT_DICT["major_tick_index_v"]))
    axs[3].xaxis.set_minor_locator(MultipleLocator(PLOT_DICT["major_tick_index_v"] / 5))
    axs[3].tick_params(axis="y",
                      labelleft=True,
                      labelright=False,
                      left=True,
                      right=False,
                      labelsize=PLOT_DICT["fontsize_ticks"]
                      )
    axs31.set_yticks(t_xticks)
    axs31.set_yticklabels(xticks_labels)
    axs31.tick_params(axis="y",
                      labelleft=False,
                      labelright=True,
                      left=False,
                      right=True,
                      labelsize=PLOT_DICT["fontsize_ticks"]
                      )
    axs31.set_ylabel(ECHEMLABEL_DICT["Ewe_Li_x[h]"]["x"],
                     fontsize=PLOT_DICT["fontsize_labels"],
                     )
    axs[3].set_xlabel(ECHEMLABEL_DICT["Ewe_Li_x[h]"]["y"],
                     fontsize=PLOT_DICT["fontsize_labels"]
                     )
    axs[3].set_ylabel(ECHEMLABEL_DICT["Ewe_Li_t[h]"]["x"],
                      fontsize=PLOT_DICT["fontsize_labels"],
                      )
    # axs31.yaxis.set_tick_params(labelsize=PLOT_DICT["fontsize_ticks"])
    axs[3].xaxis.set_tick_params(labelsize=PLOT_DICT["fontsize_ticks"])
    axs[3].invert_xaxis()
    if not isinstance(VLINES_ECHEM, type(None)):
        axs[3].axhline(y=0.99*t_changes[0], ls="--", c="k", lw=3, zorder=1)
        axs[3].axhline(y=0.995*t_changes[1], ls="--", c="k", lw=3, zorder=1)
    axs[3].set_title("(d)", fontdict = dict(fontsize=24), pad = 10)
    for e in output_folders:
        plt.savefig(f"{e}/iq_fq_gr_stackplot_echem.{e}", bbox_inches="tight")
    plt.close()

    return None


def main():
    iq_path = Path.cwd() / "iq"
    fq_path = Path.cwd() / "fq"
    gr_path = Path.cwd() / "gr"
    echem_path = Path.cwd() / "echem"
    data_paths = [iq_path, fq_path, gr_path, echem_path]
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
    print("\techem")
    d_echem = echem_load(data_files["echem"][0])
    d_echem = x_from_dict_calculate(d_echem)
    d = dict(iq=d_iq, fq=d_fq, gr=d_gr, echem=d_echem)
    print(f"Done extracting data from files.\n{80*'-'}\nPlotting data in "
          f"stackplot...")
    iq_fq_gr_stackplot_echem_plot(d, output_folders)
    print(f"Done plotting data files.\n{80*'-'}\nPlease see the "
          f"{output_folders} folders.")


    return None


if __name__ == "__main__":
    main()

# End of file.
