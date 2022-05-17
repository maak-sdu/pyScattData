import sys
import time
from pathlib import Path
import numpy as np
from diffpy.utils.parsers.loaddata import loadData
from scipy.constants import physical_constants
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.gridspec import GridSpec
try:
    from bg_mpl_stylesheet.bg_mpl_stylesheet import bg_mpl_style
    PLOT_STYLE = "found"
except ModuleNotFoundError:
    PLOT_STYLE = None


# Inputs to load echem
INDEX_TIME = 0
INDEX_VOLTAGE = 1
INDEX_CURRENT = 2

# Inputs to calculate state of charge
WORKING_ION_CHARGE = 1
WORKING_ION_START_VALUE = 0
MOLAR_MASS = 79.866
MASS = 0.6 * 11.276 * 10**-3

# Plot-specific inputs
DPI = 600
FIGSIZE = (8,4)
AXESLABEL = 'Scan Number'
CBARLABEL = r'$r_{\mathrm{Pearson}}$'
TICKINDEX_MAJOR = 10
TICKINDEX_MINOR = 1
FONTSIZE_TICKS = 12
FONTSIZE_LABELS = 18
CMAP = 'YlOrRd'

BREAKFACTOR_X = 0.04
BREAKFACTOR_Y = 0.05
TOLERANCE_FACTOR = 10**2
HSPACE = 0.1


CBAR_REL_DICT = dict(
                     # r = 1-10 Å
                     # vmin = 0.85,
                     # decimals = 3,
                     # ticks = np.linspace(0.85, 1.0, int((1.0-0.85)/0.025)+1)
                     # r = 10-20 Å
                     # vmin = 0.5,
                     # decimals = 1,
                     # ticks = np.linspace(0.5, 1.0, int((1.0-0.5)/0.1)+1)
                     # r = 20-30 Å
                     # vmin = 0.65,
                     # decimals = 2,
                     # ticks = np.linspace(0.65, 1.0, int((1.0-0.65)/0.05)+2)
                     # r = 1-15 Å
                     # vmin = 0.825,
                     # decimals = 3,
                     # ticks = np.linspace(0.825, 1.0, int((1.0-0.825)/0.025)+1)
                     # r = 10-25 Å
                     # vmin = 0.5,
                     # decimals = 1,
                     # ticks = np.linspace(0.5, 1.0, int((1.0-0.5)/0.1)+1)
                     # r = 1-30 Å
                     vmin = 0.825,
                     decimals = 3,
                     ticks = np.linspace(0.825, 1, int((1-0.825)/0.025)+1)
                    )
# print(CBAR_REL_DICT["ticks"])
# sys.exit()
# CBAR_REL_DICT = None

TIMELABEL_ECHEM = r"$t$ $[\mathrm{h}]$"
XLABEL_ECHEM = r"$x$ in Li$_{x}$TiO$_{2}$"

HEIGHTRATIO_V_LABEL = 0.25
HEIGHTRATIO_LI_LABEL = 0.4
HEIGHTRATIO_NA_LABEL = 0.5

TICKINDEX_MAJOR_ECHEM_TIME = 5
TICKINDEX_MINOR_ECHEM_TIME = 1
TICKINDEX_MAJOR_ECHEM_X = 0.2
TICKINDEX_MINOR_ECHEM_X = 0.2 / 5
TICKINDEX_MAJOR_ECHEM_VOLTAGE = 0.5
TICKINDEX_MINOR_ECHEM_VOLTAGE = 0.1

COLORS = ['#0B3C5D', '#B82601', '#1c6b0a', '#328CC1',
          '#a8b6c1', '#D9B310', '#984B43', '#76323F',
          '#626E60', '#AB987A', '#C09F80', '#b0b0b0ff']

# See possible colormaps in the dictionary below.
CMAPS = {0:'viridis', 1:'plasma', 2:'inferno', 3:'magma', 4:'Greys',
         5:'Purples', 6:'Blues', 7:'Greens', 8:'Oranges', 9:'Reds',
         10: 'YlOrBr', 11:'YlOrRd', 12:'OrRd', 13:'PuRd', 14:'RdPu',
         15:'BuPu', 16:'GnBu', 17:'PuBu', 18:'YlGnBu', 19:'PuBuGn',
         20:'BuGn', 21:'YlGn', 22:'binary', 23:'gist_yarg', 24:'gist_gray',
         25:'gray', 26:'bone', 27:'pink', 28:'spring', 29:'summer',
         30:'autumn', 31:'winter', 32:'cool', 33:'Wistia', 34:'hot',
         35:'afmhot', 36:'gist_heat', 37:'copper', 38:'PiYG', 39:'PRGn',
         40:'BrBG', 41:'PuOr', 42:'RdGy', 43:'RdBu', 44:'RdYlBu',
         45:'RdYlGn', 46:'Spectral', 47:'coolwarm', 48:'bwr', 49:'seismic',
         50:'twilight', 51:'twilight_shifted', 52:'hsv', 53:'ocean',
         54:'gist_earth', 55:'terrain', 56:'gist_stern', 57:'gnuplot',
         58:'gnuplot2', 59:'CMRmap', 60:'cubehelix', 61:'brg',
         62:'gist_rainbow', 63:'rainbow', 64:'jet', 65:'turbo',
         66:'nipy_spectral', 67:'gist_ncar'}


def dict_echem_extract(echem_file):
    d = {}
    data = loadData(echem_file)
    d["time"] = data[:,INDEX_TIME]
    d["voltage"] = data[:,INDEX_VOLTAGE]
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


def dict_scatt_extract(scatt_files):
    d = {}
    for f in scatt_files:
        scan = int(str(f.stem).split('_')[-1])
        d[scan] = {}
        data = loadData(str(f))
        d[scan]["x"] = data[:,0]
        d[scan]["y"] = data[:,1]

    return d


def pearson_correlation(scatt_files, d_scatt, d_corr):
    for f in scatt_files:
        scan = int(str(f.stem).split('_')[-1])
        basename = ''
        for e in str(f.stem).split("_")[0:-1]:
            basename += f"{e}_"
        with f.open(mode="r"):
            data = loadData(str(f))
        x_data, y_data = data[:,0], data[:,1]
        xmin_index, xmax_index = 0, len(x_data) - 1
        xmin, xmax = d_corr["xmin"], d_corr["xmax"]
        for i in range(len(x_data)):
            if x_data[i] >= xmin:
                xmin_index = i
                break
        for i in range(len(x_data)):
            if x_data[i] >= xmax:
                xmax_index = i
                break
        if xmax_index == len(x_data) - 1:
            d_scatt[scan] = dict(x = x_data[xmin_index::],
                                 y = y_data[xmin_index::])
        else:
            d_scatt[scan] = dict(x = x_data[xmin_index:xmax_index+1],
                                 y = y_data[xmin_index:xmax_index+1])
    scanlist = list(d_scatt.keys())
    missing_scans = []
    for i in range(1, len(scanlist)):
        if scanlist[i] - scanlist[i-1] != 1:
            for j in range(1, scanlist[i] - scanlist[i-1]):
                missing_scans.append(i+j)
    if len(missing_scans) > 0:
        print(f"\nMissing scan(s) {missing_scans}. Consider including 'blank' "
               "scan(s) with this(these) scan number(s).\n")
    startscan, endscan = scanlist[0] - 1, scanlist[-1]
    x_list = [d_scatt[k]['x'] for k in scanlist]
    y_list = [d_scatt[k]['y'] for k in scanlist]
    y_list = np.array(y_list)
    keys = [k for k in d_scatt]
    keys_str = [str(k) for k in scanlist]
    corr_matrix = np.corrcoef(y_list).round(decimals=6)
    corr_matrix_str = corr_matrix.astype(str)
    header_rows = np.array([keys]).astype(str)
    header_columns = header_rows.reshape(-1,1)
    corr_matrix_header = np.vstack((header_rows, corr_matrix))
    corr_matrix_txt = np.vstack((np.array(['']).astype(str), header_columns))
    for i in range(np.shape(corr_matrix_header)[1]):
        corr_matrix_txt = np.column_stack((corr_matrix_txt, corr_matrix_header[:,i]))
    print(f"{80*'-'}\nSaving txt file containing matrix to the 'txt' folder...")
    np.savetxt(f'txt/{basename}correalation_matrix_x={xmin}-{xmax}.txt',
               corr_matrix_txt,
               fmt='%s',
               delimiter='\t')
    print(f"{80*'-'}\nPlotting...\n\tcorrelation matrix on relative scale...")
    if not isinstance(PLOT_STYLE, type(None)):
        plt.style.use(bg_mpl_style)
    fig, ax = plt.subplots(dpi=DPI, figsize=FIGSIZE)
    if not isinstance(CBAR_REL_DICT, type(None)):
        im = ax.imshow(corr_matrix,
                       cmap=CMAP,
                       extent=(startscan, endscan, endscan, startscan),
                       aspect="equal",
                       vmin=CBAR_REL_DICT["vmin"],
                       vmax=1,
                       )
    else:
        im = ax.imshow(corr_matrix,
                       cmap=CMAP,
                       extent=(startscan, endscan, endscan, startscan),
                       aspect="equal",
                       )
    ax.grid(False)
    ax.xaxis.set_major_locator(MultipleLocator(TICKINDEX_MAJOR))
    ax.xaxis.set_minor_locator(MultipleLocator(TICKINDEX_MINOR))
    ax.yaxis.set_major_locator(MultipleLocator(TICKINDEX_MAJOR))
    ax.yaxis.set_minor_locator(MultipleLocator(TICKINDEX_MINOR))
    ax.set_xlabel(AXESLABEL, fontsize=FONTSIZE_LABELS)
    ax.set_ylabel(AXESLABEL, fontsize=FONTSIZE_LABELS)
    ax.xaxis.set_label_position('top')
    ax.tick_params(axis='both', labelsize=FONTSIZE_TICKS)
    ax.tick_params(axis="x", bottom=True, top=True, labelbottom=False,
                   labeltop=True)
    if not isinstance(CBAR_REL_DICT, type(None)):
        cbar = ax.figure.colorbar(im,
                                  ax=ax,
                                  format=f'%.{CBAR_REL_DICT["decimals"]}f',
                                  ticks=CBAR_REL_DICT["ticks"])
    else:
        cbar = ax.figure.colorbar(im, ax=ax)
    cbar.set_label(label=CBARLABEL, size=FONTSIZE_LABELS)
    plt.savefig(f'png/{basename}correlation_matrix_rel_x={xmin}-{xmax}.png',
                bbox_inches='tight')
    plt.savefig(f'pdf/{basename}correlation_matrix_rel_x={xmin}-{xmax}.pdf',
                bbox_inches='tight')
    plt.savefig(f'svg/{basename}correlation_matrix_rel_x={xmin}-{xmax}.svg',
                bbox_inches='tight')
    plt.close()
    print("\tcorrelation matrix on absolute scale...")
    fig, ax = plt.subplots(dpi=DPI, figsize=FIGSIZE)
    im = ax.imshow(corr_matrix,
                   cmap=CMAP,
                   vmin=0, vmax=1,
                   extent=(startscan, endscan, endscan, startscan))
    ax.grid(False)
    ax.xaxis.set_major_locator(MultipleLocator(TICKINDEX_MAJOR))
    ax.xaxis.set_minor_locator(MultipleLocator(TICKINDEX_MINOR))
    ax.yaxis.set_major_locator(MultipleLocator(TICKINDEX_MAJOR))
    ax.yaxis.set_minor_locator(MultipleLocator(TICKINDEX_MINOR))
    # ax.xaxis.tick_top()
    ax.set_xlabel(AXESLABEL, fontsize=FONTSIZE_LABELS)
    ax.set_ylabel(AXESLABEL, fontsize=FONTSIZE_LABELS)
    ax.xaxis.set_label_position('top')
    ax.tick_params(axis='both', labelsize=FONTSIZE_TICKS)
    ax.tick_params(axis="x", bottom=True, top=True, labelbottom=False,
                   labeltop=True)
    cbar = ax.figure.colorbar(im, ax=ax, format='%.1f')
    cbar.set_label(label=CBARLABEL, size=FONTSIZE_LABELS)
    plt.savefig(f'png/{basename}correlation_matrix_abs_x={xmin}-{xmax}.png',
                bbox_inches='tight')
    plt.savefig(f'pdf/{basename}correlation_matrix_abs_x={xmin}-{xmax}.pdf',
                bbox_inches='tight')
    plt.savefig(f'svg/{basename}correlation_matrix_abs_x={xmin}-{xmax}.svg',
                bbox_inches='tight')
    plt.close()
    print(f"\nPearson correlation analysis completed.\n{80*'-'}\nFigures of "
          f"the Pearson correlation matrix have been saved to the pdf and png "
          f"\nfolders. A .txt file with the correlation matrix has been saved "
          f"to the txt folder.\n{80*'-'}")
    d_corr["corr_matrix"], d_corr["scanlist"] = corr_matrix, scanlist
    d_corr["basename"] = basename
    d_corr["xmin"], d_corr["xmax"] = xmin, xmax

    return d_corr


def dummy_scan(data_scatt_path):
    files = list(data_scatt_path.glob("*.*"))
    basename = ''
    for e in str(files[0].stem).split("_")[0:-1]:
        basename += f"{e}_"
    file_ext = files[0].suffix
    zerofill = len(str(files[0].stem).split("_")[-1])
    scans = [int(str(e.stem).split("_")[-1]) for e in files]
    missing_scans = []
    for i in range(1, len(scans)):
        if scans[i] - scans[i-1] != 1:
            for j in range(1, scans[i] - scans[i-1]):
                missing_scans.append(str(scans[i-1]+j).zfill(zerofill))
    if len(missing_scans) > 0:
        with open(files[0]) as f:
            data = loadData(files[0])
            x = data[:,0]
        xy_dummy = np.column_stack((x, np.zeros(len(x))))
        for e in missing_scans:
            if file_ext == '.gr':
                np.savetxt(f"{data_scatt_path}/{basename}{e}{file_ext}",
                           xy_dummy,
                           fmt='%.2f',
                           encoding="utf-8",
                           )
            else:
                np.savetxt(f"{data_scatt_path}/{basename}{e}{file_ext}",
                           xy_dummy,
                           fmt='%.6f',
                           encoding="utf-8",
                           )
        print(f"\nThe following dummy scans have been saved to the "
              f"{data_scatt_path.name} directory:")
        for e in missing_scans:
            print(f"\t{basename}{e}{file_ext}")
    else:
        print("No scans were missing.")

    return basename


def echem_plotter(d_echem):
    time, voltage = d_echem["time"], d_echem["voltage"]
    current, x = d_echem["current"], d_echem["x"]
    voltage_min, voltage_max = d_echem["voltage_min"], d_echem["voltage_max"]
    basename, ylabel_echem = d_echem["basename"], d_echem["ylabel_echem"]
    print(f"{80*'-'}\nPlotting electrochemistry...")
    if not isinstance(PLOT_STYLE, type(None)):
        plt.style.use(bg_mpl_style)
    fig, ax = plt.subplots(dpi=DPI, figsize=FIGSIZE)
    plt.plot(time, voltage, c=COLORS[1])
    plt.xlim(np.amin(time), np.amax(time))
    plt.ylim(voltage_min, voltage_max)
    ylabel_echem = ylabel_echem.replace("\n", " ")
    plt.xlabel(TIMELABEL_ECHEM, fontsize=FONTSIZE_LABELS)
    plt.ylabel(ylabel_echem, fontsize=FONTSIZE_LABELS)
    ax.tick_params(axis="both", labelsize=FONTSIZE_TICKS)
    ax.xaxis.set_major_locator(MultipleLocator(TICKINDEX_MAJOR_ECHEM_TIME))
    ax.xaxis.set_minor_locator(MultipleLocator(TICKINDEX_MINOR_ECHEM_TIME))
    ax.yaxis.set_major_locator(MultipleLocator(TICKINDEX_MAJOR_ECHEM_VOLTAGE))
    ax.yaxis.set_minor_locator(MultipleLocator(TICKINDEX_MINOR_ECHEM_VOLTAGE))
    plt.savefig(f"png/{basename}echem_t_v.png", bbox_inches="tight")
    plt.savefig(f"pdf/{basename}echem_t_v.pdf", bbox_inches="tight")
    plt.savefig(f"svg/{basename}echem_t_v.svg", bbox_inches="tight")
    plt.close()
    fig, ax = plt.subplots(dpi=DPI, figsize=FIGSIZE)
    plt.plot(x, voltage, c=COLORS[1])
    plt.xlim(np.amin(x), np.amax(x))
    plt.ylim(voltage_min, voltage_max)
    ylabel_echem = ylabel_echem.replace("\n", " ")
    plt.xlabel(XLABEL_ECHEM, fontsize=FONTSIZE_LABELS)
    plt.ylabel(ylabel_echem, fontsize=FONTSIZE_LABELS)
    ax.tick_params(axis="both", labelsize=FONTSIZE_TICKS)
    ax.xaxis.set_major_locator(MultipleLocator(TICKINDEX_MAJOR_ECHEM_X))
    ax.xaxis.set_minor_locator(MultipleLocator(TICKINDEX_MINOR_ECHEM_X))
    ax.yaxis.set_major_locator(MultipleLocator(TICKINDEX_MAJOR_ECHEM_TIME))
    ax.yaxis.set_minor_locator(MultipleLocator(TICKINDEX_MINOR_ECHEM_TIME))
    plt.savefig(f"png/{basename}echem_x_v.png", bbox_inches="tight")
    plt.savefig(f"pdf/{basename}echem_x_v.pdf", bbox_inches="tight")
    plt.savefig(f"svg/{basename}echem_x_v.svg", bbox_inches="tight")
    plt.close()
    print(f"Plot with electrochemistry saved to the 'pdf' and 'png' folders.\
            \n{80*'-'}")

    return None


def pearson_echem_plotter(d_corr, d_echem, d_plot):
    corr_matrix, scanlist = d_corr["corr_matrix"], d_corr["scanlist"]
    xmin, xmax = d_corr["xmin"], d_corr["xmax"]
    basename = d_corr["basename"]
    time, voltage, = d_echem["time"], d_echem["voltage"]
    current, x = d_echem["current"], d_echem["x"]
    voltage_min, voltage_max = d_echem["voltage_min"], d_echem["voltage_max"]
    ylabel_echem = d_echem["ylabel_echem"]
    heightratio = d_plot["heightratio"]
    startscan, endscan = scanlist[0] - 1, scanlist[-1]
    print("Plotting correlation matrix and electrochemistry together..."
          "\n\ton absolute scale")
    if not isinstance(PLOT_STYLE, type(None)):
        plt.style.use(bg_mpl_style)
    fig = plt.figure(dpi=DPI, figsize=(6,6))
    time = d_echem["time"]
    voltage = d_echem["voltage"]
    current = d_echem["current"]
    x = d_echem["x"]
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
    if not isinstance(PLOT_STYLE, type(None)):
        plt.style.use(bg_mpl_style)
    gs = GridSpec(nrows=2,
                  ncols=3,
                  figure=fig,
                  width_ratios=[0.0965, 1, 0.209],
                  height_ratios=heightratio,
                  hspace=0.1)
    ax0 = fig.add_subplot(gs[0,:])
    ax1 = fig.add_subplot(gs[1,1])
    im = ax0.imshow(corr_matrix,
                    cmap=CMAP,
                    vmin=0,
                    vmax=1,
                    extent=(startscan, endscan, endscan, startscan),
                    aspect="equal",
                    )
    ax0.grid(False)
    ax0.xaxis.set_major_locator(MultipleLocator(TICKINDEX_MAJOR))
    ax0.xaxis.set_minor_locator(MultipleLocator(TICKINDEX_MINOR))
    ax0.yaxis.set_major_locator(MultipleLocator(TICKINDEX_MAJOR))
    ax0.yaxis.set_minor_locator(MultipleLocator(TICKINDEX_MINOR))
    ax0.set_xlabel(AXESLABEL, fontsize=FONTSIZE_LABELS)
    ax0.set_ylabel(AXESLABEL, fontsize=FONTSIZE_LABELS)
    ax0.xaxis.set_label_position('top')
    ax0.tick_params(axis='both', labelsize=FONTSIZE_TICKS)
    ax0.tick_params(axis="x", bottom=True, top=True, labelbottom=False,
                    labeltop=True)
    ax1.plot(time, voltage, c=COLORS[1])
    ax1.set_xlim(np.amin(time), np.amax(time))
    ax1.set_ylim(voltage_min, voltage_max)
    ax1.set_xlabel(XLABEL_ECHEM, fontsize=FONTSIZE_LABELS)
    ax1.set_ylabel(ylabel_echem, fontsize=FONTSIZE_LABELS)
    ax1.tick_params(axis='both', labelsize=FONTSIZE_TICKS)
    ax1.xaxis.set_major_locator(MultipleLocator(TICKINDEX_MAJOR_ECHEM_TIME))
    ax1.xaxis.set_minor_locator(MultipleLocator(TICKINDEX_MINOR_ECHEM_TIME))
    ax1.yaxis.set_major_locator(MultipleLocator(TICKINDEX_MAJOR_ECHEM_VOLTAGE))
    ax1.yaxis.set_minor_locator(MultipleLocator(TICKINDEX_MINOR_ECHEM_VOLTAGE))
    cbar = plt.colorbar(im,
                        ax=ax0,
                        anchor=(0,1),
                        )
    cbar.set_label(label=CBARLABEL, size=FONTSIZE_LABELS)
    plt.savefig(f'png/{basename}correlation_matrix_echem_abs_x={xmin}-{xmax}.png',
                bbox_inches='tight')
    plt.savefig(f'pdf/{basename}correlation_matrix_echem_abs_x={xmin}-{xmax}.pdf',
                bbox_inches='tight')
    plt.savefig(f'svg/{basename}correlation_matrix_echem_abs_x={xmin}-{xmax}.svg',
                bbox_inches='tight')
    plt.close()
    print("\ton relative scale")
    fig = plt.figure(dpi=DPI, figsize=(6,6))
    gs = GridSpec(nrows=2,
                  ncols=3,
                  figure=fig,
                  width_ratios=[0.0965, 1, 0.209],
                  height_ratios=heightratio,
                  hspace=0.1)
    ax0 = fig.add_subplot(gs[0,:])
    ax1 = fig.add_subplot(gs[1,1])
    if not isinstance(CBAR_REL_DICT, type(None)):
        im = ax0.imshow(corr_matrix,
                       cmap=CMAP,
                       extent=(startscan, endscan, endscan, startscan),
                       aspect="equal",
                       vmin=CBAR_REL_DICT["vmin"],
                       vmax=1,
                       )
    else:
        im = ax0.imshow(corr_matrix,
                       cmap=CMAP,
                       extent=(startscan, endscan, endscan, startscan),
                       aspect="equal",
                       )
    ax0.grid(False)
    ax0.xaxis.set_major_locator(MultipleLocator(TICKINDEX_MAJOR))
    ax0.xaxis.set_minor_locator(MultipleLocator(TICKINDEX_MINOR))
    ax0.yaxis.set_major_locator(MultipleLocator(TICKINDEX_MAJOR))
    ax0.yaxis.set_minor_locator(MultipleLocator(TICKINDEX_MINOR))
    ax0.set_xlabel(AXESLABEL, fontsize=FONTSIZE_LABELS)
    ax0.set_ylabel(AXESLABEL, fontsize=FONTSIZE_LABELS)
    ax0.xaxis.set_label_position('top')
    ax0.tick_params(axis='both', labelsize=FONTSIZE_TICKS)
    ax0.tick_params(axis="x", bottom=True, top=True, labelbottom=False,
                    labeltop=True)
    ax1.plot(time, voltage, c=COLORS[1])
    ax1.set_xlim(np.amin(time), np.amax(time))
    ax1.set_ylim(voltage_min, voltage_max)
    ax1.set_xlabel(XLABEL_ECHEM, fontsize=FONTSIZE_LABELS)
    ax1.set_ylabel(ylabel_echem, fontsize=FONTSIZE_LABELS)
    ax1.tick_params(axis='both', labelsize=FONTSIZE_TICKS)
    ax1.xaxis.set_major_locator(MultipleLocator(TICKINDEX_MAJOR_ECHEM_TIME))
    ax1.xaxis.set_minor_locator(MultipleLocator(TICKINDEX_MINOR_ECHEM_TIME))
    ax1.yaxis.set_major_locator(MultipleLocator(TICKINDEX_MAJOR_ECHEM_VOLTAGE))
    ax1.yaxis.set_minor_locator(MultipleLocator(TICKINDEX_MINOR_ECHEM_VOLTAGE))
    if not isinstance(CBAR_REL_DICT, type(None)):
        cbar = plt.colorbar(im,
                            ax=ax0,
                            anchor=(0,1),
                            format=f'%.{CBAR_REL_DICT["decimals"]}f',
                            ticks=CBAR_REL_DICT["ticks"])
    else:
        cbar = plt.colorbar(im,
                            ax=ax0,
                            anchor=(0,1),
                            )
    cbar.set_label(label=CBARLABEL, size=FONTSIZE_LABELS)
    plt.savefig(f'png/{basename}correlation_matrix_echem_rel_x={xmin}-{xmax}.png',
                bbox_inches='tight')
    plt.savefig(f'pdf/{basename}correlation_matrix_echem_rel_x={xmin}-{xmax}.pdf',
                bbox_inches='tight')
    plt.savefig(f'svg/{basename}correlation_matrix_echem_rel_x={xmin}-{xmax}.svg',
                bbox_inches='tight')
    plt.close()
    fig = plt.figure(dpi=DPI, figsize=(8,8))
    gs = GridSpec(nrows=2,
                  ncols=3,
                  figure=fig,
                  width_ratios=[0.0965, 1, 0.209],
                  height_ratios=heightratio,
                  hspace=0.1)
    ax0 = fig.add_subplot(gs[0,:])
    ax1 = fig.add_subplot(gs[1,1])
    ax11 = ax1.twiny()
    ax11.plot(time, voltage, c=COLORS[1])
    ax1.set_xlim(time_min, time_max)
    ax11.set_xlim(time_min, time_max)
    ax1.set_ylim(voltage_min, voltage_max)
    ax11.set_ylim(voltage_min, voltage_max)
    voltage_range = voltage_max - voltage_min
    ax11.set_ylabel(ylabel_echem, fontsize=FONTSIZE_LABELS)
    ax11.xaxis.set_label_position("top")
    ax11.tick_params(axis="x",
                    labelbottom=False,
                    labeltop=False,
                    labelsize=FONTSIZE_TICKS)
    ax11.xaxis.set_major_locator(MultipleLocator(TICKINDEX_MAJOR_ECHEM_TIME))
    ax11.xaxis.set_minor_locator(MultipleLocator(TICKINDEX_MINOR_ECHEM_TIME))
    ax11.yaxis.set_major_locator(MultipleLocator(TICKINDEX_MAJOR_ECHEM_VOLTAGE))
    ax11.yaxis.set_minor_locator(MultipleLocator(TICKINDEX_MINOR_ECHEM_VOLTAGE))
    ax1.set_xticks(t_xticks)
    ax1.set_xticklabels(xticks_labels)
    ax1.set_xlabel(XLABEL_ECHEM, fontsize=FONTSIZE_LABELS)
    ax1.set_ylabel(ylabel_echem, fontsize=FONTSIZE_LABELS)
    ax1.xaxis.set_tick_params(labelsize=FONTSIZE_TICKS)
    ax1.yaxis.set_tick_params(labelsize=FONTSIZE_TICKS)
    for i in range(len(t_changes)):
        plt.text(t_changes[i] - BREAKFACTOR_X * time_range,
                 voltage_min - BREAKFACTOR_Y * voltage_range,
                 "|",
                 rotation=45)
    scan_time = np.array([i * (time_range / (corr_matrix.shape[0] - 1))
                          for i in range(corr_matrix.shape[0])]
                          )
    if not isinstance(CBAR_REL_DICT, type(None)):
        im = ax0.imshow(corr_matrix,
                        cmap=CMAP,
                        extent=(0, np.amax(scan_time), np.amax(scan_time), 0),
                        aspect="equal",
                        vmin=CBAR_REL_DICT["vmin"],
                        vmax=1,
                        )
    else:
        im = ax0.imshow(corr_matrix,
                       cmap=CMAP,
                       extent=(0, np.amax(scan_time), np.amax(scan_time), 0),
                       aspect="equal",
                       )
    ax0.set_xlabel(TIMELABEL_ECHEM, fontsize=FONTSIZE_LABELS)
    ax0.xaxis.set_label_position("top")
    ax0.tick_params(axis="x",
                    labelbottom=False,
                    labeltop=True,
                    labelsize=FONTSIZE_TICKS)
    ax0.xaxis.set_major_locator(MultipleLocator(TICKINDEX_MAJOR_ECHEM_TIME))
    ax0.xaxis.set_minor_locator(MultipleLocator(TICKINDEX_MINOR_ECHEM_TIME))
    ax0.yaxis.set_major_locator(MultipleLocator(TICKINDEX_MAJOR_ECHEM_TIME))
    ax0.yaxis.set_minor_locator(MultipleLocator(TICKINDEX_MINOR_ECHEM_TIME))
    ax0.set_ylabel(TIMELABEL_ECHEM, fontsize=FONTSIZE_LABELS)
    if not isinstance(CBAR_REL_DICT, type(None)):
        cbar = ax0.figure.colorbar(im,
                                   ax=ax0,
                                   format=f'%.{CBAR_REL_DICT["decimals"]}f',
                                   ticks=CBAR_REL_DICT["ticks"])
    else:
        cbar = ax0.figure.colorbar(im, ax=ax0)
    cbar.set_label(label=CBARLABEL, size=FONTSIZE_LABELS)
    plt.savefig(f"png/{basename}correlation_matrix_echem_t_x_v_rel_x={xmin}-{xmax}.png", bbox_inches="tight")
    plt.savefig(f"pdf/{basename}correlation_matrix_echem_t_x_v_rel_x={xmin}-{xmax}.pdf", bbox_inches="tight")
    plt.savefig(f"svg/{basename}correlation_matrix_echem_t_x_v_rel_x={xmin}-{xmax}.svg", bbox_inches="tight")
    plt.close()
    fig = plt.figure(dpi=DPI, figsize=(8,8))
    gs = GridSpec(nrows=2,
                  ncols=3,
                  figure=fig,
                  width_ratios=[0.0965, 1, 0.209],
                  height_ratios=heightratio,
                  hspace=0.1)
    ax0 = fig.add_subplot(gs[0,:])
    ax1 = fig.add_subplot(gs[1,1])
    ax11 = ax1.twiny()
    ax11.plot(time, voltage, c=COLORS[1])
    ax1.set_xlim(time_min, time_max)
    ax11.set_xlim(time_min, time_max)
    ax1.set_ylim(voltage_min, voltage_max)
    ax11.set_ylim(voltage_min, voltage_max)
    voltage_range = voltage_max - voltage_min
    ax11.set_ylabel(ylabel_echem, fontsize=FONTSIZE_LABELS)
    ax11.xaxis.set_label_position("top")
    ax11.tick_params(axis="x",
                    labelbottom=False,
                    labeltop=False,
                    labelsize=FONTSIZE_TICKS)
    ax11.xaxis.set_major_locator(MultipleLocator(TICKINDEX_MAJOR_ECHEM_TIME))
    ax11.xaxis.set_minor_locator(MultipleLocator(TICKINDEX_MINOR_ECHEM_TIME))
    ax11.yaxis.set_major_locator(MultipleLocator(TICKINDEX_MAJOR_ECHEM_VOLTAGE))
    ax11.yaxis.set_minor_locator(MultipleLocator(TICKINDEX_MINOR_ECHEM_VOLTAGE))
    ax1.set_xticks(t_xticks)
    ax1.set_xticklabels(xticks_labels)
    ax1.set_xlabel(XLABEL_ECHEM, fontsize=FONTSIZE_LABELS)
    ax1.set_ylabel(ylabel_echem, fontsize=FONTSIZE_LABELS)
    ax1.xaxis.set_tick_params(labelsize=FONTSIZE_TICKS)
    ax1.yaxis.set_tick_params(labelsize=FONTSIZE_TICKS)
    for i in range(len(t_changes)):
        plt.text(t_changes[i] - BREAKFACTOR_X * time_range,
                 voltage_min - BREAKFACTOR_Y * voltage_range,
                 "|",
                 rotation=45)
    scan_time = np.array([i * (time_range / (corr_matrix.shape[0] - 1))
                          for i in range(corr_matrix.shape[0])]
                          )
    im = ax0.imshow(corr_matrix,
                    cmap=CMAP,
                    extent=(0, np.amax(scan_time), np.amax(scan_time), 0),
                    aspect="equal",
                    vmin=0,
                    vmax=1,
                    )
    ax0.set_xlabel(TIMELABEL_ECHEM, fontsize=FONTSIZE_LABELS)
    ax0.xaxis.set_label_position("top")
    ax0.tick_params(axis="x",
                    labelbottom=False,
                    labeltop=True,
                    labelsize=FONTSIZE_TICKS)
    ax0.xaxis.set_major_locator(MultipleLocator(TICKINDEX_MAJOR_ECHEM_TIME))
    ax0.xaxis.set_minor_locator(MultipleLocator(TICKINDEX_MINOR_ECHEM_TIME))
    ax0.yaxis.set_major_locator(MultipleLocator(TICKINDEX_MAJOR_ECHEM_TIME))
    ax0.yaxis.set_minor_locator(MultipleLocator(TICKINDEX_MINOR_ECHEM_TIME))
    ax0.set_ylabel(TIMELABEL_ECHEM, fontsize=FONTSIZE_LABELS)
    cbar = ax0.figure.colorbar(im,
                               ax=ax0,
                               format=f'%.1f',
                               ticks=np.linspace(0, 1, 6))
    cbar.set_label(label=CBARLABEL, size=FONTSIZE_LABELS)
    plt.savefig(f"png/{basename}correlation_matrix_echem_t_x_v_abs_x={xmin}-{xmax}.png", bbox_inches="tight")
    plt.savefig(f"pdf/{basename}correlation_matrix_echem_t_x_v_abs_x={xmin}-{xmax}.pdf", bbox_inches="tight")
    plt.savefig(f"svg/{basename}correlation_matrix_echem_t_x_v_abs_x={xmin}-{xmax}.svg", bbox_inches="tight")
    plt.close()
    print(f"Plots with correlation matrix and electrochemistry together have "
          f"been saved to\nthe 'pdf'and 'png' folders.\n{80*'-'}")

    return None


def main():
    data_scatt_path = Path.cwd() / "data_scatt"
    data_echem_path = Path.cwd() / "data_echem"
    data_paths = [data_scatt_path, data_echem_path]
    png_path = Path.cwd() / "png"
    pdf_path = Path.cwd() / "pdf"
    svg_path = Path.cwd() / "svg"
    txt_path = Path.cwd() / "txt"
    output_paths = [png_path, pdf_path, svg_path, txt_path]
    for p in output_paths:
        if not p.exists():
            p.mkdir()
    print(f"{80*'-'}\
            \nPlease see the top of the 'pearson_echem_plotter.py' file to "
            "ensure that the\nright plotsettings are used.")
    exit = False
    for p in data_paths:
        if not p.exists():
            p.mkdir()
            print(f"{80*'-'}\nA folder called '{p.name}' has been created. ")
            exit = True
    if exit is True:
        print(f"{80*'-'}\nPleace place your data files in the appropriate "
              f"folders and rerun the program.\n{80*'-'}")
        sys.exit()
    scatt_files = list(data_scatt_path.glob("*.*"))
    echem_files = list(data_echem_path.glob("*.*"))
    scatt_exts = []
    for f in scatt_files:
        if not f.suffix in scatt_exts:
            scatt_exts.append(f.suffix)
    if len(scatt_exts) > 1:
        print(f"{80*'-'}\n{len(scatt_exts)} different file extensions were "
              f"found in the '{data_scatt_path.name}' folder.\nPlease revisit "
              f"the content of the folder such that only one file extension is "
              f"\npresent and rerun the program.\n{80*'-'}")
        sys.exit()
    if len(echem_files) > 1:
        print(f"{80*'-'}\n{len(echem_files)} echem files were found found in "
              f"the '{data_echem_path.name}' folder.\nPlease revisit the "
              f"content of the folder such that only one echem file is\npresent "
              f"and rerun the program.\n{80*'-'}")
        sys.exit()
    print(f"{80*'-'}\nInspecting whether any dummy scans needs to be "
          f"included...")
    basename = dummy_scan(data_scatt_path)
    print(f"{80*'-'}\nCollecting electrochemical data...")
    d_echem = dict_echem_extract(echem_files[0])
    print(f"Done collecting electrochemical data.\n{80*'-'}\nCalculating state "
          f"of charge for electrochemical data...")
    d_echem = x_from_dict_calculate(d_echem)
    print(f"Done calculating state of charge for electrochemical data.\n"
          f"{80*'-'}\nCollecting scattering data...")
    d_scatt = dict_scatt_extract(scatt_files)
    print(f"Done collecting scattering data.\n{80*'-'}\nConducting correlation "
          f"analysis for scattering data...")
    xmin = float(input(f"{80*'-'}\nPlease provide the minimum x-value to "
                       "include for each data file: "))
    xmax = float(input("Please provide the maximum x-value to include for "
                       "each data file: "))
    d_corr = dict(xmin=xmin, xmax=xmax)
    d_corr = pearson_correlation(scatt_files, d_scatt, d_corr)
    print("Electrochemistry inputs...\n\tTime units:\n\t\t0\tseconds\
          \n\t\t1\tminutes\n\t\t2\thours")
    time_unit = int(input("\tPlease provide the time units of the echem data "
                          "file: "))
    if time_unit == 0:
        d_echem["time"] = d_echem["time"] / 60**2
    elif time_unit == 1:
        d_echem["time"] = d_echem["time"] / 60
    voltage_min = float(input("\tPlease provide the minimum voltage to plot: "))
    voltage_max = float(input("\tPlease provide the maximum voltage to plot: "))
    print("\tVoltage labels...\n\t\t0\tV [V]\n\t\t1\tEwe vs. Li/Li+ [V]\
            \n\t\t2\tEwe vs. Na/Na+ [V]")
    ylabel_echem = int(input("\tPlease provide the desired label for the "
                             "voltage: "))
    if ylabel_echem == 0:
        ylabel_echem = r"$V$ $[\mathrm{V}]$"
        heightratio = [1, HEIGHTRATIO_V_LABEL]
    elif ylabel_echem == 1:
        ylabel_echem = r"$E_{\mathrm{we}}\,\mathrm{vs.}$ "
        ylabel_echem += r"$\mathrm{Li/Li^{+}}$ $[\mathrm{V}]$"
        heightratio = [1, HEIGHTRATIO_LI_LABEL]
    elif ylabel_echem == 2:
        ylabel_echem = r"$E_{\mathrm{we}}\,\mathrm{vs.}$ "
        ylabel_echem += r"$\mathrm{Na/Na^{+}}$ $[\mathrm{V}]$"
        heightratio = [1, HEIGHTRATIO_NA_LABEL]
    d_echem["voltage_min"], d_echem["voltage_max"] = voltage_min, voltage_max
    d_echem["ylabel_echem"] = ylabel_echem
    d_echem["basename"] = basename
    d_plot = dict(heightratio=heightratio)
    echem_plotter(d_echem)
    pearson_echem_plotter(d_corr, d_echem, d_plot)
    print("Good job! <(^^,)>")

    return None


if __name__ == "__main__":
    main()

# End of file.
