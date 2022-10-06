import sys
from pathlib import Path
from diffpy.utils.parsers.loaddata import loadData
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from scipy.constants import physical_constants
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import LinearSegmentedColormap
from bg_mpl_stylesheet.bg_mpl_stylesheet import bg_mpl_style

# Plot inputs
DPI = 600
FIGSIZE = (8, 10)
XMIN = 1
XMAX = 10
BLANK_SCANS = {"30": 2}
GDIFF_MIN = - 0.75
GDIFF_MAX = 0.75
SCATT_XLABEL = "$r\;[\mathrm{\AA}]$"
SCATT_YLABEL = "$G_{\mathrm{diff}}\;[\mathrm{\AA}^{-2}]$"
PEARSON_LABEL = "$R_{\mathrm{Pearson}}$"
XLABEL = "$x\;\mathrm{in\;Li}_{x}\mathrm{TiO_{2}}$"
TIMELABEL = "$t\;[\mathrm{h}]$"
# VOLTAGELABEL = r"$E_{\mathrm{we}}$ vs." + "\n" + r"Li/Li$^{+} [\mathrm{V}]$"
VOLTAGELABEL = r"$E_{\mathrm{we}}\;\mathrm{vs.\;Li/Li^{+}\;[V]}$"
VOLTAGE_MIN = 1
VOLTAGE_MAX = 3
FONTSIZE_LABELS = 20
FONTSIZE_TICKS = 14
TOLERANCE_FACTOR = 10**2
VLINES_ECHEM = True

# Inputs to load echem
INDEX_TIME = 0
INDEX_VOLTAGE = 1
INDEX_CURRENT = 2

# Inputs to calculate amount of working ion transferred
WORKING_ION_CHARGE = 1
WORKING_ION_START_VALUE = 0
MOLAR_MASS = 79.866
MASS = 0.6 * 11.276 * 10**-3


CMAP = LinearSegmentedColormap.from_list('my_gradient', (
                 # Edit this gradient at https://eltos.github.io/gradient/#0B3C5D-0B3C5D-FFFFFF-B82601-B82601
                 (0.000, (0.043, 0.235, 0.365)),
                 (0.250, (0.200, 0.400, 0.500)),
                 (0.500, (1.000, 1.000, 1.000)),
                 (0.750, (0.850, 0.200, 0.100)),
                 (1.000, (0.722, 0.149, 0.004))))


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


def data_extract(files):
    data = loadData(files[0])
    x, y = data[:, 0], data[:, 1]
    y_stack = y
    for i in range(1, len(files)):
        y_stack = np.column_stack((y_stack, loadData(files[i])[:, 1]))
    d = dict(x=x, y=y_stack)

    return d


def comps_extract(file):
    data = np.loadtxt(file, skiprows=1, delimiter=",")
    x = data[:, 0]
    comps = data[:, 1:data.shape[1]]
    d = dict(x=x, comps=comps)

    return d


def weights_extract(file):
    data = np.loadtxt(file, skiprows=1, delimiter=",")
    weights = data[:, 1:]

    return weights


def linear_combine(d_comps, weights):
    x = d_comps["x"]
    comps = d_comps["comps"]
    comps_weighted = np.matmul(comps, weights)

    return comps_weighted


def extremum_indices(x, xmin, xmax):
    for i in range(len(x)):
        if x[i] >= xmin:
            xmin_index = i
            break
    for i in range(xmin_index, len(x)):
        if x[i] >= xmax:
            xmax_index = i + 1
            break
        elif i == len(x) - 1:
            xmax_index = i
            break

    return xmin_index, xmax_index


def blank_scans_insert(y, blank_scans):
    keys = [int(k) for k in blank_scans.keys()]
    blank_scan = np.zeros(y.shape[0])
    y_stack = y[:, 0]
    for i in range(1, y.shape[1]):
        if i in keys:
            for j in range(blank_scans[str(i)]):
                y_stack = np.column_stack((y_stack, blank_scan))
            y_stack = np.column_stack((y_stack, y[:, i]))
        else:
            y_stack = np.column_stack((y_stack, y[:, i]))

    return y_stack


def data_nmf_correlate(y_data, y_nmf):
    corrcoeffs = []
    for i in range(y_data.shape[1]):
        r, p = pearsonr(y_data[:, i], y_nmf[:, i])
        corrcoeffs.append(r)
    corrcoeffs = np.array(corrcoeffs)

    return corrcoeffs


def x_array_blank_scans(corrcoeffs, blank_scans):
    x = []
    keys = [int(k) for k in blank_scans.keys()]
    counter = 0
    for i in range(len(corrcoeffs)):
        if i in keys:
            for j in range(blank_scans[str(i)]):
                counter  += 1
            x.append(counter)
            counter += 1
        else:
            x.append(counter)
            counter += 1
    x = np.array(x)

    return x


def diff_plot(d, d_echem, plotpaths):
    t_changes = [d_echem["time"][e] for e in d_echem["change_indices"]]
    t_changes_labels = [f"{d_echem['x'][e]:.2f}" for e in d_echem["change_indices"]]
    xticks_labels = [f"{e:.1f}" for e in [0, 0.2, 0.4, 0.6]]
    xticks_labels.append(t_changes_labels[0])
    for e in [0.6, 0.4]:
        xticks_labels.append(f"{e:.1f}")
    xticks_labels.append(t_changes_labels[1])
    xticks_labels.append(f"{d_echem['x'][-1]:.2f}")
    t_xticks = np.array([])
    j = 0
    for i in range(0, len(d_echem["x"])):
        if np.isclose(np.array(xticks_labels[j], dtype=float),
                      d_echem["x"][i],
                      atol=abs(d_echem["x"][0] - d_echem["x"][1]) * TOLERANCE_FACTOR
                      ):
            t_xticks = np.append(t_xticks, d_echem["time"][i])
            j += 1
            if j == len(xticks_labels):
                break
    y_diff = d["y_data"] - d["y_nmf"]
    plt.style.use(bg_mpl_style)
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    fig = plt.figure(
                     dpi = d["dpi"],
                     figsize = d["figsize"],
                     )
    gs = GridSpec(
                  ncols = 2,
                  nrows = 3,
                  width_ratios=[1, 0.1375],
                  height_ratios=[1, 0.4, 0.4],
                  hspace = 0.1,
                  )
    ax0 = fig.add_subplot(gs[0, :])
    ax1 = fig.add_subplot(gs[1, 0])
    ax2 = fig.add_subplot(gs[2, 0])
    ax21 = ax2.twiny()
    ax21.plot(d_echem["time"], d_echem["voltage"], zorder=0)
    ax2.set_xlim(np.amin(d_echem["time"]), np.amax(d_echem["time"]))
    ax21.set_xlim(np.amin(d_echem["time"]), np.amax(d_echem["time"]))
    ax2.set_ylim(d["voltage_min"], d["voltage_max"])
    ax21.set_ylim(d["voltage_min"], d["voltage_max"])
    ax21.set_ylabel(d["voltage_label"], fontsize=FONTSIZE_LABELS)
    ax21.xaxis.set_label_position("top")
    ax21.tick_params(axis="x",
                     labelbottom=False,
                     labeltop=False,
                     labelsize=FONTSIZE_TICKS,
                     )
    ax2.set_xticks(t_xticks)
    ax2.set_xticklabels(xticks_labels)
    ax2.set_xlabel(d["x_label"], fontsize=FONTSIZE_LABELS)
    ax2.set_ylabel(d["voltage_label"], fontsize=FONTSIZE_LABELS, labelpad=20)
    ax2.xaxis.set_tick_params(labelsize=FONTSIZE_TICKS)
    ax2.yaxis.set_tick_params(labelsize=FONTSIZE_TICKS)
    ax2.minorticks_on()
    ax21.minorticks_on()
    im = ax0.imshow(y_diff,
                    aspect="auto",
                    interpolation="nearest",
                    extent=(np.amin(d_echem["time"]),
                            np.amax(d_echem["time"]),
                            d["xmax"],
                            d["xmin"]
                            ),
                    vmin=d["vmin"],
                    vmax=d["vmax"],
                    cmap = d["cmap"],
                    )
    ax0.minorticks_on()
    cbar = ax0.figure.colorbar(im, ax=ax0)
    cbar.set_label(label=SCATT_YLABEL, size=FONTSIZE_LABELS)
    ax0.set_xlabel(d["time_label"], fontsize=FONTSIZE_LABELS, labelpad=10)
    ax0.xaxis.set_label_position("top")
    ax0.tick_params(axis="x",
                    labelbottom=False,
                    labeltop=True,
                    labelsize=FONTSIZE_TICKS,
                    )
    ax0.set_ylabel(SCATT_XLABEL, fontsize=FONTSIZE_LABELS, labelpad=25)
    x_frac = d["x_corrcoeffs"] / np.amax(d["x_corrcoeffs"])
    x_time = x_frac * np.amax(d_echem["time"])
    ax1.plot(x_time, d["corrcoeffs"], marker="o", c=colors[1])
    ax1.set_xlim(np.amin(x_time), np.amax(x_time))
    ax1.set_ylabel(PEARSON_LABEL, fontsize=FONTSIZE_LABELS, labelpad=10)
    ax1.minorticks_on()
    ax1.tick_params(axis="x",
                    labelbottom=False,
                    labeltop=False,
                    )
    for p in plotpaths:
        plt.savefig(p / f"data_nmf_diff_corr_echem_plot.{p.name}",
                    bbox_inches="tight",
                    )
        sys.exit()

    return None


def main():
    data_exp_path = Path.cwd() / "data_exp"
    data_nmf_comps_path = Path.cwd() / "data_nmf_comps"
    data_nmf_weights_path = Path.cwd() / "data_nmf_weights"
    data_echem_path = Path.cwd() / "data_echem"
    echem_file = list(data_echem_path.glob("*.*"))[0]
    dpaths = [data_exp_path, data_nmf_comps_path, data_nmf_weights_path]
    for p in dpaths:
        if not p.exists():
            p.mkdir()
            print(f"{80*'-'}\nA folder called '{p.name}' has been created."
                  f"\nPlease put your data file(s) here and rerun the code.")
            sys.exit()
    data_exp_files = list(data_exp_path.glob("*.*"))
    d_data = data_extract(data_exp_files)
    comps_file = list(data_nmf_comps_path.glob("*.*"))[0]
    d_comps = comps_extract(comps_file)
    weights_file = list(data_nmf_weights_path.glob("*.*"))[0]
    weights = weights_extract(weights_file)
    comps_weighted = linear_combine(d_comps, weights)
    xmin_index_data, xmax_index_data = extremum_indices(d_data["x"], XMIN, XMAX)
    xmin_index_nmf, xmax_index_nmf = extremum_indices(d_comps["x"], XMIN, XMAX)
    y_data = d_data["y"][xmin_index_data:xmax_index_data]
    y_nmf = comps_weighted[xmin_index_nmf:xmax_index_nmf]
    corrcoeffs = data_nmf_correlate(y_data, y_nmf)
    x_corrcoeffs = x_array_blank_scans(corrcoeffs, BLANK_SCANS)
    y_data = blank_scans_insert(y_data, BLANK_SCANS)
    y_nmf = blank_scans_insert(y_nmf, BLANK_SCANS)
    d_echem = dict_echem_extract(echem_file)
    d_echem = x_from_dict_calcualte(d_echem)
    png_path, pdf_path = Path.cwd() / "png", Path.cwd() / "pdf"
    svg_path = Path.cwd() / "svg"
    plotpaths = [png_path, pdf_path, svg_path]
    for p in plotpaths:
        if not p.exists():
            p.mkdir()
    d_plot = dict(y_data = y_data,
                  y_nmf = y_nmf,
                  xmin = XMIN,
                  xmax = XMAX,
                  x_corrcoeffs = x_corrcoeffs,
                  corrcoeffs = corrcoeffs,
                  dpi = DPI,
                  figsize = FIGSIZE,
                  vmin = GDIFF_MIN,
                  vmax = GDIFF_MAX,
                  voltage_min = VOLTAGE_MIN,
                  voltage_max = VOLTAGE_MAX,
                  time_label = TIMELABEL,
                  voltage_label = VOLTAGELABEL,
                  x_label = XLABEL,
                  cmap = CMAP,
                  )
    diff_plot(d_plot, d_echem, plotpaths)

    return None


if __name__ == "__main__":
    main()

# End of file
