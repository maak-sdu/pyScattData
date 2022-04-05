import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from diffpy.utils.parsers.loaddata import loadData


FIGSIZE = (8,4)
DPI = 600
FONTSIZE_LABELS = 20
FONTSIZE_TICKS = 16
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

def y_stack(data_files):
    for i in range(len(data_files)):
        print(f"\t{data_files[i].name}")
        xy = loadData(str(data_files[i]))
        x, y = xy[:,0], xy[:,1]
        if i == 0:
            y_array = y
        else:
            y_array = np.column_stack((y_array, y))

    return x, y_array


def xy_overview(x, y, cmap, output_folders, basename, xy_type_index, limits):
    xmin, xmax = limits["xmin"], limits["xmax"]
    ymin, ymax = limits["ymin"], limits["ymax"]
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
    fig, ax = plt.subplots(dpi=DPI, figsize=FIGSIZE)
    # xmin_index, xmax_index = None, None
    if isinstance(xmin, type(None)):
        plot_limits = None
        xmin, xmax, ymin, ymax = np.amin(x), np.amax(x), np.amin(y), np.amax(y)
        xmin_index, xmax_index = 0, -1
    else:
        plot_limits = "found"
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
            xmax_index = -1
    if not isinstance(plot_limits, type(None)):
        y = y[xmin_index:xmax_index+1,:]
    y = np.flip(y, axis=0)
    im = ax.imshow(y,
                   interpolation="nearest",
                   aspect="auto",
                   origin="lower",
                   vmin=ymin,
                   vmax=ymax,
                   extent=(0, y.shape[-1], xmax, xmin),
                   cmap=cmap
              )
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    ax.set_xlabel("Index", fontsize=FONTSIZE_LABELS)
    ax.set_ylabel(xlabel, fontsize=FONTSIZE_LABELS)
    if not isinstance(plot_limits, type(None)):
        cbar = ax.figure.colorbar(im, ax=ax, ticks=np.linspace(ymin, ymax, 5))
    else:
        cbar = ax.figure.colorbar(im, ax=ax)
    cbar.set_label(label=ylabel, size=FONTSIZE_LABELS)
    for folder in output_folders:
        if isinstance(plot_limits, type(None)):
            output_path = Path.cwd() / folder / f"{basename}.{folder}"
        else:
            fname = f"{basename}_x={xmin}-{xmax}_y={ymin}-{ymax}.{folder}"
            output_path = Path.cwd() / folder / fname
        plt.savefig(output_path, bbox_inches="tight")

    return None


def main():
    print(f"{80*'-'}\nPlease see the top of this .py file for plot settings.")
    data_path = Path.cwd() / "data"
    if not data_path.exists():
        data_path.mkdir()
        print(f"{80*'-'}\nA folder called 'data' has been created. Please "
              f"place your data files there and\nrerun the code.\n{80*'-'}")
        sys.exit()
    data_files = list(data_path.glob("*.*"))
    if len(data_files) == 0:
        print(f"{80*'-'}\nNo files found in the 'data' folder. Please place "
              f"your data files there and\nrerun the code.\n{80*'-'}")
        sys.exit()
    data_ext = []
    for e in data_files:
        if not e.suffix in data_ext:
            data_ext.append(e.suffix)
    if len(data_ext) > 1:
        print(f"{80*'-'}\nMore than one file extension found in the 'data' "
              f"folder. Please review the files\nin the 'data' folder and rerun "
              f"the code.\n{80*'-'}")
        sys.exit()
    print(f"{80*'-'}\nStacking y data...")
    x, y = y_stack(data_files)
    print("Done stacking y data.")
    output_folders = ["pdf", "png", "svg"]
    for folder in output_folders:
        if not (Path.cwd() / folder).exists():
            (Path.cwd() / folder).mkdir()
    cmap_xytype_path = Path.cwd() / "cmap_xytype.txt"
    if not cmap_xytype_path.exists():
        cmap_input = input(f"{80*'-'}\nThe default cmap is {CMAPS[0]}. Do you "
                           f"want to plot using the default cmap?\n([y]/n): ")
        if cmap_input.lower() in ["", "y"]:
            cmap = CMAPS[0]
        else:
            print(f"{80*'-'}\ncmaps available:")
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
        with cmap_xytype_path.open(mode="w", encoding="utf8") as f:
            f.write(f"cmap\t{cmap}\nxytype\t{xy_type_index}")
    else:
        with cmap_xytype_path.open(mode="r") as f:
            lines = f.readlines()
        for line in lines:
            if "cmap" in line:
                cmap = line.split()[-1]
            elif "xytype" in line:
                xy_type_index = int(line.split()[-1])
        print(f"{80*'-'}\nThe following default values were read from "
              f"{cmap_xytype_path.name}:\n\tcmap: {cmap}\n\txy_type: "
              f"{XY_TYPES[xy_type_index]}")
        cmap_input = input(f"{80*'-'}\nDo you want to plot using the default "
                           f"cmap? ([y]/n): ")
        if cmap_input.lower() == "n":
            print(f"{80*'-'}\ncmaps available:")
            cmap_keys = list(CMAPS.keys())
            for i in range(len(cmap_keys)):
                print(f"\t{i}\t{CMAPS[cmap_keys[i]]}")
            cmap_input = input(f"Please provide the index of the desired cmap: ")
            cmap = CMAPS[int(cmap_input)]
        xy_type_input = input(f"{80*'-'}\nThe default xy type is "
                              f"'{XY_TYPES[xy_type_index]}'.\nDo you want to "
                              f"plot using the default xy type? ([y]/n): ")
        if xy_type_input.lower() == "n":
            print(f"{80*'-'}\nData type...\n\tindex\ttype")
            for i in range(len(XY_TYPES)):
                print(f"\t{i}\t{XY_TYPES[i]}")
            xy_type_index = int(input("Please indicate the type of xy data that you "
                                      "are plotting: "))
        with cmap_xytype_path.open(mode="w", encoding="utf8") as f:
            f.write(f"cmap\t{cmap}\nxytype\t{xy_type_index}")
    print(f"{80*'-'}\nMaking overview plot in full range...")
    limits = dict(xmin=None, xmax=None, ymin=None, ymax=None)
    basename = data_files[0].stem
    xy_overview(x, y, cmap, output_folders, basename, xy_type_index, limits)
    print(f"Done making overview plot. Please see the {output_folders} folders."
          f"\n{80*'-'}")
    limits_plot_req = input("Do you want to make an additional overview plot "
                            "with customized limits? ([y]/n): ")
    while limits_plot_req.lower() in ["", "y"]:
        limits["xmin"] = float(input("Please state the minimum x value: "))
        limits["xmax"] = float(input("Please state the maximum x value: "))
        limits["ymin"] = float(input("Please state the minimum y value: "))
        limits["ymax"] = float(input("Please state the maximum y value: "))
        print(f"{80*'-'}\nMaking overview plot in customized range...")
        xy_overview(x, y, cmap, output_folders, basename, xy_type_index, limits)
        print(f"Done making overview plot. Please see the {output_folders} folders."
              f"\n{80*'-'}")
        limits_plot_req = input("Do you want to make an additional overview "
                                "plot with customized limits? ([y]/n): ")
    print(f"{80*'-'}\nGood luck with your plots! (^^,)")

    return None


if __name__ == "__main__":
    main()

# End of file.
