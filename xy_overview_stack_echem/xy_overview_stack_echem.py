import sys
from pathlib import Path
from diffpy.utils.parsers.loaddata import loadData
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.gridspec import GridSpec
try:
    from bg_mpl_stylesheet.bg_mpl_stylesheet import bg_mpl_style
    PLOT_STYLE = "found"
except ModuleNotFoundError:
    PLOT_STYLE = None

PLOT_DICT = dict(dpi = 600,
                        figsize = (8,10),
                        fontsize_labels = 20,
                        fontsize_ticks = 16,
                        xmin_upper = 1,
                        xmax_upper = 10,
                        ymin_upper = -1,
                        ymax_upper = 1,
                        xmin_lower = 10,
                        xmax_lower = 20,
                        ymin_lower = -0.25,
                        ymax_lower = 0.25,
                        voltage_min = 1,
                        voltage_max = 3,
                        index_label = "Scan Number",
                        xlabel_upper = r"$r$ $[\mathrm{\AA}]$",
                        ylabel_upper = r"$G$ $[\mathrm{\AA}^{-2}]$",
                        xlabel_lower = r"$r$ $[\mathrm{\AA}]$",
                        ylabel_lower = r"$G$ $[\mathrm{\AA}^{-2}]$",
                        time_label = r"$t$ $[\mathrm{h}]$",
                        voltage_label = r"$E_{\mathrm{we}}$ vs." + "\n" + r"Li/Li$^{+} [\mathrm{V}]$",
                        minor_tick_index_upper = 5,
                        minor_tick_index_lower = 5,
                        minor_tick_index_echem = 5,
                        cmap_upper = "seismic",
                        cmap_lower = "seismic",
                        cbar_ticks_upper = 5,
                        cbar_ticks_lower = 5,
                        color = "k",
                        linewidth = 1)
LABEL_DICT = {"gr": dict(x = r"$r$ $[\mathrm{\AA}]$",
                         y = r"$G$ $[\mathrm{\AA}^{-2}]$"),
              "fq[Å^-1]": dict(x = r"$Q$ $[\mathrm{\AA}^{-1}]$",
                               y = r"$F$ $[\mathrm{\AA}^{-1}]$"),
              "fq[nm^-1]": dict(x = r"$Q$ $[\mathrm{nm}^{-1}]$",
                                y = r"$F$ $[\mathrm{\nm}^{-1}]$"),
              "sq[Å^-1]": dict(x = r"$Q$ $[\mathrm{\AA}^{-1}]$",
                               y = r"$S$ $[\mathrm{arb. u.}]$"),
              "sq[nm^-1]": dict(x = r"$Q$ $[\mathrm{nm}^{-1}]$",
                                y = r"$S$ $[\mathrm{arb. u.}]$"),
              "iq[Å^-1]": dict(x = r"$Q$ $[\mathrm{\AA}^{-1}]$",
                               y = r"$I$ $[\mathrm{arb. u.}]$"),
              "iq[nm^-1]": dict(x = r"$Q$ $[\mathrm{nm}^{-1}]$",
                                y = r"$I$ $[\mathrm{arb. u.}]$"),
              "iq[2theta]": dict(x = r"$2\theta$ $[\degree]$",
                                 y = r"$I$ $[\mathrm{arb. u.}]$"),
              "xy": dict(x = r"$x$",
                         y = r"$y$")
             }

DPI = 600
FIGSIZE = (8,10)
FONTSIZE_LABELS = 20
FONTSIZE_TICKS = 16
XMIN_UPPER = 1
XMAX_UPPER = 10
YMIN_UPPER = -1
YMAX_UPPER = 1
XMIN_LOWER = 10
XMAX_LOWER = 20
YMIN_LOWER = -0.25
YMAX_LOWER = 0.25
VOLTAGE_MIN = 1
VOLTAGE_MAX = 3
INDEXLABEL = "Scan Number"
XLABEL_UPPER = r"$r$ $[\mathrm{\AA}]$"
YLABEL_UPPER = r"$G$ $[\mathrm{\AA}^{-2}]$"
XLABEL_LOWER = r"$r$ $[\mathrm{\AA}]$"
YLABEL_LOWER = r"$G$ $[\mathrm{\AA}^{-2}]$"
TIMELABEL = r"$t$ $[\mathrm{h}]$"
VOLTAGELABEL = r"$E_{\mathrm{we}}$ vs." + "\n" + r"Li/Li$^{+} [\mathrm{V}]$"
MINOR_TICK_INDEX_UPPER = 5
MINOR_TICK_INDEX_LOWER = 5
MINOR_TICK_INDEX_ECHEM = 5
CMAP_UPPER = "seismic"
CMAP_LOWER = "seismic"
CBAR_TICKS_UPPER = 5
CBAR_TICKS_LOWER = 5
COLOR = "k"
LINEWIDTH = 1


def xy_stack(data_files):
    for i in range(len(data_files)):
        print(f"\t{data_files[i].name}")
        xy = loadData(str(data_files[i]))
        x, y = xy[:,0], xy[:,1]
        if i == 0:
            y_array = y
        else:
            y_array = np.column_stack((y_array, y))

    return x, y_array


def xy_overview_stack_echem(d, output_paths):
    x_upper, y_upper = d["x_upper"], d["y_upper"] #np.flip(d["y_upper"], axis=[0])
    x_lower, y_lower = d["x_lower"], d["y_lower"] #np.flip(d["y_lower"], axis=[0])
    time, voltage = d["time"], d["voltage"]
    # xmin_upper, xmax_upper = np.amin(x_upper), np.amax(x_upper)
    # ymin_upper, ymax_upper = np.amin(y_upper), np.amax(y_upper)
    # xmin_lower, xmax_lower = np.amin(x_lower), np.amax(x_lower)
    # ymin_lower, ymax_lower = np.amin(y_lower), np.amax(y_lower)
    time_min, time_max = np.amin(time), np.amax(time)
    # voltage_min, voltage_max = np.amin(voltage), np.amax(voltage)
    scans_upper, scans_lower = y_upper.shape[-1], y_lower.shape[-1]
    xrange_upper = XMAX_UPPER - XMIN_UPPER
    yrange_upper = YMAX_UPPER - YMIN_UPPER
    xrange_lower = XMAX_LOWER - XMIN_LOWER
    yrange_lower = YMAX_LOWER - YMIN_LOWER
    voltage_range = VOLTAGE_MAX - VOLTAGE_MIN
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
    elif 1 < VOLTAGE_MAX <= 3:
        base_voltage = 0.5
    else:
        base_voltage = 1
    # fig, axs = plt.subplots(dpi=DPI, figsize=FIGSIZE, ncols=1, nrows=3,
    #                         gridspec_kw={"height_ratios": [1, 1, 0.25]})
    # im_upper = axs[0].imshow(y_upper,
    #                          interpolation="nearest",
    #                          aspect="auto",
    #                          origin="upper",
    #                          vmin=ymin_upper,
    #                          vmax=ymax_upper,
    #                          extent=(0, scans_upper, xmax_upper, xmin_upper),
    #                          cmap=CMAP_UPPER)
    # cbar_ticks_upper = np.linspace(ymin_upper, ymax_upper, CBAR_TICKS_UPPER)
    # cbar_0 = axs[0].figure.colorbar(im_upper, ax=axs[0], ticks=cbar_ticks_upper)
    # if ymax_upper > 100:
    #     cbar_0.formatter.set_powerlimits((0, 0))
    # im_lower = axs[1].imshow(y_lower,
    #                          interpolation="nearest",
    #                          aspect="auto",
    #                          origin="upper",
    #                          vmin=ymin_lower,
    #                          vmax=ymax_lower,
    #                          extent=(0, scans_lower, xmax_lower, xmin_lower),
    #                          cmap=CMAP_LOWER)
    # cbar_ticks_lower = np.linspace(ymin_lower, ymax_lower, CBAR_TICKS_LOWER)
    # cbar_1 = axs[0].figure.colorbar(im_lower, ax=axs[1], ticks=cbar_ticks_lower)
    # if ymax_lower > 100:
    #     cbar_1.formatter.set_powerlimits((0, 0))
    # axs[2].plot(time, voltage, c=COLOR, lw=LINEWIDTH)
    # axs[2].set_xlim(time_min, time_max)
    # axs[2].set_aspect()
    # for p in output_paths:
    #     plt.savefig(p / f"xy_overview_stack_echem.{p.name}",
    #                 bbox_inches="tight")
    xmin_index_upper, xmax_index_upper = None, None
    xmin_index_lower, xmax_index_lower = None, None
    for i in range(0, len(x_upper)):
        if XMIN_UPPER <= x_upper[i]:
            xmin_index_upper = i
            break
    if isinstance(xmin_index_upper, type(None)):
        xmin_index_upper = 0
    for i in range(xmin_index_upper + 1, len(x_upper)):
        if XMAX_UPPER <= x_upper[i]:
            xmax_index_upper = i
            break
    if isinstance(xmax_index_upper, type(None)):
        xmax_index_upper = len(x_upper)
    for i in range(0, len(x_lower)):
        if XMIN_LOWER <= x_lower[i]:
            xmin_index_lower = i
            break
    if isinstance(xmin_index_lower, type(None)):
        xmin_index_lower = 0
    for i in range(xmin_index_lower + 1, len(x_lower)):
        if XMAX_LOWER <= x_lower[i]:
            xmax_index_lower = i
            break
    if isinstance(xmax_index_lower, type(None)):
        xmax_index_lower = len(x_lower)
    y_upper = y_upper[xmin_index_upper:xmax_index_upper,:]
    y_lower = y_lower[xmin_index_lower:xmax_index_lower,:]
    if not isinstance(PLOT_STYLE, type(None)):
        plt.style.use(bg_mpl_style)
    fig = plt.figure(dpi=DPI, figsize=FIGSIZE)
    gs = GridSpec(nrows=3,
                  ncols=2,
                  figure=fig,
                  width_ratios=[1, 0.1375],
                  height_ratios=[1, 1, 0.4],
                  hspace=0.1)
    ax0 = fig.add_subplot(gs[0,:])
    ax1 = fig.add_subplot(gs[1,:])
    ax2 = fig.add_subplot(gs[2,0])
    im_upper = ax0.imshow(y_upper,
                             interpolation="nearest",
                             aspect="auto",
                             origin="upper",
                             vmin=YMIN_UPPER,
                             vmax=YMAX_UPPER,
                             extent=(0, scans_upper, XMAX_UPPER, XMIN_UPPER),
                             cmap=CMAP_UPPER)
    cbar_ticks_upper = np.linspace(YMIN_UPPER, YMAX_UPPER, CBAR_TICKS_UPPER)
    cbar_0 = ax0.figure.colorbar(im_upper, ax=ax0, ticks=cbar_ticks_upper)
    if YMAX_UPPER > 100:
        cbar_0.formatter.set_powerlimits((0, 0))
    cbar_0.set_label(label=YLABEL_UPPER, size=FONTSIZE_LABELS)
    ax0.set_xlabel(INDEXLABEL, fontsize=FONTSIZE_LABELS)
    ax0.xaxis.set_label_position("top")
    ax0.tick_params(axis="x",
                    labelbottom=False,
                    labeltop=True,
                    labelsize=FONTSIZE_TICKS)
    ax0.set_ylabel(XLABEL_UPPER)
    ax0.xaxis.set_major_locator(ticker.MultipleLocator(base_scan_upper))
    ax0.xaxis.set_minor_locator(ticker.MultipleLocator(base_scan_upper / MINOR_TICK_INDEX_UPPER))
    ax0.yaxis.set_major_locator(ticker.MultipleLocator(base_scatt_upper))
    ax0.yaxis.set_minor_locator(ticker.MultipleLocator(base_scatt_upper / MINOR_TICK_INDEX_UPPER))
    im_lower = ax1.imshow(y_lower,
                             interpolation="nearest",
                             aspect="auto",
                             origin="upper",
                             vmin=YMIN_LOWER,
                             vmax=YMAX_LOWER,
                             extent=(0, scans_lower, XMAX_LOWER, XMIN_LOWER),
                             cmap=CMAP_LOWER)
    cbar_ticks_lower = np.linspace(YMIN_LOWER, YMAX_LOWER, CBAR_TICKS_LOWER)
    cbar_1 = ax1.figure.colorbar(im_lower, ax=ax1, ticks=cbar_ticks_lower)
    cbar_1.set_label(label=YLABEL_LOWER, size=FONTSIZE_LABELS)
    if YMAX_LOWER > 100:
        cbar_1.formatter.set_powerlimits((0, 0))
    ax1.set_ylabel(XLABEL_LOWER, fontsize=FONTSIZE_LABELS)
    ax1.tick_params(axis="x",
                    labelbottom=False,
                    labeltop=False)
    ax1.xaxis.set_major_locator(ticker.MultipleLocator(base_scan_lower))
    ax1.xaxis.set_minor_locator(ticker.MultipleLocator(base_scan_lower / MINOR_TICK_INDEX_LOWER))
    ax1.yaxis.set_major_locator(ticker.MultipleLocator(base_scatt_lower))
    ax1.yaxis.set_minor_locator(ticker.MultipleLocator(base_scatt_lower / MINOR_TICK_INDEX_LOWER))
    ax2.plot(time, voltage, c=COLOR, lw=LINEWIDTH)
    ax2.set_xlim(time_min, time_max)
    ax2.set_ylim(VOLTAGE_MIN, VOLTAGE_MAX)
    ax2.set_xlabel(TIMELABEL, fontsize=FONTSIZE_LABELS)
    ax2.set_ylabel(VOLTAGELABEL, fontsize=FONTSIZE_LABELS)
    ax2.xaxis.set_major_locator(ticker.MultipleLocator(base_scan_lower))
    ax2.xaxis.set_minor_locator(ticker.MultipleLocator(base_scan_lower / MINOR_TICK_INDEX_ECHEM))
    ax2.yaxis.set_major_locator(ticker.MultipleLocator(base_scatt_lower))
    ax2.yaxis.set_minor_locator(ticker.MultipleLocator(base_scatt_lower / MINOR_TICK_INDEX_ECHEM))
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
    print(f"{80*'-'}\nStacking xy data for upper plot...")
    x_upper, y_upper = xy_stack(data_upper_files)
    print(f"{80*'-'}\nStacking xy data for lower plot...")
    x_lower, y_lower = xy_stack(data_lower_files)
    echem_file = data_echem_files[0]
    print(f"{80*'-'}\nCollecting electrochemical data...\n\t{echem_file.name}")
    time_voltage = np.loadtxt(echem_file)
    data_dict = dict(x_upper = x_upper,
                     y_upper = y_upper,
                     x_lower = x_lower,
                     y_lower = y_lower,
                     time = time_voltage[:,0],
                     voltage = time_voltage[:,1]
                     )
    output_paths = [Path.cwd() / "pdf",
                    Path.cwd() / "png",
                    Path.cwd() / "svg"]
    for p in output_paths:
        if not p.exists():
            p.mkdir()
    print(f"{80*'-'}\nMaking plot with stacked overview plots and echem...")
    xy_overview_stack_echem(data_dict, output_paths)
    output_folders = [p.name for p in output_paths]
    print(f"Done plotting.\n{80*'-'}\nPlease see the {output_folders} folders.")

    return None


if __name__ == "__main__":
    main()

# End of file.
