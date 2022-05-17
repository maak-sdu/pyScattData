import sys
from pathlib import Path
import numpy as np
from diffpy.utils.parsers.loaddata import loadData
from scipy.constants import physical_constants
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.gridspec import GridSpec
from matplotlib.colors import LinearSegmentedColormap
try:
    PLOT_STYLE = True
    from bg_mpl_stylesheet.bg_mpl_stylesheet import bg_mpl_style
except ImportError:
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

# Inputs for plots
DPI = 600
FIGSIZE = (8,8)
FONTSIZE_LABELS = 20
FONTSIZE_TICKS = 14
HSPACE = 0.1

XLABEL = "$x$ in Li$_{x}$TiO$_{2}$"
TIMELABEL = "$t$ $[\mathrm{h}]$"
VOLTAGELABEL = r"$E_{\mathrm{we}}$ vs." + "\n" + r"Li/Li$^{+} [\mathrm{V}]$"

SCATT_XMIN = 1
SCATT_XMAX = 10
SCATT_XLABEL = r"$r$ $[\mathrm{\AA}]$"
SCATT_YLABEL = r"$G$ $[\mathrm{\AA}^{-2}]$"
CMAP = "seismic"
my_gradient = LinearSegmentedColormap.from_list('my_gradient', (
                 # Edit this gradient at https://eltos.github.io/gradient/#0B3C5D-0B3C5D-FFFFFF-B82601-B82601
                 (0.000, (0.043, 0.235, 0.365)),
                 (0.250, (0.200, 0.400, 0.500)),
                 (0.500, (1.000, 1.000, 1.000)),
                 (0.750, (0.850, 0.200, 0.100)),
                 (1.000, (0.722, 0.149, 0.004))))
CMAP = my_gradient
CUSTOM_CMAP = False
RGB_START = (11, 60, 93)
RGB_END = (184, 38, 1)

CBAR_MIN = -0.8
CBAR_MAX = 0.8
CBAR_TICKS = 9


MAJOR_TICK_INDEX_TIME = 5
MAJOR_TICK_INDEX_VOLTAGE = 0.5
MAJOR_TICK_INDEX_SCATT_X = 1

VOLTAGE_LIMITS = True
VOLTAGE_MIN = 1
VOLTAGE_MAX = 3
BREAKFACTOR_X = 0.04
BREAKFACTOR_Y = 0.04
TOLERANCE_FACTOR = 10**2


def diverging_cmap_generate(rgb_start, rgb_end):
    N = 256
    vals_blue = np.ones((N, 4))
    for i in range(len(RGB_START)):
        vals_blue[:, i] = np.linspace(RGB_START[i] / 256, 1, N)
    cmap_blue = ListedColormap(vals_blue)
    vals_red = np.ones((N, 4))
    for i in range(len(RGB_END)):
        vals_red[:, i] = np.flip(np.linspace(RGB_END[i] / 256, 1, N), axis=0)
    cmap_red = ListedColormap(vals_red)
    newcolors = np.vstack((cmap_blue(np.linspace(0, 1, N)),
                           cmap_red(np.linspace(0, 1, N))
                           ))
    cmap = ListedColormap(newcolors, name="BGBlueRed")

    return cmap


def dict_echem_extract(echem_file):
    d = {}
    data = loadData(echem_file)
    d["time"] = data[:,INDEX_TIME]
    d["voltage"] = data[:,INDEX_VOLTAGE]
    d["current"] = data[:,INDEX_CURRENT]

    return d


def x_from_dict_calcualte(d):
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


def dict_scatt_extract(scatt_files):
    d = {}
    for i in range(len(scatt_files)):
        d[i] = {}
        data = loadData(scatt_files[i])
        d[i]["x"] = data[:,0]
        d[i]["y"] = data[:,1]

    return d


def array_from_dict(d):
    keys = list(d.keys())
    x = d[keys[0]]["x"]
    xmin_index, xmax_index = None, None
    for i in range(0, len(x)):
        if SCATT_XMIN <= x[i]:
            xmin_index = i
            break
    if isinstance(xmin_index, type(None)):
        xmin_index = 0
    for i in range(xmin_index + 1, len(x)):
        if SCATT_XMAX <= x[i]:
            xmax_index = i
            break
    if isinstance(xmax_index, type(None)):
        xmax_index = len(x)
    for i in range(len(keys)):
        if i == 0:
            array = d[keys[i]]["y"]
        else:
            array = np.column_stack((array, d[keys[i]]["y"]))
    array = array[xmin_index:xmax_index,:]

    return array


def scatt_echem_plot(d_echem, scatt_array, output_folders):
    time = d_echem["time"]
    voltage = d_echem["voltage"]
    current = d_echem["current"]
    x = d_echem["x"]
    change_indices = d_echem["change_indices"]
    t_changes = [time[e] for e in change_indices]
    t_changes_labels = [f"{x[e]:.2f}" for e in change_indices]
    xticks_labels = [f"{e:.1f}" for e in np.arange(0, 0.8, 0.2)]
    xticks_labels.append(t_changes_labels[0])
    for e in np.arange(0.7, 0.3, -0.2):
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
    voltage_min, voltage_max = np.amin(voltage), np.amax(voltage)
    if not isinstance(PLOT_STYLE, type(None)):
        plt.style.use(bg_mpl_style)
    if CUSTOM_CMAP is True:
        cmap = diverging_cmap_generate(RGB_START, RGB_END)
    else:
        cmap = CMAP
    fig = plt.figure(dpi=DPI, figsize=FIGSIZE)
    gs = GridSpec(nrows=2,
                  ncols=2,
                  figure=fig,
                  width_ratios=[1, 0.1375],
                  height_ratios=[1, 0.4],
                  hspace=HSPACE,
                  )
    ax1 = fig.add_subplot(gs[1,0])
    ax11 = ax1.twiny()
    ax11.plot(time, voltage)
    ax1.set_xlim(time_min, time_max)
    ax11.set_xlim(time_min, time_max)
    if VOLTAGE_LIMITS is True:
        ax1.set_ylim(VOLTAGE_MIN, VOLTAGE_MAX)
        ax11.set_ylim(VOLTAGE_MIN, VOLTAGE_MAX)
        voltage_range = VOLTAGE_MAX - VOLTAGE_MIN
    else:
        ax1.set_ylim(voltage_min, voltage_max)
        ax11.set_ylim(voltage_min, voltage_max)
        voltage_range = voltage_max - voltage_min
    # ax1.set_xlabel(XLABEL)
    ax11.set_ylabel(VOLTAGELABEL, fontsize=FONTSIZE_LABELS)
    ax11.xaxis.set_label_position("top")
    ax11.tick_params(axis="x",
                    labelbottom=False,
                    labeltop=False,
                    labelsize=FONTSIZE_TICKS)
    ax11.xaxis.set_major_locator(MultipleLocator(MAJOR_TICK_INDEX_TIME))
    ax11.xaxis.set_minor_locator(MultipleLocator(MAJOR_TICK_INDEX_TIME / 5))
    ax11.yaxis.set_major_locator(MultipleLocator(MAJOR_TICK_INDEX_VOLTAGE))
    ax11.yaxis.set_minor_locator(MultipleLocator(MAJOR_TICK_INDEX_VOLTAGE / 5))
    ax1.set_xticks(t_xticks)
    ax1.set_xticklabels(xticks_labels)
    ax1.set_xlabel(XLABEL, fontsize=FONTSIZE_LABELS)
    ax1.set_ylabel(VOLTAGELABEL, fontsize=FONTSIZE_LABELS)
    ax1.xaxis.set_tick_params(labelsize=FONTSIZE_TICKS)
    ax1.yaxis.set_tick_params(labelsize=FONTSIZE_TICKS)
    for i in range(len(t_changes)):
        plt.text(t_changes[i] - BREAKFACTOR_X * time_range,
                 voltage_min - BREAKFACTOR_Y * voltage_range,
                 "|",
                 rotation=45)
    scan_time = np.array([i * (time_range / (scatt_array.shape[1] - 1))
                          for i in range(scatt_array.shape[1])])
    ax0 = fig.add_subplot(gs[0,:],
                          # sharex=ax11,
                          )
    im = ax0.imshow(scatt_array,
                    interpolation="nearest",
                    aspect="auto",
                    origin="upper",
                    vmin=CBAR_MIN,
                    vmax=CBAR_MAX,
                    extent=(0, np.amax(scan_time), SCATT_XMAX, SCATT_XMIN),
                    cmap=cmap,
                    )
    # ax0.set_xlim(0, scatt_array.shape[1])
    ax0.set_xlabel(TIMELABEL, fontsize=FONTSIZE_LABELS)
    ax0.xaxis.set_label_position("top")
    ax0.tick_params(axis="x",
                    labelbottom=False,
                    labeltop=True,
                    labelsize=FONTSIZE_TICKS)
    ax0.set_ylabel(SCATT_XLABEL, fontsize=FONTSIZE_LABELS)
    cbar_ticks = np.linspace(CBAR_MIN, CBAR_MAX, CBAR_TICKS)
    cbar = ax0.figure.colorbar(im, ax=ax0, ticks=cbar_ticks)
    if CBAR_MAX > 100:
        cbar.formatter.set_powerlimits((0, 0))
    cbar.set_label(label=SCATT_YLABEL, size=FONTSIZE_LABELS)
    ax0.xaxis.set_major_locator(MultipleLocator(MAJOR_TICK_INDEX_TIME))
    ax0.xaxis.set_minor_locator(MultipleLocator(MAJOR_TICK_INDEX_TIME / 5))    
    ax0.yaxis.set_major_locator(MultipleLocator(MAJOR_TICK_INDEX_SCATT_X))
    ax0.yaxis.set_minor_locator(MultipleLocator(MAJOR_TICK_INDEX_SCATT_X / 5))
    for f in output_folders:
        plt.savefig(f"{f}/stackplot_scatt_echem_t_x_v.{f}", bbox_inches="tight")
    plt.close()

    return None


def main():
    data_scatt_path = Path.cwd() / "data_scatt"
    data_echem_path = Path.cwd() / "data_echem"
    data_paths = [data_scatt_path, data_echem_path]
    exit = False
    for p in data_paths:
        if not p.exists():
            p.mkdir()
            print(f"{80*'-'}\nA folder called '{p.name}' has been created.")
            exit = True
    if exit is True:
        print(f"{80*'-'}\nPlease place your data files in the proper data "
              f"folder and rerun the program.\n{80*'-'}")
        sys.exit()
    data_scatt_files = list(data_scatt_path.glob("*.*"))
    data_echem_files = list(data_echem_path.glob("*.*"))
    data_files = [data_scatt_files, data_echem_files]
    for i in range(len(data_files)):
        if len(data_files[i]) == 0:
            print(f"{80*'-'}\nNo files found in the '{data_paths[i].name}' "
                  f"folder.")
            exit = True
    if exit is True:
        print(f"{80*'-'}\nPlease place your data files in the proper data "
              f"folder and rerun the program.\n{80*'-'}")
    d_echem = dict_echem_extract(data_echem_files[0])
    d_echem = x_from_dict_calcualte(d_echem)
    d_scatt = dict_scatt_extract(data_scatt_files)
    scatt_array = array_from_dict(d_scatt)
    output_folders = ["pdf", "png", "svg"]
    for f in output_folders:
        if not (Path.cwd() / f).exists():
            (Path.cwd() / f).mkdir()
    scatt_echem_plot(d_echem, scatt_array, output_folders)

    return None


if __name__ == "__main__":
    main()

# End of file.
