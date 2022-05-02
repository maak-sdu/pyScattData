import sys
import time
from pathlib import Path
import numpy as np
from diffpy.utils.parsers.loaddata import loadData
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.gridspec import GridSpec
try:
    from bg_mpl_stylesheet.bg_mpl_stylesheet import bg_mpl_style
    PLOT_STYLE = "found"
except ModuleNotFoundError:
    PLOT_STYLE = None

# Plot-specific inputs
DPI = 600
FIGSIZE = (8,4)
AXESLABEL = 'Scan Number'
CBARLABEL = r'$r_{\mathrm{Pearson}}$'
TICKINDEX_MAJOR = 10
TICKINDEX_MINOR = 1
FONTSIZE_TICKS = 14
FONTSIZE_LABELS = 20
CMAP = 'YlOrRd'


# CBAR_REL_DICT = dict(
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
                    #  vmin = 0.825,
                    #  decimals = 3,
                    #  ticks = np.linspace(0.825, 1, int((1-0.825)/0.025)+1)
                    # )
# print(CBAR_REL_DICT["ticks"])
# sys.exit()
CBAR_REL_DICT = None

XLABEL_ECHEM = r"$t$ $[\mathrm{h}]$"

SHRINK_V_LABEL = 0.76
HEIGHTRATIO_V_LABEL = 0.25
SHRINK_LI_LABEL = 0.68
HEIGHTRATIO_LI_LABEL = 0.4
SHRINK_NA_LABEL = 0.635
HEIGHTRATIO_NA_LABEL = 0.5

TICKINDEX_MAJOR_ECHEM_X = 5
TICKINDEX_MINOR_ECHEM_X = 1
TICKINDEX_MAJOR_ECHEM_Y = 0.5
TICKINDEX_MINOR_ECHEM_Y = 0.1

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


def pearson_correlation(data_ext):
    xmin = float(input("\tPlease provide the minimum x-value to include for "
                       "each data file: "))
    xmax = float(input("\tPlease provide the maximum x-value to include for "
                       "each data file: "))
    print(f"{80*'-'}\nConducting the Pearson correlation analysis...")
    datafiles = (Path.cwd() / 'data').glob(f'*{data_ext}')
    data_dict = {}
    for f in datafiles:
        scan = int(str(f.stem).split('_')[-1])
        filename = ''
        for e in str(f.stem).split("_")[0:-1]:
            filename += f"{e}_"
        with open(f) as input_file:
            data = loadData(str(f))
        x_data, y_data = data[:,0], data[:,1]
        xmin_index, xmax_index = 0, len(x_data) - 1
        for i in range(len(x_data)):
            if x_data[i] >= xmin:
                xmin_index = i
                break
        for i in range(len(x_data)):
            if x_data[i] >= xmax:
                xmax_index = i
                break
        if xmax_index == len(x_data) - 1:
            data_dict[scan] = dict(x = x_data[xmin_index::],
                                   y = y_data[xmin_index::])
        else:
            data_dict[scan] = dict(x = x_data[xmin_index:xmax_index+1],
                                   y = y_data[xmin_index:xmax_index+1])
    scanlist = list(data_dict.keys())
    missing_scans = []
    for i in range(1, len(scanlist)):
        if scanlist[i] - scanlist[i-1] != 1:
            for j in range(1, scanlist[i] - scanlist[i-1]):
                missing_scans.append(i+j)
    if len(missing_scans) > 0:
        print(f"\nMissing scan(s) {missing_scans}. Consider including 'blank' "
               "scan(s) with this(these) scan number(s).\n")
    startscan, endscan = scanlist[0] - 1, scanlist[-1]
    x_list = [data_dict[k]['x'] for k in data_dict]
    y_list = [data_dict[k]['y'] for k in data_dict]
    y_list = np.array(y_list)
    keys = [k for k in data_dict]
    keys_str = [str(k) for k in data_dict]
    corr_matrix = np.corrcoef(y_list).round(decimals=6)
    corr_matrix_str = corr_matrix.astype(str)
    header_rows = np.array([keys]).astype(str)
    header_columns = header_rows.reshape(-1,1)
    corr_matrix_header = np.vstack((header_rows, corr_matrix))
    corr_matrix_txt = np.vstack((np.array(['']).astype(str), header_columns))
    for i in range(np.shape(corr_matrix_header)[1]):
        corr_matrix_txt = np.column_stack((corr_matrix_txt, corr_matrix_header[:,i]))
    print(f"{80*'-'}\nSaving txt file containing matrix to the 'txt' folder...")
    np.savetxt(f'txt/{filename}correalation_matrix_x={xmin}-{xmax}.txt',
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
    ax.xaxis.set_major_locator(ticker.MultipleLocator(TICKINDEX_MAJOR))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(TICKINDEX_MINOR))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(TICKINDEX_MAJOR))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(TICKINDEX_MINOR))
    # ax.xaxis.tick_top()
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
    plt.savefig(f'png/{filename}correlation_matrix_rel_x={xmin}-{xmax}.png',
                bbox_inches='tight')
    plt.savefig(f'pdf/{filename}correlation_matrix_rel_x={xmin}-{xmax}.pdf',
                bbox_inches='tight')
    plt.savefig(f'svg/{filename}correlation_matrix_rel_x={xmin}-{xmax}.svg',
                bbox_inches='tight')
    plt.close()
    print("\tcorrelation matrix on absolute scale...")
    fig, ax = plt.subplots(dpi=DPI, figsize=FIGSIZE)
    im = ax.imshow(corr_matrix,
                   cmap=CMAP,
                   vmin=0, vmax=1,
                   extent=(startscan, endscan, endscan, startscan))
    ax.grid(False)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(TICKINDEX_MAJOR))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(TICKINDEX_MINOR))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(TICKINDEX_MAJOR))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(TICKINDEX_MINOR))
    # ax.xaxis.tick_top()
    ax.set_xlabel(AXESLABEL, fontsize=FONTSIZE_LABELS)
    ax.set_ylabel(AXESLABEL, fontsize=FONTSIZE_LABELS)
    ax.xaxis.set_label_position('top')
    ax.tick_params(axis='both', labelsize=FONTSIZE_TICKS)
    ax.tick_params(axis="x", bottom=True, top=True, labelbottom=False,
                   labeltop=True)
    cbar = ax.figure.colorbar(im, ax=ax, format='%.1f')
    cbar.set_label(label=CBARLABEL, size=FONTSIZE_LABELS)
    plt.savefig(f'png/{filename}correlation_matrix_abs_x={xmin}-{xmax}.png',
                bbox_inches='tight')
    plt.savefig(f'pdf/{filename}correlation_matrix_abs_x={xmin}-{xmax}.pdf',
                bbox_inches='tight')
    plt.savefig(f'svg/{filename}correlation_matrix_abs_x={xmin}-{xmax}.svg',
                bbox_inches='tight')
    plt.close()
    print(f"\nPearson correlation analysis completed.\n{80*'-'}\nFigures of "
          f"the Pearson correlation matrix have been saved to the pdf and png "
          f"\nfolders. A .txt file with the correlation matrix has been saved "
          f"to the txt folder.\n{80*'-'}")

    return corr_matrix, scanlist, filename, xmin, xmax


def dummy_scan(data_ext):
    if not (Path.cwd() / 'data').exists():
        print(f"{80*'-'}\nPlease create a folder named 'data' and place your "
              f"data files there.\n{80*'-'}")
        sys.exit()
    files = list((Path.cwd() / 'data').glob('*.*'))
    if len(files) == 0:
        print(f"{80*'-'}\nPlease place your data files in the 'data' folder.\
              \n{80*'-'}")
        sys.exit()
    files = list((Path.cwd() / 'data').glob(f'*{data_ext}'))
    filename = ''
    for e in str(files[0].stem).split("_")[0:-1]:
        filename += f"{e}_"
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
            x, y = data[:,0], data[:,1]
        y_dummy = np.zeros(len(x))
        xy_dummy = np.column_stack((x, y_dummy))
        for e in missing_scans:
            if file_ext == '.gr':
                np.savetxt(f"data/{filename}{e}{file_ext}", xy_dummy,
                           fmt='%.2f')
            else:
                np.savetxt(f"data/{filename}{e}{file_ext}", xy_dummy,
                           fmt='%.6f')
        print(f"\t\tThe following dummy scans have been saved to the "
               "'data' directory:")
        for e in missing_scans:
            print(f"\t\t\t{filename}{e}{file_ext}")

        return None


def echem_collector(echemfile):
    print("Collecting electrochemical data...")
    data = np.loadtxt(echemfile)
    time, voltage = data[:,0], data[:,1]
    print(f"Electrochemical data collected.\n{80*'-'}")

    return time, voltage


def echem_plotter(time, voltage, filename, voltage_min, voltage_max,
                  ylabel_echem):
    print(f"{80*'-'}\nPlotting electrochemistry...")
    if not isinstance(PLOT_STYLE, type(None)):
        plt.style.use(bg_mpl_style)
    fig, ax = plt.subplots(dpi=DPI, figsize=FIGSIZE)
    plt.plot(time, voltage, c=COLORS[1])
    plt.xlim(np.amin(time), np.amax(time))
    plt.ylim(voltage_min, voltage_max)
    ylabel_echem = ylabel_echem.replace("\n", " ")
    plt.xlabel(XLABEL_ECHEM, fontsize=FONTSIZE_LABELS)
    plt.ylabel(ylabel_echem, fontsize=FONTSIZE_LABELS)
    ax.tick_params(axis="both", labelsize=FONTSIZE_TICKS)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(TICKINDEX_MAJOR_ECHEM_X))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(TICKINDEX_MINOR_ECHEM_X))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(TICKINDEX_MAJOR_ECHEM_Y))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(TICKINDEX_MINOR_ECHEM_Y))
    plt.savefig(f"png/{filename}echem.png", bbox_inches="tight")
    plt.savefig(f"pdf/{filename}echem.pdf", bbox_inches="tight")
    plt.savefig(f"svg/{filename}echem.svg", bbox_inches="tight")
    plt.close()
    print(f"Plot with electrochemistry saved to the 'pdf' and 'png' folders.\
            \n{80*'-'}")

    return None


def pearson_echem_plotter(corr_matrix, scanlist, time, voltage, filename,
                          voltage_min, voltage_max, xmin, xmax,
                          ylabel_echem, heightratio, shrink):
    startscan, endscan = scanlist[0] - 1, scanlist[-1]
    print("Plotting correlation matrix and electrochemistry together..."
          "\n\ton absolute scale")
    if not isinstance(PLOT_STYLE, type(None)):
        plt.style.use(bg_mpl_style)
    fig = plt.figure(dpi=DPI, figsize=(6,6))
    # fig, axs = plt.subplots(dpi=DPI, figsize=(6,6), nrows=2, ncols=1,
    #                         gridspec_kw={'height_ratios': heightratio,
    #                                      # 'width_ratios': [1, 0.1]
    #                                      }
    #                         )
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
    ax0.xaxis.set_major_locator(ticker.MultipleLocator(TICKINDEX_MAJOR))
    ax0.xaxis.set_minor_locator(ticker.MultipleLocator(TICKINDEX_MINOR))
    ax0.yaxis.set_major_locator(ticker.MultipleLocator(TICKINDEX_MAJOR))
    ax0.yaxis.set_minor_locator(ticker.MultipleLocator(TICKINDEX_MINOR))
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
    ax1.xaxis.set_major_locator(ticker.MultipleLocator(TICKINDEX_MAJOR_ECHEM_X))
    ax1.xaxis.set_minor_locator(ticker.MultipleLocator(TICKINDEX_MINOR_ECHEM_X))
    ax1.yaxis.set_major_locator(ticker.MultipleLocator(TICKINDEX_MAJOR_ECHEM_Y))
    ax1.yaxis.set_minor_locator(ticker.MultipleLocator(TICKINDEX_MINOR_ECHEM_Y))
    # plt.subplots_adjust(hspace=0.1)
    cbar = plt.colorbar(im,
                        ax=ax0,
                        anchor=(0,1),
                        # shrink=shrink,
                        # format='%.1f'
                        )
    cbar.set_label(label=CBARLABEL, size=FONTSIZE_LABELS)
    plt.savefig(f'png/{filename}correlation_matrix_echem_abs_x={xmin}-{xmax}.png',
                bbox_inches='tight')
    plt.savefig(f'pdf/{filename}correlation_matrix_echem_abs_x={xmin}-{xmax}.pdf',
                bbox_inches='tight')
    plt.savefig(f'svg/{filename}correlation_matrix_echem_abs_x={xmin}-{xmax}.svg',
                bbox_inches='tight')
    plt.close()
    print("\ton relative scale")
    fig = plt.figure(dpi=DPI, figsize=(6,6))
    # fig, axs = plt.subplots(dpi=DPI, figsize=(6,6), nrows=2, ncols=1,
    #                         gridspec_kw={'height_ratios': heightratio,
    #                                      # 'width_ratios': [1, 0.1]
    #                                      }
    #                         )
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
    ax0.xaxis.set_major_locator(ticker.MultipleLocator(TICKINDEX_MAJOR))
    ax0.xaxis.set_minor_locator(ticker.MultipleLocator(TICKINDEX_MINOR))
    ax0.yaxis.set_major_locator(ticker.MultipleLocator(TICKINDEX_MAJOR))
    ax0.yaxis.set_minor_locator(ticker.MultipleLocator(TICKINDEX_MINOR))
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
    ax1.xaxis.set_major_locator(ticker.MultipleLocator(TICKINDEX_MAJOR_ECHEM_X))
    ax1.xaxis.set_minor_locator(ticker.MultipleLocator(TICKINDEX_MINOR_ECHEM_X))
    ax1.yaxis.set_major_locator(ticker.MultipleLocator(TICKINDEX_MAJOR_ECHEM_Y))
    ax1.yaxis.set_minor_locator(ticker.MultipleLocator(TICKINDEX_MINOR_ECHEM_Y))
    # plt.subplots_adjust(hspace=0.1
    if not isinstance(CBAR_REL_DICT, type(None)):
        cbar = plt.colorbar(im,
                            ax=ax0,
                            anchor=(0,1),
                            # shrink=shrink,
                            format=f'%.{CBAR_REL_DICT["decimals"]}f',
                            ticks=CBAR_REL_DICT["ticks"])
    else:
        cbar = plt.colorbar(im,
                            ax=ax0,
                            anchor=(0,1),
                            # shrink=shrink,
                            # format='%.3f'
                            )
    cbar.set_label(label=CBARLABEL, size=FONTSIZE_LABELS)
    plt.savefig(f'png/{filename}correlation_matrix_echem_rel_x={xmin}-{xmax}.png',
                bbox_inches='tight')
    plt.savefig(f'pdf/{filename}correlation_matrix_echem_rel_x={xmin}-{xmax}.pdf',
                bbox_inches='tight')
    plt.savefig(f'svg/{filename}correlation_matrix_echem_rel_x={xmin}-{xmax}.svg',
                bbox_inches='tight')
    plt.close()
    print(f"Plots with correlation matrix and electrochemistry together have "
          f"been saved to\nthe 'pdf'and 'png' folders.\n{80*'-'}")

    return None


def main():
    png_path = Path.cwd() / 'png'
    pdf_path = Path.cwd() / 'pdf'
    svg_path = Path.cwd() / "svg"
    txt_path = Path.cwd() / 'txt'
    PATHS = [png_path, pdf_path, svg_path, txt_path]
    for path in PATHS:
        if not path.exists():
            path.mkdir()
    print(f"{80*'-'}\
            \nPlease see the top of the 'pearson_echem_plotter.py' file to "
            "ensure that the\nright plotsettings are used.")
    if not (Path.cwd() / 'data').exists():
        print(f"{80*'-'}\nPlease make a folder called 'data' and put your "
              f"datafiles into this.\n{80*'-'}")
        sys.exit()
    data_ext = input(f"{80*'-'}\nCorrelation analysis inputs...\
                     \n\tPlease provide the file extension for the datafiles "
                     "(e.g. '.gr'): ")
    dummy_scan(data_ext)
    corr_matrix, scanlist, filename, xmin, xmax = pearson_correlation(data_ext)
    echemfile = list((Path.cwd() / "data").glob('*.txt'))[0]
    time, voltage = echem_collector(echemfile)
    print("Electrochemistry inputs...\n\tTime units:\n\t\t0\tseconds\
          \n\t\t1\tminutes\n\t\t2\thours")
    time_unit = int(input("\tPlease provide the time units of the echem data "
                          "file: "))
    if time_unit == 0:
        time = time / 60**2
    elif time_unit == 1:
        time = time / 60
    voltage_min = float(input("\tPlease provide the minimum voltage to plot: "))
    voltage_max = float(input("\tPlease provide the maximum voltage to plot: "))
    print("\tVoltage labels...\n\t\t0\tV [V]\n\t\t1\tEwe vs. Li/Li+ [V]\
            \n\t\t2\tEwe vs. Na/Na+ [V]")
    ylabel_echem = int(input("\tPlease provide the desired label for the "
                             "voltage: "))
    if ylabel_echem == 0:
        ylabel_echem = r"$V$ $[\mathrm{V}]$"
        heightratio = [1, HEIGHTRATIO_V_LABEL]
        shrink = SHRINK_V_LABEL
    elif ylabel_echem == 1:
        ylabel_echem = r"$E_{\mathrm{we}}\,\mathrm{vs.}$" + "\n"
        ylabel_echem += r"$\mathrm{Li/Li^{+}}$ $[\mathrm{V}]$"
        heightratio = [1, HEIGHTRATIO_LI_LABEL]
        shrink = SHRINK_LI_LABEL
    elif ylabel_echem == 2:
        ylabel_echem = r"$E_{\mathrm{we}}\,\mathrm{vs.}$" + "\n"
        ylabel_echem += r"$\mathrm{Na/Na^{+}}$ $[\mathrm{V}]$"
        heightratio = [1, HEIGHTRATIO_NA_LABEL]
        shrink = SHRINK_NA_LABEL
    echem_plotter(time, voltage, filename, voltage_min, voltage_max,
                  ylabel_echem)
    pearson_echem_plotter(corr_matrix, scanlist, time, voltage, filename,
                          voltage_min, voltage_max, xmin, xmax,
                          ylabel_echem, heightratio, shrink)
    print("Good job! <(^^,)>")

    return None


if __name__ == "__main__":
    main()

# End of file.
