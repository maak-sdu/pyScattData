import sys
from pathlib import Path
import json
import numpy as np
from diffpy.utils.parsers.loaddata import loadData
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
try:
    from bg_mpl_stylesheet.bg_mpl_stylesheet import bg_mpl_style
    PLOT_STYLE = "found"
except ModuleNotFoundError:
    PLOT_STYLE = None


FIGSIZE = (8,6)
DPI = 600
FONTSIZE_LABELS = 20
FONTSIZE_TICKS = 16
MINOR_TICK_INDEX = 5
INDEX_LABEL = "Scan Number"
CBAR_TICKS = 5
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
XY_TYPES = ["I vs. Q [Å^-1]", "I vs. Q [nm^-1]", "I vs. 2theta [deg]",
            "G vs. r [Å]", "F vs. Q [Å^-1]", "y vs. x (general)"]
TIME_LABEL = r"$t$ $[\mathrm{h}]$"
VOLTAGE_LABELS = ["E_we vs. Li/Li^+", "E_we vs. Na/Na^+", "V [V]$"]
LINEWIDTH = 1
COLOR = "k"
HEIGHTRATIOS = [3,1]


def y_stack(xy_files):
    for i in range(len(xy_files)):
        print(f"\t{xy_files[i].name}")
        xy = loadData(str(xy_files[i]))
        x, y = xy[:,0], xy[:,1]
        if i == 0:
            y_array = y
        else:
            y_array = np.column_stack((y_array, y))

    return x, y_array


def echem_plot(echem_file, output_folders, vlabel_index):
    data = loadData(str(echem_file))
    time, voltage = data[:,0], data[:,1]
    time_min, time_max = np.amin(time), np.amax(time)
    voltage_min, voltage_max = np.amin(voltage), np.amax(voltage)
    voltage_range = voltage_max - voltage_min
    if vlabel_index == 0:
        vlabel = r"$E_{\mathrm{we}}$ vs. Li/Li$^{+} [\mathrm{V}]$"
    elif vlabel_index == 1:
        vlabel = r"$E_{\mathrm{we}}$ vs. Na/Na$^{+} [\mathrm{V}]$"
    elif vlabel_index == 2:
        vlabel = r"$V$ $[\mathrm{V}]$"
    if not isinstance(PLOT_STYLE, type(None)):
        plt.style.use(bg_mpl_style)
        plt.rcParams['xtick.labelbottom'] = True
        plt.rcParams['xtick.labeltop'] = False
    fig, ax = plt.subplots(dpi=DPI, figsize=FIGSIZE)
    ax.plot(time, voltage, c=COLOR, lw=LINEWIDTH)
    ax.set_xlabel(TIME_LABEL, fontsize=FONTSIZE_LABELS)
    ax.set_ylabel(vlabel, fontsize=FONTSIZE_LABELS)
    ax.set_xlim(time_min, time_max)
    ax.set_ylim(voltage_min, voltage_max)
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
    elif 1 < voltage_max <= 3:
        base_voltage = 0.5
    else:
        base_voltage = 1
    ax.xaxis.set_major_locator(MultipleLocator(base_time))
    ax.xaxis.set_minor_locator(MultipleLocator(base_time / MINOR_TICK_INDEX))
    ax.yaxis.set_major_locator(MultipleLocator(base_voltage))
    ax.yaxis.set_minor_locator(MultipleLocator(base_voltage / MINOR_TICK_INDEX))
    for folder in output_folders:
        output_path = Path.cwd() / folder / f"{echem_file.stem}.{folder}"
        plt.savefig(output_path, bbox_inches="tight")

    return None


def xy_overview(x, y, cmap, output_folders, basename_xy, xy_type_index,
                user_inputs):
    xmin, xmax = user_inputs["xmin"], user_inputs["xmax"]
    ymin, ymax = user_inputs["ymin"], user_inputs["ymax"]
    xrange, yrange = xmax - xmin, ymax - ymin
    scans = y.shape[-1]
    if xy_type_index in [0, 4]:
        xlabel = r"$Q$ $[\mathrm{\AA}^{-1}]$"
    elif xy_type_index == 1:
        xlabel = r"$Q$ $[\mathrm{nm}^{-1}]$"
    elif xy_type_index == 2:
        xlabel = r"$2\theta$ $[\degree]$"
    elif xy_type_index == 3:
        xlabel = r"$r$ $[\mathrm{\AA}]$"
    elif xy_type_index == 5:
        xlabel = r"$x$"
    if xy_type_index in [0, 1, 2]:
        ylabel = r"$I$ $[\mathrm{arb. u.}]$"
    elif xy_type_index == 3:
        ylabel = r"$G$ $[\mathrm{\AA}^{-2}]$"
    elif xy_type_index == 4:
        ylabel = r"$F$ $[\mathrm{\AA}^{-1}]$"
    elif xy_type_index == 5:
        ylabel = r"$y$"
    if scans <= 10:
        base_scan = 1
    elif 10 < scans <= 20:
        base_scan = 2
    elif 20 < scans <= 50:
        base_scan = 5
    else:
        base_scan = 10
    if xrange <= 10:
        base_scatt = 1
    elif 10 < xrange <= 20:
        base_scatt = 2
    elif 20 < xrange <= 50:
        base_scatt = 5
    else:
        base_scatt = 10
    if isinstance(xmin, type(None)):
        plot_xy_limits = None
        xmin, xmax, ymin, ymax = np.amin(x), np.amax(x), np.amin(y), np.amax(y)
        xrange, yrange = xmax - xmin, ymax - ymin
        xmin_index, xmax_index = 0, -1
    else:
        plot_xy_limits = "found"
        xrange, yrange = xmax - xmin, ymax - ymin
        for i in range(0, len(x)):
            xmin_index = None
            if xmin <= x[i]:
                xmin_index = i
                break
        if isinstance(xmin_index, type(None)):
            xmin_index = 0
        for i in range(xmin_index + 1, len(x)):
            xmax_index = None
            if xmax <= x[i]:
                xmax_index = i
                break
        if isinstance(xmax_index, type(None)):
            xmax_index = -1
    if not isinstance(plot_xy_limits, type(None)):
        y = y[xmin_index:xmax_index,:]
    y = np.flip(y, axis=0)
    if not isinstance(PLOT_STYLE, type(None)):
        plt.style.use(bg_mpl_style)
    fig, ax = plt.subplots(dpi=DPI, figsize=FIGSIZE)
    im = ax.imshow(y,
                   interpolation="nearest",
                   aspect="auto",
                   origin="lower",
                   vmin=ymin,
                   vmax=ymax,
                   extent=(0, scans, xmax, xmin),
                   cmap=cmap
              )
    if isinstance(PLOT_STYLE, type(None)):
        axs[0].xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    ax.tick_params(labeltop=True, labelbottom=False)
    ax.set_xlabel(INDEX_LABEL, fontsize=FONTSIZE_LABELS)
    ax.set_ylabel(xlabel, fontsize=FONTSIZE_LABELS)
    ax.xaxis.set_major_locator(MultipleLocator(base_scan))
    ax.xaxis.set_minor_locator(MultipleLocator(base_scan / MINOR_TICK_INDEX))
    ax.yaxis.set_major_locator(MultipleLocator(base_scatt))
    ax.yaxis.set_minor_locator(MultipleLocator(base_scatt / MINOR_TICK_INDEX))
    if not isinstance(plot_xy_limits, type(None)):
        cbar = ax.figure.colorbar(im,
                                  ax=ax,
                                  ticks=np.linspace(ymin, ymax, CBAR_TICKS)
                                  )
        if ymax > 100:
            cbar.formatter.set_powerlimits((0, 0))
    else:
        cbar = ax.figure.colorbar(im, ax=ax)
        if np.amax(y) > 100:
            cbar.formatter.set_powerlimits((0, 0))
    cbar.set_label(label=ylabel, size=FONTSIZE_LABELS)
    cbar.minorticks_on()
    for folder in output_folders:
        if isinstance(plot_xy_limits, type(None)):
            output_path = Path.cwd() / folder / f"{basename_xy}.{folder}"
        else:
            fname = f"{basename_xy}_x={xmin}-{xmax}_y={ymin}-{ymax}.{folder}"
            output_path = Path.cwd() / folder / fname
        plt.savefig(output_path, bbox_inches="tight")
    plt.close()

    return None


def xy_overview_echem(x, y, cmap, output_folders, basename_xy, xy_type_index,
                      user_inputs, echem_file):
    data_echem = loadData(str(echem_file))
    time, voltage = data_echem[:,0], data_echem[:,1]
    time_min, time_max = np.amin(time), np.amax(time)
    voltage_min, voltage_max = np.amin(voltage), np.amax(voltage)
    voltage_range = voltage_max - voltage_min
    if not isinstance(PLOT_STYLE, type(None)):
        plt.style.use(bg_mpl_style)
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
    elif 1 < voltage_max <= 3:
        base_voltage = 0.5
    else:
        base_voltage = 1
    xmin, xmax = user_inputs["xmin"], user_inputs["xmax"]
    ymin, ymax = user_inputs["ymin"], user_inputs["ymax"]
    vlabel_index = user_inputs["vlabel_index"]
    xrange, yrange = xmax - xmin, ymax - ymin
    scans = y.shape[-1]
    if xy_type_index in [0, 4]:
        xlabel = r"$Q$ $[\mathrm{\AA}^{-1}]$"
    elif xy_type_index == 1:
        xlabel = r"$Q$ $[\mathrm{nm}^{-1}]$"
    elif xy_type_index == 2:
        xlabel = r"$2\theta$ $[\degree]$"
    elif xy_type_index == 3:
        xlabel = r"$r$ $[\mathrm{\AA}]$"
    elif xy_type_index == 5:
        xlabel = r"$x$"
    if xy_type_index in [0, 1, 2]:
        ylabel = r"$I$ $[\mathrm{arb. u.}]$"
    elif xy_type_index == 3:
        ylabel = r"$G$ $[\mathrm{\AA}^{-2}]$"
    elif xy_type_index == 4:
        ylabel = r"$F$ $[\mathrm{\AA}^{-1}]$"
    elif xy_type_index == 5:
        ylabel = r"$y$"
    if vlabel_index == 0:
        vlabel = r"$E_{\mathrm{we}}$ vs." + "\n" + r"Li/Li$^{+} [\mathrm{V}]$"
    elif vlabel_index == 1:
        vlabel = r"$E_{\mathrm{we}}$vs." + "\n" + r"Na/Na$^{+} [\mathrm{V}]$"
    elif vlabel_index == 2:
        vlabel = r"$V$ $[\mathrm{V}]$"
    if scans <= 10:
        base_scan = 1
    elif 10 < scans <= 20:
        base_scan = 2
    elif 20 < scans <= 50:
        base_scan = 5
    else:
        base_scan = 10
    if xrange <= 10:
        base_scatt = 1
    elif 10 < xrange <= 20:
        base_scatt = 2
    elif 20 < xrange <= 50:
        base_scatt = 5
    else:
        base_scatt = 10
    if isinstance(xmin, type(None)):
        plot_xy_limits = None
        xmin, xmax, ymin, ymax = np.amin(x), np.amax(x), np.amin(y), np.amax(y)
        xrange, yrange = xmax - xmin, ymax - ymin
        xmin_index, xmax_index = 0, -1
    else:
        plot_xy_limits = "found"
        xrange, yrange = xmax - xmin, ymax - ymin
        for i in range(0, len(x)):
            xmin_index = None
            if xmin <= x[i]:
                xmin_index = i
                break
        if isinstance(xmin_index, type(None)):
            xmin_index = 0
        for i in range(xmin_index + 1, len(x)):
            xmax_index = None
            if xmax <= x[i]:
                xmax_index = i
                break
        if isinstance(xmax_index, type(None)):
            xmax_index = -1
    if not isinstance(plot_xy_limits, type(None)):
        y = y[xmin_index:xmax_index,:]
    y = np.flip(y, axis=0)
    if not isinstance(PLOT_STYLE, type(None)):
        plt.style.use(bg_mpl_style)
    fig, axs = plt.subplots(dpi=DPI, figsize=FIGSIZE, ncols=1, nrows=2,
                            gridspec_kw=dict(height_ratios=HEIGHTRATIOS,
                                            )
                            )
    im = axs[0].imshow(y,
                       interpolation="nearest",
                       aspect="auto",
                       origin="lower",
                       vmin=ymin,
                       vmax=ymax,
                       extent=(0, scans, xmax, xmin),
                       cmap=cmap,
                       )
    if isinstance(PLOT_STYLE, type(None)):
        axs[0].xaxis.tick_top()
    axs[0].xaxis.set_label_position('top')
    axs[0].tick_params(labeltop=True, labelbottom=False)
    axs[0].set_xlabel(INDEX_LABEL, fontsize=FONTSIZE_LABELS)
    axs[0].set_ylabel(xlabel, fontsize=FONTSIZE_LABELS)
    axs[0].xaxis.set_major_locator(MultipleLocator(base_scan))
    axs[0].xaxis.set_minor_locator(MultipleLocator(base_scan / MINOR_TICK_INDEX))
    axs[0].yaxis.set_major_locator(MultipleLocator(base_scatt))
    axs[0].yaxis.set_minor_locator(MultipleLocator(base_scatt / MINOR_TICK_INDEX))
    if HEIGHTRATIOS[0] / HEIGHTRATIOS[1] == 1:
        shrink = 0.455
    elif HEIGHTRATIOS[0] / HEIGHTRATIOS[1] == 3/2:
        shrink = 0.545
    elif HEIGHTRATIOS[0] / HEIGHTRATIOS[1] == 2:
        shrink = 0.605
    elif HEIGHTRATIOS[0] / HEIGHTRATIOS[1] == 3:
        shrink = 0.68
    if not isinstance(plot_xy_limits, type(None)):
        cbar = axs[0].figure.colorbar(im,
                                      ax=axs,
                                      ticks=np.linspace(ymin, ymax, CBAR_TICKS),
                                      anchor=(0,1),
                                      shrink=shrink,
                                      )
    else:
        cbar = axs[0].figure.colorbar(im, ax=ax)
    if np.amax(y) > 100:
        cbar.formatter.set_powerlimits((0, 0))
    cbar.set_label(label=ylabel, size=FONTSIZE_LABELS)
    cbar.minorticks_on()
    axs[1].plot(time, voltage, c=COLOR, lw=LINEWIDTH)
    axs[1].set_xlabel(TIME_LABEL, fontsize=FONTSIZE_LABELS)
    axs[1].set_ylabel(vlabel, fontsize=FONTSIZE_LABELS)
    axs[1].set_xlim(time_min, time_max)
    axs[1].set_ylim(voltage_min, voltage_max)
    axs[1].xaxis.set_major_locator(MultipleLocator(base_time))
    axs[1].xaxis.set_minor_locator(MultipleLocator(base_time / MINOR_TICK_INDEX))
    axs[1].yaxis.set_major_locator(MultipleLocator(base_voltage))
    axs[1].yaxis.set_minor_locator(MultipleLocator(base_voltage / MINOR_TICK_INDEX))
    for folder in output_folders:
        if isinstance(plot_xy_limits, type(None)):
            output_path = Path.cwd() / folder / f"{basename}.{folder}"
        else:
            fname = f"{basename_xy}_x={xmin}-{xmax}_y={ymin}-{ymax}_echem_"
            fname += f"heightratio={HEIGHTRATIOS[0]/HEIGHTRATIOS[1]}.{folder}"
            output_path = Path.cwd() / folder / fname
        plt.savefig(output_path, bbox_inches="tight")
    plt.close()

    return None


def main():
    print(f"{80*'-'}\nPlease see the top of this .py file for plot settings.")
    data_xy_path = Path.cwd() / "data_xy"
    data_echem_path = Path.cwd() / "data_echem"
    data_paths = [data_xy_path, data_echem_path]
    exit = False
    for p in data_paths:
        if not p.exists():
            p.mkdir()
            print(f"{80*'-'}\nA folder called '{p.name}' has been created.")
            if "xy" in p.name:
                print(f"Please place your xy data files there and rerun the "
                      f"code.")
                exit = True
            elif "echem" in p.name:
                print(f"Please place your echem file there and rerun the "
                      f"code.")
                exit = True
    if exit is True:
        print(f"{80*'-'}")
        sys.exit()
    xy_files = list(data_xy_path.glob("*.*"))
    echem_files = list(data_echem_path.glob("*.*"))
    file_lists = [xy_files, echem_files]
    for i in range(len(file_lists)):
        if len(file_lists[i]) == 0:
            folder = data_paths[i].name
            dtype = folder.split("_")[1]
            print(f"{80*'-'}\nNo files found in the '{folder}' folder.")
            if dtype == "xy":
                print(f"Please place your {dtype} files there and rerun the "
                      f"code.")
            elif dtype == "echem":
                print(f"Please place your {dtype} file there and rerun the "
                      f"code.")
            exit = True
    if exit is True:
        print(f"{80*'-'}")
        sys.exit()
    data_ext = []
    for e in xy_files:
        if not e.suffix in data_ext:
            data_ext.append(e.suffix)
    if len(data_ext) > 1:
        print(f"{80*'-'}\nMore than one file extension found in the 'data' "
              f"folder. Please review the files\nin the 'data' folder and rerun "
              f"the code.\n{80*'-'}")
        sys.exit()
    if len(echem_files) > 1:
        print(f"{80*'-'}\nMore than one file was found in the "
              f"'{data_echem_path.name}' folder. Please review the files "
              f"\nin the '{data_echem_path.name}' folder and rerun the code."
              f"\n{80*'-'}")
        sys.exit()
    print(f"{80*'-'}\nStacking y data...")
    x, y = y_stack(xy_files)
    print("Done stacking y data.")
    output_folders = ["pdf", "png", "svg"]
    for folder in output_folders:
        if not (Path.cwd() / folder).exists():
            (Path.cwd() / folder).mkdir()
    if isinstance(PLOT_STYLE, type(None)):
        print(f"{80*'-'}\n'bg_mpl_stylesheet' module not found. Consider "
              f"installing this to your current\nconda environment:\n\tconda "
              f"install -c conda-forge bg-mpl-stylesheets")
    user_input_path = Path.cwd() / "user_inputs.json"
    if not user_input_path.exists():
        print(f"{80*'-'}\nUser inputs for overview plot...\ncmaps available:")
        cmap_keys = list(CMAPS.keys())
        for i in range(len(cmap_keys)):
            print(f"\t{i}\t{CMAPS[cmap_keys[i]]}")
        cmap_input = input(f"Please provide the index of the desired cmap: ")
        cmap = CMAPS[int(cmap_input)]
        print(f"{80*'-'}\nData type...\n\tindex\ttype")
        for i in range(len(XY_TYPES)):
            print(f"\t{i}\t{XY_TYPES[i]}")
        xy_type_index = int(input("Please indicate the type of xy data that you "
                                  "are plotting: "))
        xmin = float(input(f"{80*'-'}\nPlease provide the minimum x-value to "
                           f"plot for the xy data: "))
        xmax = float(input("Please provide the maximum x-value to plot for the "
                           "xy data: "))
        ymin = float(input("Please provide the maximum y-value to plot for the "
                           "xy data: "))
        ymax = float(input("Please provide the maximum y-value to plot for the "
                           "xy data: "))
        print(f"{80*'-'}\nVoltage labels...")
        for i in range(len(VOLTAGE_LABELS)):
            print(f"\t{i}\t{VOLTAGE_LABELS[i]}")
        vlabel_index = int(input("Please provide the index for the voltage "
                                 "label: "))
        user_inputs = dict(cmap=cmap,
                           xytype_index=xy_type_index,
                           xmin=xmin,
                           xmax=xmax,
                           ymin=ymin,
                           ymax=ymax,
                           vlabel_index=vlabel_index,
                           )
        with user_input_path.open(mode="w") as o:
            json.dump(user_inputs, o)
    else:
        with user_input_path.open(mode="r") as f:
            user_inputs = json.load(f)
        print(f"{80*'-'}\nThe following values were read from "
              f" {user_input_path.name}:")
        for k,v in user_inputs.items():
            if not k == "xytype_index":
                print(f"\t{k}\t{v}")
            else:
                print(f"\t{k}\t{XY_TYPES[v]}")
        plot_input = input(f"{80*'-'}\nDo you want to plot using the default "
                           f"plot settings? ([y]/n): ")
        if plot_input.lower() in ["", "y"]:
            cmap = user_inputs["cmap"]
            xy_type_index = int(user_inputs["xytype_index"])
            xmin = float(user_inputs["xmin"])
            xmax = float(user_inputs["xmax"])
            ymin = float(user_inputs["ymin"])
            ymax = float(user_inputs["ymax"])
            vlabel_index = int(user_inputs["vlabel_index"])
        else:
            print(f"{80*'-'}\ncmaps available:")
            cmap_keys = list(CMAPS.keys())
            for i in range(len(cmap_keys)):
                print(f"\t{i}\t{CMAPS[cmap_keys[i]]}")
            plot_input = input(f"Please provide the index of the desired cmap: ")
            cmap = CMAPS[int(plot_input)]
            print(f"{80*'-'}\nData type...\n\tindex\ttype")
            for i in range(len(XY_TYPES)):
                print(f"\t{i}\t{XY_TYPES[i]}")
            xy_type_index = int(input("Please indicate the type of xy data "
                                      "that you are plotting: "))
            xmin = float(input(f"{80*'-'}\nPlease provide the minimum x-value "
                               f"to plot for the xy data: "))
            xmax = float(input("Please provide the maximum x-value to plot for "
                               "the xy data: "))
            ymin = float(input("Please provide the maximum y-value to plot for "
                               "the xy data: "))
            ymax = float(input("Please provide the maximum y-value to plot for "
                               "the xy data: "))
            print(f"{80*'-'}\nVoltage labels...")
            for i in range(len(VOLTAGE_LABELS)):
                print(f"\t{i}\t{VOLTAGE_LABELS[i]}")
            vlabel_index = int(input("Please provide type of voltage label: "))
            user_inputs = dict(cmap=cmap,
                               xytype_index=xy_type_index,
                               xmin=xmin,
                               xmax=xmax,
                               ymin=ymin,
                               ymax=ymax,
                               vlabel_index=vlabel_index,
                               )
            with user_input_path.open(mode="w") as o:
                json.dump(user_inputs, o)
    basename_xy = xy_files[0].stem
    print(f"{80*'-'}\nPlotting echem...")
    echem_plot(echem_files[0], output_folders, vlabel_index)
    print(f"Done plotting echem.\n{80*'-'}\nMaking overview plot...")
    xy_overview(x, y, cmap, output_folders, basename_xy, xy_type_index,
                user_inputs)
    print(f"Done plotting xy_overview.\n{80*'-'}\nPlotting xy_overview and "
          f"echem together...")
    xy_overview_echem(x, y, cmap, output_folders, basename_xy, xy_type_index,
                      user_inputs, echem_files[0])
    print(f"Done making xy_overview_echem plot. Please see the "
          f"{output_folders} folders.\n{80*'-'}")
    # xy_limits_plot_req = input("Do you want to make an additional overview plot "
    #                         "with customized xy_limits? ([y]/n): ")
    # while xy_limits_plot_req.lower() in ["", "y"]:
    #     xy_limits["xmin"] = float(input("Please state the minimum x value: "))
    #     xy_limits["xmax"] = float(input("Please state the maximum x value: "))
    #     xy_limits["ymin"] = float(input("Please state the minimum y value: "))
    #     xy_limits["ymax"] = float(input("Please state the maximum y value: "))
    #     print(f"{80*'-'}\nMaking overview plot in customized range...")
    #     xy_overview(x, y, cmap, output_folders, basename, xy_type_index, xy_limits)
    #     print(f"Done making overview plot. Please see the {output_folders} folders."
    #           f"\n{80*'-'}")
    #     xy_limits_plot_req = input("Do you want to make an additional overview "
    #                             "plot with customized xy_limits? ([y]/n): ")
    # print(f"{80*'-'}\nGood luck with your plots! (^^,)")

    return None


if __name__ == "__main__":
    main()

# End of file.
