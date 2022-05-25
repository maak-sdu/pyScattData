import sys
from pathlib import Path
from diffpy.utils.parsers.loaddata import loadData
import numpy as np
from scipy.constants import physical_constants
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.colors as colors
from matplotlib.gridspec import GridSpec
from matplotlib.colors import LinearSegmentedColormap
try:
    from bg_mpl_stylesheet.bg_mpl_stylesheet import bg_mpl_style
    PLOT_STYLE = "found"
except ModuleNotFoundError:
    PLOT_STYLE = None


MY_GRADIENT = LinearSegmentedColormap.from_list('my_gradient', (
                 # Edit this gradient at https://eltos.github.io/gradient/#0B3C5D-0B3C5D-FFFFFF-B82601-B82601
                 (0.000, (0.043, 0.235, 0.365)),
                 (0.250, (0.200, 0.400, 0.500)),
                 (0.500, (1.000, 1.000, 1.000)),
                 (0.750, (0.850, 0.200, 0.100)),
                 (1.000, (0.722, 0.149, 0.004))))

def shiftedColorMap(cmap, start=0, midpoint=0.5, stop=1.0, name='shiftedcmap'):
    '''
    Function to offset the "center" of a colormap. Useful for
    data with a negative min and positive max and you want the
    middle of the colormap's dynamic range to be at zero.

    Input
    -----
      cmap : The matplotlib colormap to be altered
      start : Offset from lowest point in the colormap's range.
          Defaults to 0.0 (no lower offset). Should be between
          0.0 and `midpoint`.
      midpoint : The new center of the colormap. Defaults to
          0.5 (no shift). Should be between 0.0 and 1.0. In
          general, this should be  1 - vmax / (vmax + abs(vmin))
          For example if your data range from -15.0 to +5.0 and
          you want the center of the colormap at 0.0, `midpoint`
          should be set to  1 - 5/(5 + 15)) or 0.75
      stop : Offset from highest point in the colormap's range.
          Defaults to 1.0 (no upper offset). Should be between
          `midpoint` and 1.0.
    '''
    cdict = {
        'red': [],
        'green': [],
        'blue': [],
        'alpha': []
    }

    # regular index to compute the colors
    reg_index = np.linspace(start, stop, 257)

    # shifted index to match the data
    shift_index = np.hstack([
        np.linspace(0.0, midpoint, 128, endpoint=False),
        np.linspace(midpoint, 1.0, 129, endpoint=True)
    ])

    for ri, si in zip(reg_index, shift_index):
        r, g, b, a = cmap(ri)

        cdict['red'].append((si, r, r))
        cdict['green'].append((si, g, g))
        cdict['blue'].append((si, b, b))
        cdict['alpha'].append((si, a, a))

    newcmap = colors.LinearSegmentedColormap(name, cdict)
    plt.register_cmap(cmap=newcmap)

    return newcmap


def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
               'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name,
                                                   a=minval,
                                                   b=maxval
                                                   ),
               cmap(np.linspace(minval, maxval, n)))

    return new_cmap


ORIG_CMAP = MY_GRADIENT
TRUNCATE_CMAP_IQ = truncate_colormap(MY_GRADIENT, 0.5, 1)
SHRUNK_CMAP_FQ = shiftedColorMap(ORIG_CMAP, start=-0.5, midpoint=0.0, stop=1.0, name='shrunk')


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
                   "V_x[h]": dict(x = r"$x$ in Li$_{x}$TiO$_{2}$",
                                  y = r"$V$ $[\mathrm{V}]$"),
                   "Ewe_Li_x[h]": dict(x = r"$x$ in Li$_{x}$TiO$_{2}$",
                                       y = r"$E_{\mathrm{we}}$ vs." + "\n" + r"Li/Li$^{+}$ $[\mathrm{V}]$"),
                   "Ewe_Na_t[h]": dict(x = r"$x$ in Li$_{x}$TiO$_{2}$",
                                       y = r"$E_{\mathrm{we}}$ vs." + "\n" + r"Na/Na$^{+}$ $[\mathrm{V}]$")
                    }

MY_GRADIENT = LinearSegmentedColormap.from_list('my_gradient', (
                 # Edit this gradient at https://eltos.github.io/gradient/#0B3C5D-0B3C5D-FFFFFF-B82601-B82601
                 (0.000, (0.043, 0.235, 0.365)),
                 (0.250, (0.200, 0.400, 0.500)),
                 (0.500, (1.000, 1.000, 1.000)),
                 (0.750, (0.850, 0.200, 0.100)),
                 (1.000, (0.722, 0.149, 0.004))))
PLOT_DICT = dict(dpi = 600,
                 figsize = (8,10),
                 fontsize_labels = 20,
                 fontsize_ticks = 16,
                 xmin_upper = 1,
                 xmax_upper = 10,
                 ymin_upper = 0,
                 ymax_upper = 2*10**5,
                 xmin_lower = 1,
                 xmax_lower = 10,
                 ymin_lower = -0.5,
                 ymax_lower = 1,
                 voltage_min = 1,
                 voltage_max = 3,
                 indexlabel = "Scan Number",
                 xlabel_upper = SCATTLABEL_DICT["iq[A^-1]"]["x"],
                 ylabel_upper = SCATTLABEL_DICT["iq[A^-1]"]["y"],
                 xlabel_lower = SCATTLABEL_DICT["fq[A^-1]"]["x"],
                 ylabel_lower = SCATTLABEL_DICT["fq[A^-1]"]["y"],
                 timelabel = ECHEMLABEL_DICT["Ewe_Li_t[h]"]["x"],
                 voltagelabel = ECHEMLABEL_DICT["Ewe_Li_x[h]"]["y"],
                 xlabel = ECHEMLABEL_DICT["Ewe_Li_x[h]"]["x"],
                 minor_tick_index_upper = 5,
                 minor_tick_index_lower = 5,
                 minor_tick_index_echem = 5,
                 cmap_upper = TRUNCATE_CMAP_IQ,
                 cmap_lower = SHRUNK_CMAP_FQ,
                 cbar_ticks_upper = 9,
                 cbar_ticks_lower = 7,
                 linewidth = 2,
                 hspace = 0.1)


def xy_stack(data_files):
    d = {}
    for i in range(len(data_files)):
        print(f"\t{data_files[i].name}")
        xy = loadData(str(data_files[i]))
        x, y = xy[:,0], xy[:,1]
        if i == 0:
            y_array = y
        else:
            y_array = np.column_stack((y_array, y))
    d["x"], d["y_array"] = x, y_array

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
                      and current[i] * current[i-1] <= 0]
    d["x"], d["change_indices"] = np.array(x), np.array(change_indices)

    return d


def xy_overview_stack_echem(d_upper, d_lower, d_echem, d_plot, output_paths):
    x_upper, y_upper = d_upper["x"], d_upper["y_array"]
    x_lower, y_lower = d_lower["x"], d_lower["y_array"]
    time, voltage = d_echem["time"], d_echem["voltage"]
    current, x = d_echem["current"], d_echem["x"]
    change_indices = d_echem["change_indices"]
    t_changes = [time[e] for e in change_indices]
    t_changes_labels = [f"{x[e]:.2f}" for e in change_indices]
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
    time_range = time_max - time_min
    xrange_upper = d_plot["xmax_upper"] - d_plot["xmin_upper"]
    yrange_upper = d_plot["ymax_upper"] - d_plot["ymin_upper"]
    xrange_lower = d_plot["xmax_lower"] - d_plot["xmin_lower"]
    yrange_lower = d_plot["ymax_lower"] - d_plot["ymin_lower"]
    voltage_range = d_plot["voltage_max"] - d_plot["voltage_min"]
    scans_upper, scans_lower = y_upper.shape[-1], y_lower.shape[-1]
    if scans_upper <= 10:
        base_scan_upper = 1
    elif 10 < scans_upper <= 20:
        base_scan_upper = 2
    elif 20 < scans_upper <= 50:
        base_scan_upper = 5
    else:
        base_scan_upper = 10
    if xrange_upper <= 10:
        base_scatt_upper = 1
    elif 10 < xrange_upper <= 20:
        base_scatt_upper = 2
    elif 20 < xrange_upper <= 50:
        base_scatt_upper = 5
    else:
        base_scatt_upper = 10
    if scans_lower <= 10:
        base_scan_lower = 1
    elif 10 < scans_lower <= 20:
        base_scan_lower = 2
    elif 20 < scans_lower <= 50:
        base_scan_lower = 5
    else:
        base_scan_lower = 10
    if xrange_lower <= 10:
        base_scatt_lower = 1
    elif 10 < xrange_lower <= 20:
        base_scatt_lower = 2
    elif 20 < xrange_lower <= 50:
        base_scatt_lower = 5
    else:
        base_scatt_lower = 10
    if time_max <= 10:
        base_time = 1
    elif 10 < time_max <= 20:
        base_time = 2
    elif 20 < time_max <= 50:
        base_time = 5
    else:
        base_time = 10
    if voltage_range <= 0.5:
        base_voltage = 0.1
    elif 0.5 < voltage_range <= 1:
        base_voltage = 0.2
    elif 1 < d_plot["voltage_max"] <= 4:
        base_voltage = 0.5
    else:
        base_voltage = 1
    xmin_index_upper, xmax_index_upper = None, None
    xmin_index_lower, xmax_index_lower = None, None
    for i in range(0, len(x_upper)):
        if d_plot["xmin_upper"] <= x_upper[i]:
            xmin_index_upper = i
            break
    if isinstance(xmin_index_upper, type(None)):
        xmin_index_upper = 0
    for i in range(xmin_index_upper + 1, len(x_upper)):
        if d_plot["xmax_upper"] <= x_upper[i]:
            xmax_index_upper = i
            break
    if isinstance(xmax_index_upper, type(None)):
        xmax_index_upper = len(x_upper)
    for i in range(0, len(x_lower)):
        if d_plot["xmin_lower"] <= x_lower[i]:
            xmin_index_lower = i
            break
    if isinstance(xmin_index_lower, type(None)):
        xmin_index_lower = 0
    for i in range(xmin_index_lower + 1, len(x_lower)):
        if d_plot["xmax_lower"] <= x_lower[i]:
            xmax_index_lower = i
            break
    if isinstance(xmax_index_lower, type(None)):
        xmax_index_lower = len(x_lower)
    y_upper = y_upper[xmin_index_upper:xmax_index_upper,:]
    y_lower = y_lower[xmin_index_lower:xmax_index_lower,:]
    if not isinstance(PLOT_STYLE, type(None)):
        plt.style.use(bg_mpl_style)
    fig = plt.figure(dpi=d_plot["dpi"], figsize=d_plot["figsize"])
    gs = GridSpec(nrows=3,
                  ncols=2,
                  figure=fig,
                  width_ratios=[1, 0.1375],
                  height_ratios=[1, 1, 0.4],
                  hspace=d_plot["hspace"])
    ax0 = fig.add_subplot(gs[0,:])
    ax1 = fig.add_subplot(gs[1,:])
    ax2 = fig.add_subplot(gs[2,0])
    im_upper = ax0.imshow(y_upper,
                          interpolation="nearest",
                          aspect="auto",
                          origin="upper",
                          vmin=d_plot["ymin_upper"],
                          vmax=d_plot["ymax_upper"],
                          extent=(time_min, time_max, d_plot["xmax_upper"], d_plot["xmin_upper"]),
                          cmap=d_plot["cmap_upper"])
    cbar_ticks_upper = np.linspace(d_plot["ymin_upper"], d_plot["ymax_upper"], d_plot["cbar_ticks_upper"])
    cbar_0 = ax0.figure.colorbar(im_upper, ax=ax0, ticks=cbar_ticks_upper)
    if d_plot["ymax_upper"] > 100:
        cbar_0.formatter.set_powerlimits((0, 0))
    cbar_0.set_label(label=d_plot["ylabel_upper"], size=d_plot["fontsize_labels"])
    ax0.set_xlabel(d_plot["timelabel"], fontsize=d_plot["fontsize_labels"])
    ax0.xaxis.set_label_position("top")
    ax0.tick_params(axis="x",
                    labelbottom=False,
                    labeltop=True,
                    labelsize=d_plot["fontsize_ticks"])
    ax0.set_ylabel(d_plot["xlabel_upper"])
    ax0.xaxis.set_major_locator(ticker.MultipleLocator(base_scan_upper))
    ax0.xaxis.set_minor_locator(ticker.MultipleLocator(base_scan_upper / d_plot["minor_tick_index_upper"]))
    ax0.yaxis.set_major_locator(ticker.MultipleLocator(base_scatt_upper))
    ax0.yaxis.set_minor_locator(ticker.MultipleLocator(base_scatt_upper / d_plot["minor_tick_index_upper"]))
    im_lower = ax1.imshow(y_lower,
                             interpolation="nearest",
                             aspect="auto",
                             origin="upper",
                             vmin=d_plot["ymin_lower"],
                             vmax=d_plot["ymax_lower"],
                             extent=(time_min, time_max, d_plot["xmax_lower"], d_plot["xmin_lower"]),
                             cmap=d_plot["cmap_lower"])
    cbar_ticks_lower = np.linspace(d_plot["ymin_lower"], d_plot["ymax_lower"], d_plot["cbar_ticks_lower"])
    cbar_1 = ax1.figure.colorbar(im_lower, ax=ax1, ticks=cbar_ticks_lower)
    cbar_1.set_label(label=d_plot["ylabel_lower"], size=d_plot["fontsize_labels"])
    if d_plot["ymax_lower"] > 100:
        cbar_1.formatter.set_powerlimits((0, 0))
    ax1.set_ylabel(d_plot["xlabel_lower"], fontsize=d_plot["fontsize_labels"])
    ax1.tick_params(axis="x",
                    labelbottom=False,
                    labeltop=False)
    ax1.xaxis.set_major_locator(ticker.MultipleLocator(base_scan_lower))
    ax1.xaxis.set_minor_locator(ticker.MultipleLocator(base_scan_lower / d_plot["minor_tick_index_lower"]))
    ax1.yaxis.set_major_locator(ticker.MultipleLocator(base_scatt_lower))
    ax1.yaxis.set_minor_locator(ticker.MultipleLocator(base_scatt_lower / d_plot["minor_tick_index_lower"]))
    ax21 = ax2.twiny()
    ax21.plot(time, voltage, lw=d_plot["linewidth"])
    ax21.set_xlim(time_min, time_max)
    ax2.set_xlim(time_min, time_max)
    ax21.set_ylim(d_plot["voltage_min"], d_plot["voltage_max"])
    ax2.set_ylim(d_plot["voltage_min"], d_plot["voltage_max"])
    # ax21.set_xlabel(d_plot["timelabel"], fontsize=d_plot["fontsize_labels"])
    # ax21.set_ylabel(d_plot["voltagelabel"], fontsize=d_plot["fontsize_labels"])
    ax21.xaxis.set_major_locator(ticker.MultipleLocator(base_time))
    ax21.xaxis.set_minor_locator(ticker.MultipleLocator(base_time / d_plot["minor_tick_index_echem"]))
    ax21.yaxis.set_major_locator(ticker.MultipleLocator(base_voltage))
    ax21.yaxis.set_minor_locator(ticker.MultipleLocator(base_voltage / d_plot["minor_tick_index_echem"]))
    ax21.tick_params(axis="x",
                    labelbottom=False,
                    labeltop=False,
                    # labelsize=d_plot["fontsize_ticks"]
                    )
    ax2.set_xticks(t_xticks)
    ax2.set_xticklabels(xticks_labels)
    ax2.set_xlabel(d_plot["xlabel"], fontsize=d_plot["fontsize_labels"])
    ax2.set_ylabel(d_plot["voltagelabel"], fontsize=d_plot["fontsize_labels"])
    ax2.xaxis.set_tick_params(labelsize=d_plot["fontsize_ticks"])
    ax2.yaxis.set_tick_params(labelsize=d_plot["fontsize_ticks"])
    if not isinstance(VLINES_ECHEM, type(None)):
        ax21.axvline(x=0.987*t_changes[0], ls="--", c="k", lw=2, zorder=1)
        ax21.axvline(x=0.9925*t_changes[1], ls="--", c="k", lw=2, zorder=1)
        # for t in t_changes:
        #     ax11.axvline(x=t, ls="--", c="k", lw=2, zorder=1)
    # scan_time = np.array([i * (time_range / (scatt_array.shape[1] - 1))
    #                       for i in range(scatt_array.shape[1])])
    for p in output_paths:
        plt.savefig(p / f"xy_overview_stack_echem.{p.name}",
                    bbox_inches="tight")
    plt.close()

    return None


def main():
    data_upper = Path.cwd() / "data_upper"
    data_lower = Path.cwd() / "data_lower"
    data_echem = Path.cwd() / "data_echem"
    data_paths = [data_upper, data_lower, data_echem]
    exit = None
    for p in data_paths:
        if not p.exists():
            p.mkdir()
            print(f"{80*'-'}\nA folder called '{p.name}' has been created.")
            if p.name in ["data_upper", "data_lower"]:
                print(f"Please place your xy data files for the "
                      f"{p.name.split('_')[-1]} xy overview plot in the\n"
                      f"'{p.name}' folder and rerun the program.")
            elif p.name == "data_echem":
                print(f"Please place your echem data file in the '{p.name}' "
                      f"folder and rerun the\nprogram.")
            exit = True
    if exit is True:
        sys.exit()
    data_upper_files = list(data_upper.glob("*.*"))
    data_lower_files = list(data_lower.glob("*.*"))
    data_echem_files = list(data_echem.glob("*.*"))
    file_lists = [data_upper_files, data_lower_files, data_echem_files]
    for i in range(len(file_lists)):
        if len(file_lists[i]) == 0:
            print(f"{80*'-'}\nNo files were found in the "
                  f"'{data_paths[i].name}' folder. Please place the proper "
                  f"data\nfile(s) in the '{data_paths[i].name}' folder and "
                  f"rerun the code.")
            exit = True
    if exit is True:
        sys.exit()
    data_upper_exts, data_lower_exts, data_echem_exts = [], [], []
    for e in data_upper_files:
        if not e.suffix in data_upper_exts:
            data_upper_exts.append(e.suffix)
    for e in data_lower_files:
        if not e.suffix in data_lower_exts:
            data_lower_exts.append(e.suffix)
    if len(data_upper_exts) > 1:
        print(f"{80*'-'}\nMore than one file extension was found in the "
              f"'{data_upper.name}' folder: ")
        for e in data_upper_exts:
            print(f"\t{e}")
        exit = True
    if len(data_lower_exts) > 1:
        print(f"{80*'-'}\nMore than one file extension was found in the "
              f"'{data_lower.name}' folder: ")
        for e in data_lower_exts:
            print(f"\t{e}")
        exit = True
    if len(data_echem_files) > 1:
        print(f"{80*'-'}\nMore than one file was found in the "
              f"'{data_echem.name}' folder: ")
        for e in data_echem_files:
            print(f"\t{e.name}")
        exit = True
    if exit is True:
        print(f"{80*'-'}\nPlease review the relevant data folder(s) and rerun "
              f"the program.")
        sys.exit()
    print(f"{80*'-'}\nStacking xy data for upper plot...")
    d_upper = xy_stack(data_upper_files)
    print(f"{80*'-'}\nStacking xy data for lower plot...")
    d_lower = xy_stack(data_lower_files)
    echem_file = data_echem_files[0]
    print(f"{80*'-'}\nCollecting electrochemical data...\n\t{echem_file.name}")
    d_echem = echem_load(echem_file)
    d_echem = x_from_dict_calculate(d_echem)
    # data_dict = dict(x_upper = x_upper,
    #                  y_upper = y_upper,
    #                  x_lower = x_lower,
    #                  y_lower = y_lower,
    #                  time = time_voltage[:,0],
    #                  voltage = time_voltage[:,1]
    #                  )
    output_paths = [Path.cwd() / "pdf",
                    Path.cwd() / "png",
                    Path.cwd() / "svg"]
    for p in output_paths:
        if not p.exists():
            p.mkdir()
    print(f"{80*'-'}\nMaking plot with stacked overview plots and echem...")
    xy_overview_stack_echem(d_upper, d_lower, d_echem, PLOT_DICT, output_paths)
    output_folders = [p.name for p in output_paths]
    print(f"Done plotting.\n{80*'-'}\nPlease see the {output_folders} folders.")

    return None


if __name__ == "__main__":
    main()

# End of file.
