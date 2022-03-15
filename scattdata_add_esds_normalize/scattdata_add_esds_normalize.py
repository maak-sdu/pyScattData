import sys
from pathlib import Path
import numpy as np
from diffpy.utils.parsers.loaddata import loadData
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


DPI = 300
FIGSIZE = (12,4)
FONTSIZE_LABELS = 20
FONTSIZE_TICKS = 14
LINEWIDTH = 1

TICKINDEX_SCAN_MAJOR = 5
TICKINDEX_SCAN_MINOR = 1
TICKINDEX_SCATT_MAJOR = 5
TICKINDEX_SCATT_MINOR = 1

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
CMAP = f"{CMAPS[25]}_r"


def comma_to_dot(files):
    with files[0].open(mode="r") as f:
        s = f.read()
    if "," in s:
        parent = files[0].parent.name
        comma_to_dot_path = files[0].parent.parent / f"{parent}_comma_to_dot"
        if not comma_to_dot_path.exists():
            comma_to_dot_path.mkdir()
        print(f"{80*'-'}\nConverting commas to dots...")
        for e in files:
            print(f"\t{e.name}")
            with e.open(mode="r") as f:
                s = f.read().replace(",", ".")
            fname = comma_to_dot_path / e.name
            with fname.open(mode="w", encoding="utf-8") as o:
                o.write(s)
        print(f"Done converting commas to dots.\n{80*'-'}")

    return None


def data_files_to_dict(data_files, type):
    d = {}
    if type == "data":
        for f in data_files:
            scan = int(str(f.stem).split("_")[-1])
            d[scan] = loadData(str(f))
    elif type == "bkg":
        for f in data_files:
            d["bkg"] = loadData(str(f))

    return d


def sigma_calculator_writer(data_dict, basename, file_ext, zfill, sdd, type):
    for k in data_dict.keys():
        x, y, = data_dict[k][:,0], data_dict[k][:,1]
        normalizer = np.array([2*np.pi*sdd*np.tan(np.pi*x[i]/180)/0.150
                              for i in range(len(x))])
        sigma = np.sqrt(y/normalizer)
        xye = np.column_stack((x, y, sigma))
        if type == "data":
            fname = f"{basename}_s_{str(k).zfill(zfill)}{file_ext}"
            output_path = Path.cwd() / "data_sigmas" / fname
        elif type == "bkg":
            fname = f"{basename}_s{file_ext}"
            output_path = Path.cwd() / "bkg_sigmas" / fname
        print(f"\t{fname}")
        np.savetxt(output_path, xye, fmt="%.18e", delimiter="\t",
                   encoding="utf-8")

    return None


def stack_plotter(data_dict, basename, data_files_ext, xtype, xunit, zfill,
                  type):
    plt.figure(dpi=DPI, figsize=FIGSIZE)
    for k in data_dict.keys():
        x, y = data_dict[k][:,0], data_dict[k][:,1]
        plt.plot(x, y,c=np.random.rand(3,), lw=0.3)
    plt.xlim(np.amin(x), np.amax(x))
    plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
    xlabel = f"{xtype} {xunit}"
    ylabel = r"$I$ $[\mathrm{counts}]$"
    plt.xlabel(xlabel, fontsize=FONTSIZE_LABELS)
    plt.ylabel(ylabel, fontsize=FONTSIZE_LABELS)
    plt.tick_params(axis="both", labelsize=FONTSIZE_TICKS)
    if type == "sigma":
        plt.savefig(f"png/{basename}_s.png", bbox_inches='tight')
        plt.savefig(f"pdf/{basename}_s.pdf", bbox_inches='tight')
    elif type == "scaled":
        plt.savefig(f"png/{basename}_ss.pdf", bbox_inches='tight')
        plt.savefig(f"pdf/{basename}_ss.pdf", bbox_inches='tight')
    plt.show()

    return None


def basecase_calculator(file_ext, scale_xmin, scale_xmax):
    sigma_file = list((Path.cwd() / "data_sigmas").glob(f"*{file_ext}"))[0]
    basecase = 0
    with sigma_file.open(mode="r") as f:
        xy = np.loadtxt(f)
        x, y = xy[:,0], xy[:,1]
        for i in range(len(x)):
            if scale_xmin <= x[i] <= scale_xmax:
                basecase += y[i]

    return basecase


def norm_factor(filename, basecase, scale_xmin, scale_xmax):
    intensity, intensity_sum = 0, 0
    xy = np.loadtxt(filename)
    x, y = xy[:,0], xy[:,1]
    for i in range(len(y)):
        if scale_xmin <= x[i] <= scale_xmax:
            intensity_sum += y[i]
    if intensity_sum == 0:
        normalizer = 1
    else:
        normalizer = basecase / intensity_sum

    return normalizer


def normalizer(file_ext, basecase, scale_xmin, scale_xmax, type):
    files_sigmas = (Path.cwd() / f"{type}_sigmas").glob(f"*{file_ext}")
    for f in files_sigmas:
        fname = ''
        if type == "data":
            for e in f.name.split("_")[0:-2]:
                fname += f"{e}_"
            fname += f"ss_{f.name.split('_')[-1]}"
        elif type == "bkg":
            fname = f"{f.stem}s{f.suffix}"
        print(f"\t{fname}")
        factor = norm_factor(f, basecase, scale_xmin, scale_xmax)
        xye = np.loadtxt(f)
        x, y, e = xye[:,0], xye[:,1], xye[:,2]
        y_norm, e_norm = y * factor, e * factor
        np.savetxt(f"{type}_normalized/{fname}",
            np.column_stack((x, y_norm, e_norm)))

    return None


def buf_writer(files_norm, buf_path):
    basename_split = files_norm[0].stem.split("_")
    basename = ""
    for e in basename_split[0:-1]:
        basename += f"{e}_"
    basename = basename.strip("_")
    buf_file_path = buf_path / f"{basename}.buf"
    s =""
    for e in files_norm:
        s += f"{e.name}\n"
    with buf_file_path.open(mode="w", encoding="utf-8") as o:
        o.write(s)

    return None


def data_dict_overview(data_dict, xlabel, basename):
    keys = list(data_dict.keys())
    for i in range(len(keys)):
        xy = data_dict[keys[i]]
        x, y = xy[:,0], xy[:,1]
        if i == 0:
            y_stack = y
        else:
            y_stack = np.column_stack((y_stack, y))
    xmin, xmax = None, None
    for i in range(len(y)-1):
        if y[i] == 0 and y[i+1] != 0:
            xmin_index = i
            xmin = x[i]
            break
    for i in range(xmin_index + 1, len(y) - 6):
        if y[i] == y[i+1] == y[i+2] == y[i+3] == y[i+4] == y[i+5] == y[i+6] ==0:
            xmax_index = i
            xmax = x[i]
            break
    if isinstance(xmin, type(None)):
        xmin = np.amin(x)
    if isinstance(xmax, type(None)):
        xmax = np.amax(x)
    y = np.flip(y_stack[xmin_index:xmax_index, :], axis=0)
    fig, ax = plt.subplots(dpi=DPI, figsize=FIGSIZE)
    im = plt.imshow(y,
                    interpolation='nearest',
                    origin='lower',
                    vmin=np.amin(y), vmax=np.amax(y),
                    extent=(0, len(keys), xmax, xmin),
                    # aspect=(len(scannumbers) - 0)/(np.amax(x) - np.amin(x)),
                    # aspect=FIGSIZE[0]/FIGSIZE[-1],
                    cmap=CMAP
                    )
    ax.xaxis.set_ticks_position('top')
    plt.tick_params(axis="both", labelsize=FONTSIZE_LABELS)
    plt.title("Scan", fontsize=FONTSIZE_LABELS)
    plt.ylabel(xlabel, fontsize=FONTSIZE_LABELS)
    cbar = plt.colorbar(im, ax=ax)
    cbar.ax.set_ylabel(r"$I$ " "$[\mathrm{arb. u.}]$", fontsize=FONTSIZE_LABELS)
    cbar.formatter.set_powerlimits((0, 0))
    cbar.ax.tick_params(labelsize=FONTSIZE_TICKS)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(TICKINDEX_SCAN_MAJOR))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(TICKINDEX_SCAN_MINOR))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(TICKINDEX_SCATT_MAJOR))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(TICKINDEX_SCATT_MINOR))
    plt.savefig(f"png/{basename}_overview.png", bbox_inches="tight")
    plt.savefig(f"pdf/{basename}_overview.pdf", bbox_inches="tight")
    plt.show()

    return None


def main():
    """
    This will run by default when the file is executed using
    "python file.py" in the command line

    Parameters
    ----------
    None

    Returns
    ----------
    None
    """
    data_path = Path.cwd() / "data"
    bkg_path = Path.cwd() / "bkg"
    if not data_path.exists():
        data_path.mkdir()
        print(f"{80*'-'}\nA folder called 'data' has been created. Please "
              f"place your data files there and\nrerun the code.\n{80*'-'}")
        sys.exit()
    elif not bkg_path.exists():
        bkg_path.mkdir()
        print(f"{80*'-'}\nA folder called 'bkg' has been created. Please "
              f"place your backgorund file there\nand rerun the code."
              f"\n{80*'-'}")
        sys.exit()
    data_files = list(data_path.glob("*.*"))
    bkg_files = list(bkg_path.glob("*.*"))
    if len(data_files) == 0:
        print(f"{80*'-'}\nNo data files found in the 'data' folder. Please "
              f"place your data files there and\nrerun the code.\n{80*'-'}")
        sys.exit()
    elif len(bkg_files) == 0:
        print(f"{80*'-'}\nNo bkg file found in the 'bkg' folder. Please "
              f"place your bkg file there and\nrerun the code.\n{80*'-'}")
        sys.exit()
    elif len(bkg_files) > 1:
        print(f"{80*'-'}\nMore than one bkg file found in the 'bkg' folder: "
              f"{[f.name for f in bkg_files]}\nPlease ensure that only one bkg "
              f"file is placed in the 'bkg' folder and rerun the\ncode."
              f"\n{80*'-'}")
        sys.exit()
    data_files_exts, basenames = [], []
    for f in data_files:
        if not f.suffix in data_files_exts:
            data_files_exts.append(f.suffix)
        name_split = str(f.stem).split('_')
        basename = name_split[0]
        for i in range(1, len(name_split)-1):
            basename += f"_{name_split[i]}"
        if not basename in basenames:
            basenames.append(basename)
    if len(data_files_exts) > 1:
        print(f"{80*'-'}\nMore than one file extension was found in the 'data' "
              f"folder: {data_files_exts}\nPlease ensure that only one type of "
              f"files are placed in the 'data' folder and\nrerun the code."
              f"\n{80*'-'}")
        sys.exit()
    elif len(basenames) > 1:
        print(f"{80*'-'}\nMore than one naming scheme was found in the 'data' "
              f"folder: {basenames}\nPlease ensure that only data files are "
              f"placed in the 'data' folder.\nThe bkg file should be placed in "
              f"the 'bkg' folder.\nPlease re-arrange your files and rerun the "
              f"code.\n{80*'-'}")
        sys.exit()
    zfill = len(str(len(data_files)))
    basename = basenames[0]
    bkgname = bkg_files[0].stem
    data_files_ext = data_files_exts[0]
    comma_to_dot(data_files)
    data_comma_to_dot_path = Path.cwd() / "data_comma_to_dot"
    if data_comma_to_dot_path.exists():
        data_files = list(data_comma_to_dot_path.glob("*.*"))
    comma_to_dot(bkg_files)
    bkg_comma_to_dot_path = Path.cwd() / "bkg_comma_to_dot"
    if bkg_comma_to_dot_path.exists():
        bkg_files = list(bkg_comma_to_dot_path.glob("*.*"))
    data_dict = data_files_to_dict(data_files, type="data")
    bkg_dict = data_files_to_dict(bkg_files, type="bkg")
    data_bkg_dict = data_files_to_dict(data_files, type="data")
    data_bkg_dict["bkg"] = bkg_dict["bkg"]
    sdd = float(input(f"{80*'-'}\nPlease state the sample-to-detector-distance "
                      f"in mm: "))
    print(f"{80*'-'}\nPlease state the quantity and unit for the independent "
          f"variable:\n\t1\tfor Q in inverse Ångström.\n\t2\tfor Q in inverse "
          f"nm.\n\t3\tfor 2theta in degrees.")
    xtype = int(input("Please state the quantity on the x-axis: "))
    if xtype == 1:
        xtype = r'$Q$'
        xunit = r'$[\mathrm{\AA}^{-1}]$'
    elif xtype == 2:
        xtype = r'$Q$'
        xunit = r'$[\mathrm{nm}^{-1}]$'
    elif xtype == 3:
        xtype = r'$2\theta$'
        xunit = r'$[\degree]$'
    print(f"{80*'-'}\nAdding sigmas and writing files...")
    data_sigma_path = Path.cwd() / "data_sigmas"
    if not data_sigma_path.exists():
        data_sigma_path.mkdir()
    bkg_sigma_path = Path.cwd() / "bkg_sigmas"
    if not bkg_sigma_path.exists():
        bkg_sigma_path.mkdir()
    sigma_calculator_writer(data_dict, basename, data_files_ext, zfill, sdd,
                            type="data")
    sigma_calculator_writer(bkg_dict, bkgname, data_files_ext, zfill, sdd,
                            type="bkg")
    print(f"Done adding sigmas and writing to files.")
    data_sigma_files = list(data_sigma_path.glob("*.*"))
    bkg_sigma_files = list(bkg_sigma_path.glob("*.*"))
    plot_paths = ["png", "pdf"]
    for e in plot_paths:
        p = Path.cwd() / e
        if not p.exists():
            p.mkdir()
    print(f"{80*'-'}\nMaking stack plot of data files and bkg...")
    stack_plotter(data_bkg_dict, basename, data_files_ext, xtype, xunit, zfill,
                  type="sigma")
    print(f"Stack plot of data files and bkg saved to the 'pdf' and 'png' "
          f"folders.\n{80*'-'}")
    scale_xmin = float(input(f"Lower limit of the {xtype.strip('$')} range to "
                             f"scale within: "))
    scale_xmax = float(input(f"Upper limit of the {xtype.strip('$')} range to "
                             f"scale within: "))
    print(f"{80*'-'}\nCalculating 'basecase' to use for scaling...")
    basecase = basecase_calculator(data_files_ext, scale_xmin, scale_xmax)
    print("Done calculating 'basecase' to use for scaling...")
    scale_paths = ["data_normalized", "bkg_normalized"]
    for e in scale_paths:
        p = Path.cwd() / e
        if not p.exists():
            p.mkdir()
    print(f"{80*'-'}\nNormalizing data...")
    data_scaled = normalizer(data_files_ext, basecase, scale_xmin, scale_xmax,
                              type="data")
    data_scaled = normalizer(data_files_ext, basecase, scale_xmin, scale_xmax,
                              type="bkg")
    print(f"Done normalizing data.\n{80*'-'}\nWriting .buf file.")
    buf_path = Path.cwd() / "buf"
    if not buf_path.exists():
        buf_path.mkdir()
    data_norm_path = Path.cwd() / "data_normalized"
    bkg_norm_path = Path.cwd() / "bkg_normalized"
    files_norm = list(data_norm_path.glob(f"*{data_files_ext}"))
    files_norm.append(list(bkg_norm_path.glob(f"*{data_files_ext}"))[0])
    buf_writer(files_norm, buf_path)
    print("Done writing .buf file.")
    print(f"{80*'-'}\nMaking stack plot of normalized files...")
    data_files_norm = list(data_norm_path.glob(f"*{data_files_ext}"))
    bkg_file_norm = list(bkg_norm_path.glob(f"*{data_files_ext}"))
    data_dict_norm = data_files_to_dict(data_files_norm, type="data")
    bkg_dict_norm = data_files_to_dict(bkg_file_norm, type="bkg")
    data_bkg_dict_norm = data_files_to_dict(data_files_norm, type="data")
    data_bkg_dict_norm["bkg"] = bkg_dict_norm["bkg"]
    stack_plotter(data_bkg_dict_norm, basename, data_files_ext, xtype, xunit,
                  zfill, type="scaled")
    print(f"Stack plot of normalized data files and bkg saved to the 'pdf' and "
          f"'png' folders.\n{80*'-'}\nMaking overview plot of normalized "
          f"files...")
    data_dict_overview(data_dict_norm, f"{xtype} {xunit}", f"{basename}_ss")
    print(f"Overview plot of normalized data files saved to the 'pdf' "
          f"and 'png' folders.\n{80*'-'}\nDone working with files. <(^^,)>")

    return None


if __name__ == '__main__':
    main()

# End of file
