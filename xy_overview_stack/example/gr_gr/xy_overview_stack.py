import sys
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from diffpy.utils.parsers.loaddata import loadData
import matplotlib.ticker as ticker
try:
    from bg_mpl_stylesheet.bg_mpl_stylesheet import bg_mpl_style
    PLOT_STYLE = "found"
except ModuleNotFoundError:
    PLOT_STYLE = None


FIGSIZE = (8,4)
DPI = 600
INDEX_LABEL = "Scan Number"
FONTSIZE_LABELS = 20
FONTSIZE_TICKS = 16
MINOR_TICK_INDEX = 5
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
XY_TYPE_INDEX = 0
XMIN = 0
XMAX = 10
YMIN = 0
YMAX = 1
HSPACE = 0.2


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


def xy_overview(x, y, output_folders, basename, user_inputs, pos):
    dpi = user_inputs["dpi"]
    figsize = (user_inputs["figsize"][0], user_inputs["figsize"][1] / 2)
    fontsize_labels = user_inputs["fontsize_labels"]
    fontsize_ticks = user_inputs["fontsize_ticks"]
    cmap = user_inputs[f"cmap_{pos}"]
    cbar_ticks = user_inputs[f"cbar_ticks_{pos}"]
    minor_tick_index = user_inputs[f"minor_tick_index_{pos}"]
    index_label = user_inputs[f"index_label_{pos}"]
    xy_type_index = user_inputs[f"xytype_index_{pos}"]
    xmin, xmax = user_inputs[f"xmin_{pos}"], user_inputs[f"xmax_{pos}"]
    ymin, ymax = user_inputs[f"ymin_{pos}"], user_inputs[f"ymax_{pos}"]
    xrange, yrange = xmax - xmin, ymax - ymin
    xmin_index, xmax_index = None, None
    for i in range(0, len(x)):
        if xmin <= x[i]:
            xmin_index = i
            break
    if isinstance(xmin_index, type(None)):
        xmin_index = 0
    for i in range(xmin_index + 1, len(x)):
        if xmax <= x[i]:
            xmax_index = i
            break
    if isinstance(xmax_index, type(None)):
        xmax_index = len(x)
    y = y[xmin_index:xmax_index,:]
    scans = y.shape[-1]
    y = np.flip(y, axis=0)
    if int(xy_type_index) in [0, 4]:
        xlabel = r"$Q$ $[\mathrm{\AA}^{-1}]$"
    elif int(xy_type_index) == 1:
        xlabel = r"$Q$ $[\mathrm{nm}^{-1}]$"
    elif int(xy_type_index) == 2:
        xlabel = r"$2\theta$ $[\degree]$"
    elif int(xy_type_index) == 3:
        xlabel = r"$r$ $[\mathrm{\AA}]$"
    elif int(xy_type_index) == 5:
        xlabel = r"$x$"
    if int(xy_type_index) in [0, 1, 2]:
        ylabel = r"$I$ $[\mathrm{arb. u.}]$"
    elif int(xy_type_index) == 3:
        ylabel = r"$G$ $[\mathrm{\AA}^{-2}]$"
    elif int(xy_type_index) == 4:
        ylabel = r"$F$ $[\mathrm{\AA}^{-1}]$"
    elif int(xy_type_index) == 5:
        ylabel = r"$y$"
    if not isinstance(PLOT_STYLE, type(None)):
        plt.style.use(bg_mpl_style)
        plt.rcParams['xtick.labelbottom'] = False
        plt.rcParams['xtick.labeltop'] = True
    fig, ax = plt.subplots(dpi=DPI, figsize=figsize)
    im = ax.imshow(y,
                   interpolation="nearest",
                   aspect="auto",
                   origin="lower",
                   vmin=ymin,
                   vmax=ymax,
                   extent=(0, scans, xmax, xmin),
                   cmap=cmap)
    if isinstance(PLOT_STYLE, type(None)):
        ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    ax.set_xlabel(index_label, fontsize=fontsize_labels)
    ax.set_ylabel(xlabel, fontsize=fontsize_labels)
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
    ax.xaxis.set_major_locator(ticker.MultipleLocator(base_scan))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(base_scan / minor_tick_index))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(base_scatt))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(base_scatt / minor_tick_index))
    cbar = ax.figure.colorbar(im,
                              ax=ax,
                              ticks=np.linspace(ymin, ymax, cbar_ticks)
                              )
    if ymax > 100:
        cbar.formatter.set_powerlimits((0, 0))
    cbar.set_label(label=ylabel, size=fontsize_labels)
    cbar.minorticks_on()
    for folder in output_folders:
        fname = f"{basename}_x={xmin}-{xmax}_y={ymin}-{ymax}.{folder}"
        output_path = Path.cwd() / folder / fname
        plt.savefig(output_path, bbox_inches="tight")
    plt.close()

    return None


def xy_overview_stack(xy_dict, output_folders, basename, user_inputs):
    x_upper, y_upper = xy_dict["x_upper"], xy_dict["y_upper"]
    x_lower, y_lower = xy_dict["x_lower"], xy_dict["y_lower"]
    dpi, figsize = user_inputs["dpi"], user_inputs["figsize"]
    fontsize_labels = user_inputs["fontsize_labels"]
    fontsize_ticks = user_inputs["fontsize_ticks"]
    cmap_upper = user_inputs["cmap_upper"]
    cmap_lower = user_inputs["cmap_lower"]
    cbar_ticks_upper = user_inputs["cbar_ticks_upper"]
    cbar_ticks_lower = user_inputs["cbar_ticks_lower"]
    minor_tick_index_upper = user_inputs["minor_tick_index_upper"]
    minor_tick_index_lower = user_inputs["minor_tick_index_lower"]
    index_label_upper = user_inputs["index_label_upper"]
    index_label_lower = user_inputs["index_label_lower"]
    xy_type_index_upper = user_inputs["xytype_index_upper"]
    xy_type_index_lower = user_inputs["xytype_index_lower"]
    xmin_upper= user_inputs["xmin_upper"]
    xmax_upper = user_inputs["xmax_upper"]
    ymin_upper = user_inputs["ymin_upper"]
    ymax_upper = user_inputs["ymax_upper"]
    xmin_lower= user_inputs["xmin_lower"]
    xmax_lower = user_inputs["xmax_lower"]
    ymin_lower = user_inputs["ymin_lower"]
    ymax_lower = user_inputs["ymax_lower"]
    hspace = user_inputs["hspace"]
    xrange_upper = xmax_upper - xmin_upper
    yrange_upper = ymax_upper - ymin_upper
    xrange_lower = xmax_lower - xmin_lower
    yrange_lower = ymax_lower - ymin_lower
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
    y_upper = np.flip(y_upper[xmin_index_upper:xmax_index_upper,:], axis=0)
    y_lower = np.flip(y_lower[xmin_index_lower:xmax_index_lower,:], axis=0)
    scans_upper = y_upper.shape[-1]
    scans_lower = y_lower.shape[-1]
    if int(xy_type_index_upper) in [0, 4]:
        xlabel_upper = r"$Q$ $[\mathrm{\AA}^{-1}]$"
    elif int(xy_type_index_upper) == 1:
        xlabel_upper = r"$Q$ $[\mathrm{nm}^{-1}]$"
    elif int(xy_type_index_upper) == 2:
        xlabel_upper = r"$2\theta$ $[\degree]$"
    elif int(xy_type_index_upper) == 3:
        xlabel_upper = r"$r$ $[\mathrm{\AA}]$"
    elif int(xy_type_index_upper) == 5:
        xlabel_upper = r"$x$"
    if int(xy_type_index_upper) in [0, 1, 2]:
        ylabel_upper = r"$I$ $[\mathrm{arb. u.}]$"
    elif int(xy_type_index_upper) == 3:
        ylabel_upper = r"$G$ $[\mathrm{\AA}^{-2}]$"
    elif int(xy_type_index_upper) == 4:
        ylabel_upper = r"$F$ $[\mathrm{\AA}^{-1}]$"
    elif int(xy_type_index_upper) == 5:
        ylabel_upper = r"$y$"
    if int(xy_type_index_lower) in [0, 4]:
        xlabel_lower = r"$Q$ $[\mathrm{\AA}^{-1}]$"
    elif int(xy_type_index_lower) == 1:
        xlabel_lower = r"$Q$ $[\mathrm{nm}^{-1}]$"
    elif int(xy_type_index_lower) == 2:
        xlabel_lower = r"$2\theta$ $[\degree]$"
    elif int(xy_type_index_lower) == 3:
        xlabel_lower = r"$r$ $[\mathrm{\AA}]$"
    elif int(xy_type_index_lower) == 5:
        xlabel_lower = r"$x$"
    if int(xy_type_index_lower) in [0, 1, 2]:
        ylabel_lower = r"$I$ $[\mathrm{arb. u.}]$"
    elif int(xy_type_index_lower) == 3:
        ylabel_lower = r"$G$ $[\mathrm{\AA}^{-2}]$"
    elif int(xy_type_index_lower) == 4:
        ylabel_lower = r"$F$ $[\mathrm{\AA}^{-1}]$"
    elif int(xy_type_index_lower) == 5:
        ylabel_lower = r"$y$"
    if not isinstance(PLOT_STYLE, type(None)):
        plt.style.use(bg_mpl_style)
        plt.rcParams['xtick.labelbottom'] = False
        plt.rcParams['xtick.labeltop'] = True
    fig, axs = plt.subplots(dpi=DPI, figsize=figsize, ncols=1, nrows=2,
                            sharex=True)
    im_upper = axs[0].imshow(y_upper,
                             interpolation="nearest",
                             aspect="auto",
                             origin="lower",
                             vmin=ymin_upper,
                             vmax=ymax_upper,
                             extent=(0, scans_upper, xmax_upper, xmin_upper),
                             cmap=cmap_upper)
    if isinstance(PLOT_STYLE, type(None)):
        axs[0].xaxis.tick_top()
    axs[0].xaxis.set_label_position('top')
    axs[0].set_xlabel(index_label_upper, fontsize=fontsize_labels)
    axs[0].set_ylabel(xlabel_upper, fontsize=fontsize_labels)
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
    axs[0].xaxis.set_major_locator(ticker.MultipleLocator(base_scan_upper))
    axs[0].xaxis.set_minor_locator(ticker.MultipleLocator(base_scan_upper / minor_tick_index_upper))
    axs[0].yaxis.set_major_locator(ticker.MultipleLocator(base_scatt_upper))
    axs[0].yaxis.set_minor_locator(ticker.MultipleLocator(base_scatt_upper / minor_tick_index_upper))
    cbar0 = axs[0].figure.colorbar(im_upper,
                                   ax=axs[0],
                                   ticks=np.linspace(ymin_upper, ymax_upper, cbar_ticks_upper)
                                   )
    if ymax_upper > 100:
        cbar0.formatter.set_powerlimits((0, 0))
    cbar0.set_label(label=ylabel_upper, size=fontsize_labels)
    cbar0.minorticks_on()
    im_lower = axs[1].imshow(y_lower,
                             interpolation="nearest",
                             aspect="auto",
                             origin="lower",
                             vmin=ymin_lower,
                             vmax=ymax_lower,
                             extent=(0, scans_lower, xmax_lower, xmin_lower),
                             cmap=cmap_lower)
    if isinstance(PLOT_STYLE, type(None)):
        axs[1].xaxis.tick_top()
    axs[1].xaxis.set_label_position('top')
    # axs[1].set_xlabel(index_label_lower, fontsize=fontsize_labels)
    axs[1].set_ylabel(xlabel_lower, fontsize=fontsize_labels)
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
    axs[1].xaxis.set_major_locator(ticker.MultipleLocator(base_scan_lower))
    axs[1].xaxis.set_minor_locator(ticker.MultipleLocator(base_scan_lower / minor_tick_index_lower))
    axs[1].yaxis.set_major_locator(ticker.MultipleLocator(base_scatt_lower))
    axs[1].yaxis.set_minor_locator(ticker.MultipleLocator(base_scatt_lower / minor_tick_index_lower))
    cbar1 = axs[1].figure.colorbar(im_lower,
                                   ax=axs[1],
                                   ticks=np.linspace(ymin_lower, ymax_lower, cbar_ticks_lower)
                                   )
    if ymax_lower > 100:
        cbar1.formatter.set_powerlimits((0, 0))
    cbar1.set_label(label=ylabel_lower, size=fontsize_labels)
    cbar1.minorticks_on()
    fig.subplots_adjust(hspace=hspace)
    for folder in output_folders:
        fname = f"{basename}_"
        fname += f"xupper={xmin_upper}-{xmax_upper}_"
        fname += f"yupper={ymin_upper}-{ymax_upper}_"
        fname += f"xlower={xmin_lower}-{xmax_lower}_"
        fname += f"ylower={ymin_lower}-{ymax_lower}"
        fname += f".{folder}"
        output_path = Path.cwd() / folder / fname
        plt.savefig(output_path, bbox_inches="tight")
    plt.close()

    return None


def main():
    data_path_upper = Path.cwd() / "data_upper"
    data_path_lower = Path.cwd() / "data_lower"
    data_paths = [data_path_upper, data_path_lower]
    exit = False
    for p in data_paths:
        if not p.exists():
            p.mkdir()
            print(f"{80*'-'}\nA folder called '{p.name}' has been created.")
            exit = True
    if exit is True:
        print(f"{80*'-'}\nPlease place your data files in the appropriate folders and "
              f"rerun the code.\n{80*'-'}")
        sys.exit()
    data_files_upper = list(data_path_upper.glob("*.*"))
    data_files_lower = list(data_path_lower.glob("*.*"))
    data_files = [data_files_upper, data_files_lower]
    for i in range(len(data_files)):
        if len(data_files[i]) == 0:
            print(f"{80*'-'}\nNo files found in the '{data_paths[i].name}' "
                  f"folder.")
            exit = True
    if exit is True:
        print(f"{80*'-'}\nPlease place your data files in the appropriate "
              f"folders and rerun the code.\n{80*'-'}")
        sys.exit()
    data_exts = []
    for i in range(len(data_files)):
        data_exts.append([])
        for j in range(len(data_files[i])):
            if not data_files[i][j].suffix in data_exts[i]:
                data_exts[i].append(data_files[i][j].suffix)
    for i in range(len(data_exts)):
        if len(data_exts[i]) > 1:
            print(f"{80*'-'}\nMore than one file extension found in the "
                  f"'{data_paths[i].name}' folder.")
            exit = True
    if exit is True:
        print(f"{80*'-'}\nPlease review the files in the data folders and "
                  f"rerun the code.\n{80*'-'}")
        sys.exit()
    print(f"{80*'-'}\nStacking xy data for upper plot...")
    x_upper, y_upper = xy_stack(data_files_upper)
    print(f"{80*'-'}\nStacking xy data for lower plot...")
    x_lower, y_lower = xy_stack(data_files_lower)
    print(f"{80*'-'}\nDone stacking xy data.")
    xy_dict = dict(x_upper=x_upper,
                   y_upper=y_upper,
                   x_lower=x_lower,
                   y_lower=y_lower)
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
        user_inputs = dict(dpi = DPI,
                           figsize = FIGSIZE,
                           fontsize_labels = FONTSIZE_LABELS,
                           fontsize_ticks = FONTSIZE_TICKS,
                           cmap_upper = CMAPS[0],
                           cbar_ticks_upper = CBAR_TICKS,
                           minor_tick_index_upper = MINOR_TICK_INDEX,
                           index_label_upper = INDEX_LABEL,
                           xytype_index_upper = XY_TYPE_INDEX,
                           xmin_upper = XMIN,
                           xmax_upper = XMAX,
                           ymin_upper = YMIN,
                           ymax_upper = YMAX,
                           cmap_lower = CMAPS[0],
                           cbar_ticks_lower = CBAR_TICKS,
                           minor_tick_index_lower = MINOR_TICK_INDEX,
                           index_label_lower = INDEX_LABEL,
                           xytype_index_lower = XY_TYPE_INDEX,
                           xmin_lower = XMIN,
                           xmax_lower = XMAX,
                           ymin_lower = YMIN,
                           ymax_lower = YMAX,
                           hspace = HSPACE,
                           )
        with user_input_path.open(mode="w") as o:
            json.dump(user_inputs, o, indent=4, sort_keys=False)
        print(f"{80*'-'}\nThe following values were read from "
              f" {user_input_path.name}:")
        for k,v in user_inputs.items():
            if not k == "xytype_index":
                print(f"\t{k}\t{v}")
            else:
                print(f"\t{k}\t{XY_TYPES[v]}")
        plot_input = input(f"{80*'-'}\nDo you want to plot using the default "
                           f"plot settings? ([y]/n): ")
        while plot_input.lower() == "n":
            user_inputs_items = list(user_inputs.items())
            print(f"{80*'-'}\nindex\tkey\tvalue")
            for i in range(len(user_inputs_items)):
                print(f"{i}\t{user_inputs_items[i][0]}\t"
                      f"{user_inputs_items[i][1]}")
            user_inputs_index = int(input(f"{80*'-'}\nPlease provide the index "
                                          f"of the setting that you would like "
                                          f"to change: "))
            user_input_key = user_inputs_items[user_inputs_index][0]
            if user_input_key == "figsize":
                user_input_val = input(f"Please state the desired "
                                       f"{user_input_key} (width, height): ")
                user_input_val = user_input_val.lstrip("(").rstrip(")")
                user_input_val = user_input_val.split(",")
                user_inputs[user_input_key] = (int(user_input_val[0]),
                                               int(user_input_val[1]))
            else:
                user_input_val = input(f"Please state the desired "
                                       f"{user_input_key}: ")
                nonstr_keys = ["dpi",
                               "fontsize_labels",
                               "fontsize_ticks",
                               "cbar_ticks_upper",
                               "minor_tick_index_upper",
                               "xy_type_index_upper",
                               "xmin_upper",
                               "xmax_upper",
                               "ymin_upper",
                               "ymax_upper",
                               "cbar_ticks_lower",
                               "minor_tick_index_lower",
                               "xy_type_index_lower",
                               "xmin_lower",
                               "xmax_lower",
                               "ymin_lower",
                               "ymax_lower",
                               "hspace"]
                if user_input_key in nonstr_keys:
                    user_inputs[user_input_key] = float(user_input_val)
                else:
                    user_inputs[user_input_key] = user_input_val
            with user_input_path.open(mode="w") as o:
                json.dump(user_inputs, o, indent=4, sort_keys=False)
            with user_input_path.open(mode="r") as f:
                user_inputs = json.load(f)
            user_inputs["figsize"] = tuple(user_inputs["figsize"])
            print(f"{80*'-'}\nThe following values were read from "
                  f" {user_input_path.name}:")
            for k,v in user_inputs.items():
                if not k == "xytype_index":
                    print(f"\t{k}\t{v}")
                else:
                    print(f"\t{k}\t{XY_TYPES[v]}")
            plot_input = input(f"{80*'-'}\nDo you want to plot using the default "
                               f"plot settings? ([y]/n): ")
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
        while plot_input.lower() == "n":
            user_inputs_items = list(user_inputs.items())
            print(f"{80*'-'}\nindex\tkey\tvalue")
            for i in range(len(user_inputs_items)):
                print(f"{i}\t{user_inputs_items[i][0]}\t"
                      f"{user_inputs_items[i][1]}")
            user_inputs_index = int(input(f"{80*'-'}\nPlease provide the index "
                                          f"of the setting that you would like "
                                          f"to change: "))
            user_input_key = user_inputs_items[user_inputs_index][0]
            if user_input_key == "figsize":
                user_input_val = input(f"Please state the desired "
                                       f"{user_input_key} (width, height): ")
                user_input_val = user_input_val.lstrip("(").rstrip(")")
                user_input_val = user_input_val.split(",")
                user_inputs[user_input_key] = (int(user_input_val[0]),
                                               int(user_input_val[1]))
            else:
                user_input_val = input(f"Please state the desired "
                                       f"{user_input_key}: ")
                nonstr_keys = ["dpi",
                               "fontsize_labels",
                               "fontsize_ticks",
                               "cbar_ticks_upper",
                               "minor_tick_index_upper",
                               "xy_type_index_upper",
                               "xmin_upper",
                               "xmax_upper",
                               "ymin_upper",
                               "ymax_upper",
                               "cbar_ticks_lower",
                               "minor_tick_index_lower",
                               "xy_type_index_lower",
                               "xmin_lower",
                               "xmax_lower",
                               "ymin_lower",
                               "ymax_lower",
                               "hspace",]
                if user_input_key in nonstr_keys:
                    user_inputs[user_input_key] = float(user_input_val)
                else:
                    user_inputs[user_input_key] = user_input_val
            with user_input_path.open(mode="w") as o:
                json.dump(user_inputs, o, indent=4, sort_keys=False)
            with user_input_path.open(mode="r") as f:
                user_inputs = json.load(f)
            user_inputs["figsize"] = tuple(user_inputs["figsize"])
            print(f"{80*'-'}\nThe following values were read from "
                  f" {user_input_path.name}:")
            for k,v in user_inputs.items():
                if not k == "xytype_index":
                    print(f"\t{k}\t{v}")
                else:
                    print(f"\t{k}\t{XY_TYPES[v]}")
            plot_input = input(f"{80*'-'}\nDo you want to plot using the default "
                               f"plot settings? ([y]/n): ")
    print(f"{80*'-'}\nMaking overview plots...")
    basename = data_files[0][0].stem
    print("\tUpper plot individually...")
    xy_overview(x_upper, y_upper, output_folders, basename, user_inputs, "upper")
    print("\tLower plot individually...")
    xy_overview(x_lower, y_lower, output_folders, basename, user_inputs, "lower")
    print("\tBoth plots together...")
    xy_overview_stack(xy_dict, output_folders, basename, user_inputs)
    print(f"Done making overview plot. Please see the {output_folders} "
          f"folders.\n{80*'-'}\nGood luck with your plots! (^^,)")

    return None


if __name__ == "__main__":
    main()

# End of file.
