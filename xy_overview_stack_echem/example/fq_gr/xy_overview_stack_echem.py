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

DPI = 600
FIGSIZE = (8,10)
FONTSIZE_LABELS = 20
FONTSIZE_TICKS = 16
INDEXLABEL = "Scan Number"
XLABEL_UPPER = r"$Q$ $[\mathrm{\AA}^{-1}]$"
YLABEL_UPPER = r"$F$ $[\mathrm{\AA}^{-1}]$"
XLABEL_LOWER = r"$r$ $[\mathrm{\AA}]$"
YLABEL_LOWER = r"$G$ $[\mathrm{\AA}^{-2}]$"
TIMELABEL = r"$t$ $[\mathrm{h}]$"
VOLTAGELABEL = r"$E_{\mathrm{we}}$ vs." + "\n" + r"Li/Li$^{+} [\mathrm{V}]$"
MINOR_TICK_INDEX_UPPER = 5
MINOR_TICK_INDEX_LOWER = 5
CMAP_UPPER = "viridis"
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
    voltage_min, voltage_max = np.amin(voltage), np.amax(voltage)
    xmin_upper, xmax_upper = 1, 10
    ymin_upper, ymax_upper = -0.5, 1
    xmin_lower, xmax_lower = 1, 10
    ymin_lower, ymax_lower = -1, 1
    scans_upper, scans_lower = y_upper.shape[-1], y_lower.shape[-1]
    xrange_upper = xmax_upper - xmin_upper
    yrange_upper = ymax_upper - ymin_upper
    xrange_lower = xmax_lower - xmin_lower
    yrange_lower = ymax_lower - ymin_lower
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
        if xmin_upper <= x_upper[i]:
            xmin_index_upper = i
            break
    if isinstance(xmin_index_upper, type(None)):
        xmin_index_upper = 0
    for i in range(xmin_index_upper + 1, len(x_upper)):
        if xmax_upper <= x_upper[i]:
            xmax_index_upper = i
            break
    if isinstance(xmax_index_upper, type(None)):
        xmax_index_upper = len(x_upper)
    for i in range(0, len(x_lower)):
        if xmin_lower <= x_lower[i]:
            xmin_index_lower = i
            break
    if isinstance(xmin_index_lower, type(None)):
        xmin_index_lower = 0
    for i in range(xmin_index_lower + 1, len(x_lower)):
        if xmax_lower <= x_lower[i]:
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
                  width_ratios=[1, 0.14],
                  height_ratios=[1, 1, 0.4],
                  hspace=0.1)
    ax0 = fig.add_subplot(gs[0,:])
    ax1 = fig.add_subplot(gs[1,:])
    ax2 = fig.add_subplot(gs[2,0])
    im_upper = ax0.imshow(y_upper,
                             interpolation="nearest",
                             aspect="auto",
                             origin="upper",
                             vmin=ymin_upper,
                             vmax=ymax_upper,
                             extent=(0, scans_upper, xmax_upper, xmin_upper),
                             cmap=CMAP_UPPER)
    cbar_ticks_upper = np.linspace(ymin_upper, ymax_upper, CBAR_TICKS_UPPER)
    cbar_0 = ax0.figure.colorbar(im_upper, ax=ax0, ticks=cbar_ticks_upper)
    if ymax_upper > 100:
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
                             vmin=ymin_lower,
                             vmax=ymax_lower,
                             extent=(0, scans_lower, xmax_lower, xmin_lower),
                             cmap=CMAP_LOWER)
    cbar_ticks_lower = np.linspace(ymin_lower, ymax_lower, CBAR_TICKS_LOWER)
    cbar_1 = ax1.figure.colorbar(im_lower, ax=ax1, ticks=cbar_ticks_lower)
    cbar_1.set_label(label=YLABEL_LOWER, size=FONTSIZE_LABELS)
    if ymax_lower > 100:
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
    ax2.set_xlabel(TIMELABEL, fontsize=FONTSIZE_LABELS)
    ax2.set_ylabel(VOLTAGELABEL, fontsize=FONTSIZE_LABELS)
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
    x_upper, y_upper = xy_stack(data_upper_files)
    x_lower, y_lower = xy_stack(data_lower_files)
    time_voltage = np.loadtxt(data_echem_files[0])
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
    xy_overview_stack_echem(data_dict, output_paths)

    return None


if __name__ == "__main__":
    main()

# End of file.
