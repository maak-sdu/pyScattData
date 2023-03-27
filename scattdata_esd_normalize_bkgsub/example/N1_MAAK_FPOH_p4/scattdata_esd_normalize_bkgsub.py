import sys
from pathlib import Path
import numpy as np
import pandas as pd
from diffpy.utils.parsers.loaddata import loadData
from skbeam.core.utils import q_to_twotheta
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from bg_mpl_stylesheet.bg_mpl_stylesheet import bg_mpl_style


SCAN_SPLIT_CHAR = "_"
SCAN_SEQ_SPLIT_CHAR = "-"

DPI = 300
FIGSIZE = (12,4)
FONTSIZE_LABELS = 20
FONTSIZE_TICKS = 14
LINEWIDTH = 1

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
        print(f"Done converting commas to dots.")

    return None


def data_files_to_dict(data_files, scan_split_index, scan_split_index2, type):
    d = {}
    if type == "data":
        for f in data_files:
            if isinstance(scan_split_index2, int):
                scan = f.stem.split(SCAN_SPLIT_CHAR)[scan_split_index]
                scan = int(scan.split(SCAN_SEQ_SPLIT_CHAR)[scan_split_index2])
            else:
                scan = int(f.stem.split(SCAN_SPLIT_CHAR)[scan_split_index])
            d[scan] = loadData(str(f))
    elif type == "bkg":
        for f in data_files:
            d["bkg"] = loadData(str(f))

    return d


def esd_calculator_writer(data_dict, basename, file_ext, zfill, wl, sdd,
                          xtype, xunit, type):
    for k in sorted(data_dict.keys()):
        x, y, = data_dict[k][:,0], data_dict[k][:,1]
        if xtype == r'$Q$' and xunit == r'$[\mathrm{\AA}^{-1}]$':
            x_rad = q_to_twotheta(x, wl)
        elif xtype == r'$Q$' and xunit == r'$[\mathrm{nm}^{-1}]$':
            x_rad = q_to_twotheta(x / 10, wl)
        elif xtype == r'$2\theta$' and xunit == r'$[\degree]$':
            x_rad = np.radians(x)
        normalizer = np.array([2*np.pi*sdd*np.tan(x_rad[i])/0.150
                              for i in range(len(x))])
        esd = np.sqrt(y / normalizer)
        xye = np.column_stack((x, y, esd))
        if type == "data":
            fname = f"{basename}_s_{str(k).zfill(zfill)}{file_ext}"
            output_path = Path.cwd() / "data_esd" / fname
        elif type == "bkg":
            fname = f"{basename}_s{file_ext}"
            output_path = Path.cwd() / "bkg_esd" / fname
        print(f"\t{fname}")
        np.savetxt(output_path, xye, fmt="%.18e", delimiter="\t",
                   encoding="utf-8")

    return None


def stack_plotter(data_dict, basename, data_files_ext, xtype, xunit, zfill,
                  type):
    plt.style.use(bg_mpl_style)
    plt.figure(dpi=DPI, figsize=FIGSIZE)
    for k in data_dict.keys():
        x, y = data_dict[k][:,0], data_dict[k][:,1]
        plt.plot(x, y,c=np.random.rand(3,), lw=0.3)
    plt.xlim(np.amin(x), np.amax(x))
    plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
    xlabel = f"{xtype} {xunit}"
    ylabel = r"$I$ $[\mathrm{arb. u.}]$"
    plt.xlabel(xlabel, fontsize=FONTSIZE_LABELS)
    plt.ylabel(ylabel, fontsize=FONTSIZE_LABELS)
    plt.tick_params(axis="both", labelsize=FONTSIZE_TICKS)
    plt.minorticks_on()
    if type == "esd":
        plt.savefig(f"png/{basename}_s.png", bbox_inches='tight')
        plt.savefig(f"pdf/{basename}_s.pdf", bbox_inches='tight')
    elif type == "scaled":
        plt.savefig(f"png/{basename}_ss.png", bbox_inches='tight')
        plt.savefig(f"pdf/{basename}_ss.pdf", bbox_inches='tight')
    elif type == "bkgsub":
        plt.savefig(f"png/{basename}_ss_bkgsub.png", bbox_inches='tight')
        plt.savefig(f"pdf/{basename}_ss_bkgsub.pdf", bbox_inches='tight')
    plt.show()

    return None


def basecase_calculator(file_ext, scale_xmin, scale_xmax):
    esd_file = list((Path.cwd() / "data_esd").glob(f"*{file_ext}"))[0]
    basecase = 0
    with esd_file.open(mode="r") as f:
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
    files_esd = (Path.cwd() / f"{type}_esd").glob(f"*{file_ext}")
    for f in files_esd:
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
        np.savetxt(f"{type}_esd_normalized/{fname}",
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


def extrema_collect(data_dict):
    keys = sorted(list(data_dict.keys()))
    for i in range(len(keys)):
        xy = data_dict[keys[i]]
        x, y = xy[:,0], xy[:,1]
        if i == 0:
            y_stack = y
        else:
            y_stack = np.column_stack((y_stack, y))
    xmin, xmax, xmin_index, xmax_index = None, None, 0, -1
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

    return xmin, xmax, xmin_index, xmax_index


def dict_bkg_subtract(data_dict_norm, bkg_dict_norm):
    bkg_scale_list = []
    bkg_scale = 1
    y_bkg_norm = bkg_dict_norm["bkg"][:,1]
    for k in data_dict_norm.keys():
        xy = data_dict_norm[k]
        x, y = xy[:,0], xy[:,1]
        y_bkg = bkg_scale * y_bkg_norm
        bool_list = y >= y_bkg
        while False in bool_list:
            bkg_scale = bkg_scale * 0.999
            y_bkg = bkg_scale * y_bkg_norm
            bool_list = y >= y_bkg
        bkg_scale_list.append(bkg_scale)
    bkg_scale = min(bkg_scale_list)
    y_bkg_scaled = bkg_scale * bkg_dict_norm["bkg"][:,1]
    data_dict_bkg_sub = {}
    for k in data_dict_norm.keys():
        xy = data_dict_norm[k]
        x, y = xy[:,0], xy[:,1]
        y_bkg_sub = y - y_bkg_scaled
        data_dict_bkg_sub[k] = np.column_stack((x, y_bkg_sub))

    return data_dict_bkg_sub


def dict_bkg_sub_writer(data_dict_bkg_sub, basename, file_ext, output_path,
                        zfill):
    for k in data_dict_bkg_sub.keys():
        xy = data_dict_bkg_sub[k]
        fname = f"{basename}_{str(k).zfill(zfill)}_ss_bkgsub"f"{file_ext}"
        file_path = output_path / fname
        np.savetxt(file_path, xy, fmt="%.18e", delimiter="\t", encoding="utf-8")

    return None


def data_dict_overview(data_dict, xlabel, basename, xmin, xmax, xmin_index,
                       xmax_index):
    keys = sorted(list(data_dict.keys()))
    for i in range(len(keys)):
        xy = data_dict[keys[i]]
        x, y = xy[:,0], xy[:,1]
        if i == 0:
            y_stack = y
        else:
            y_stack = np.column_stack((y_stack, y))
    y = np.flip(y_stack[xmin_index:xmax_index, :], axis=0)
    xrange = xmax - xmin
    plt.style.use(bg_mpl_style)
    fig, ax = plt.subplots(dpi=DPI, figsize=FIGSIZE)
    im = plt.imshow(y,
                    interpolation='nearest',
                    origin='lower',
                    vmin=np.amin(y), vmax=np.amax(y),
                    extent=(0, len(keys), xmax, xmin),
                    aspect="auto",
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
    ax.minorticks_on()
    # major_ticks, minor_ticks = 5, 5
    # base_scan = 10
    # if xrange < 15:
    #     base_scatt = 2
    # elif 15 <= xrange < 50:
    #     base_scatt = 5
    # else:
    #     base_scatt = 10
    # tickindex_scan_major = (base_scan * round(len(keys) / major_ticks /
    #                         base_scan))
    # tickindex_scan_minor = tickindex_scan_major / minor_ticks
    # tickindex_scatt_major = (base_scatt * round(xrange / major_ticks /
    #                          base_scatt))
    # tickindex_scatt_minor = tickindex_scatt_major / minor_ticks
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(tickindex_scan_major))
    # ax.xaxis.set_minor_locator(ticker.MultipleLocator(tickindex_scan_minor))
    # ax.yaxis.set_major_locator(ticker.MultipleLocator(tickindex_scatt_major))
    # ax.yaxis.set_minor_locator(ticker.MultipleLocator(tickindex_scatt_minor))
    plt.savefig(f"png/{basename}_overview.png", bbox_inches="tight")
    plt.savefig(f"pdf/{basename}_overview.pdf", bbox_inches="tight")
    plt.show()

    return None


def array_from_dict(d):
    for i, k in enumerate(d.keys()):
        if i == 0:
            array = np.column_stack((d[k][:, 0], d[k][:, 1]))
        else:
            array = np.column_stack((array, d[k][:, 1]))

    return array


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
    print(f"{80*'-'}\nFor plot settings, please see the top of this .py file.")
    data_path = Path.cwd() / "data"
    bkg_path = Path.cwd() / "bkg"
    if not data_path.exists():
        data_path.mkdir()
        print(f"{80*'-'}\nA folder called 'data' has been created. Please "
              f"place your data files there and\nrerun the code. "
              f"\n{80*'-'}")
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
    if len(data_files_exts) > 1:
        print(f"{80*'-'}\nMore than one file extension was found in the 'data' "
              f"folder: {data_files_exts}\nPlease ensure that only one type of "
              f"files are placed in the 'data' folder and\nrerun the code."
              f"\n{80*'-'}")
        sys.exit()
    scanseq_split = data_files[0].stem.split(SCAN_SPLIT_CHAR)
    print(f"{80*'-'}\nSplitting the filename '{data_files[0].name}' at "
          f"'{SCAN_SPLIT_CHAR}': ")
    for i in range(len(scanseq_split)):
        print(f"\t{i}\t{scanseq_split[i]}")
    scan_split_index = int(input("Please provide the integer for the entry "
                                    "containing the scan number\n(possibly "
                                    "more, e.g. the sequential number): "))
    for f in data_files:
        fname_split = f.stem.split(SCAN_SPLIT_CHAR)
        basename = fname_split[0]
        for i in range(1, scan_split_index):
            basename += f"_{scanseq_split[i]}"
        if not basename in basenames:
            basenames.append(basename)
    if len(basenames) > 1:
        print(f"{80*'-'}\nMore than one naming scheme was found in the 'data' "
              f"folder: {basenames}\nPlease ensure that only data files are "
              f"placed in the 'data' folder.\nThe bkg file should be placed in "
              f"the 'bkg' folder.\nPlease re-arrange your files and rerun the "
              f"code.\n{80*'-'}")
        sys.exit()
    zfill = len(str(len(data_files)))
    bkgname = bkg_files[0].stem
    data_files_ext = data_files_exts[0]
    comma_to_dot(data_files)
    data_comma_to_dot_path = Path(f"{data_path}_comma_to_dot")
    if data_comma_to_dot_path.exists():
        data_files = list(data_comma_to_dot_path.glob("*.*"))
    comma_to_dot(bkg_files)
    bkg_comma_to_dot_path = Path(f"{bkg_path}_comma_to_dot")
    if bkg_comma_to_dot_path.exists():
        bkg_files = list(bkg_comma_to_dot_path.glob("*.*"))
    f_0 = data_files[0]
    scan_syntax = f_0.stem.split(SCAN_SPLIT_CHAR)[scan_split_index]
    if SCAN_SEQ_SPLIT_CHAR in scan_syntax:
        scan_syntax_split = scan_syntax.split(SCAN_SEQ_SPLIT_CHAR)
        print(f"{80*'-'}\nSplitting '{scan_syntax}' at "
              f"'{SCAN_SEQ_SPLIT_CHAR}'...")
        for i in range(len(scan_syntax_split)):
            print(f"\t{i}\t{scan_syntax_split[i]}")
        scan_split_index2 = int(input("Please state the integer for the "
                                       "entry of the scan number: "))
    else:
        scan_split_index2 = None
    print(f"{80*'-'}\nLoading data and bkg into dictionaries...")
    data_dict = data_files_to_dict(data_files, scan_split_index,
                                   scan_split_index2, type="data")
    bkg_dict = data_files_to_dict(bkg_files, scan_split_index,
                                  scan_split_index2, type="bkg")
    data_bkg_dict = data_files_to_dict(data_files, scan_split_index,
                                       scan_split_index2, type="data")
    data_bkg_dict["bkg"] = bkg_dict["bkg"]
    print("Done loading data and bkg into dictionaries.")
    wl_sdd_path = Path.cwd() / "wl_sdd.txt"
    if not wl_sdd_path.exists():
        wl = float(input(f"{80*'-'}\nPlease state the wavelength in "
                         f"Ångström: "))
        sdd = float(input(f"{80*'-'}\nPlease state the sample-to-detector-"
                          f"distance in mm: "))
        with wl_sdd_path.open(mode="w", encoding="utf-8") as o:
            o.write(f"wavelength: {wl}\nsample-to-detector-distance: {sdd}\n")
    else:
        with wl_sdd_path.open(mode="r") as f:
            lines = f.readlines()
        for line in lines:
            if "wavelength" in line:
                wl = float(line.split()[1])
            elif "sample" in line:
                sdd = float(line.split()[1])
        print(f"{80*'-'}\nThe following wavelength (wl) and sample-to-detector-"
              f"distance (sdd) were read from the \n{wl_sdd_path.name} file:"
              f"\n\twl:\t{wl} Å\n\tsdd:\t{sdd} "
              f"mm")
        wl_sdd_conf = input("Please state whether these value are correct. "
                            "([y]/n): ")
        if not wl_sdd_conf.lower() in ["", "y", "n"]:
            wl_sdd_conf = input("Please state whether these value are correct."
                                "(y/n): ")
        if wl_sdd_conf.lower() == "n":
            wl = float(input(f"{80*'-'}\nPlease state the wavelength in "
                             f"Ångström: "))
            sdd = float(input(f"{80*'-'}\nPlease state the sample-to-detector-"
                              f"distance in mm: "))
        with wl_sdd_path.open(mode="w", encoding="utf-8") as o:
            o.write(f"wavelength: {wl}\nsample-to-detector-distance: {sdd}\n")
    print(f"{80*'-'}\nPlease state the quantity and unit for the independent "
          f"variable:\n\t1\tfor Q in inverse Ångström.\n\t2\tfor Q in inverse "
          f"nm.\n\t3\tfor 2theta in degrees.")
    xtype = int(input("Please state the quantity on the x-axis: "))
    if xtype == 1:
        xtype, xunit = r'$Q$', r'$[\mathrm{\AA}^{-1}]$'
    elif xtype == 2:
        xtype, xunit = r'$Q$', r'$[\mathrm{nm}^{-1}]$'
    elif xtype == 3:
        xtype, xunit = r'$2\theta$', r'$[\degree]$'
    print(f"{80*'-'}\nAdding esds and writing files...")
    esd_paths = [Path(f"{data_path}_esd"), Path(f"{bkg_path}_esd")]
    for e in esd_paths:
        if not e.exists():
            e.mkdir()
        if "data" in e.name:
            data_esd_path = e
        elif "bkg" in e.name:
            bkg_esd_path = e
    esd_calculator_writer(data_dict, basename, data_files_ext, zfill, wl, sdd,
                          xtype, xunit, type="data")
    esd_calculator_writer(bkg_dict, bkgname, data_files_ext, zfill, wl, sdd,
                          xtype, xunit, type="bkg")
    print(f"Done adding esds and writing to files.")
    data_esd_files = list(data_esd_path.glob("*.*"))
    bkg_esd_files = list(bkg_esd_path.glob("*.*"))
    plot_paths = ["png", "pdf"]
    for e in plot_paths:
        p = Path.cwd() / e
        if not p.exists():
            p.mkdir()
    print(f"{80*'-'}\nMaking stack plot of data files and bkg...")
    stack_plotter(data_bkg_dict, basename, data_files_ext, xtype, xunit, zfill,
                  type="esd")
    print(f"Stack plot of data files and bkg saved to the 'pdf' and 'png' "
          f"folders.\n{80*'-'}")
    scale_xmin = float(input(f"Lower limit of the {xtype.strip('$')} range to "
                             f"scale within: "))
    scale_xmax = float(input(f"Upper limit of the {xtype.strip('$')} range to "
                             f"scale within: "))
    print(f"{80*'-'}\nCalculating 'basecase' to use for scaling...")
    basecase = basecase_calculator(data_files_ext, scale_xmin, scale_xmax)
    print("Done calculating 'basecase' to use for scaling...")
    norm_paths = [Path(f"{data_esd_path}_normalized"),
                  Path(f"{bkg_esd_path}_normalized")]
    for e in norm_paths:
        if not e.exists():
            e.mkdir()
        if "data" in e.name:
            data_norm_path = e
        elif "bkg" in e.name:
            bkg_norm_path = e
    print(f"{80*'-'}\nNormalizing data...")
    data_scaled = normalizer(data_files_ext, basecase, scale_xmin, scale_xmax,
                             type="data")
    data_scaled = normalizer(data_files_ext, basecase, scale_xmin, scale_xmax,
                             type="bkg")
    print(f"Done normalizing data.\n{80*'-'}\nWriting .buf file.")
    buf_path = Path.cwd() / "buf_esd_normalized"
    if not buf_path.exists():
        buf_path.mkdir()
    files_norm = list(data_norm_path.glob(f"*{data_files_ext}"))
    files_norm.append(list(bkg_norm_path.glob(f"*{data_files_ext}"))[0])
    buf_writer(files_norm, buf_path)
    print("Done writing .buf file.")
    print(f"{80*'-'}\nMaking stack plot of normalized files...")
    data_files_norm = list(data_norm_path.glob(f"*{data_files_ext}"))
    bkg_file_norm = list(bkg_norm_path.glob(f"*{data_files_ext}"))
    scan_split_index, scan_split_index2 = -1, None
    data_dict_norm = data_files_to_dict(data_files_norm, scan_split_index,
                                        scan_split_index2, type="data")
    array_norm = array_from_dict(data_dict_norm)
    npy_path, csv_path = Path.cwd() / "npy", Path.cwd() / "csv"
    for p in [npy_path, csv_path]:
        if not p.exists():
            p.mkdir()
    np.save(npy_path / "data_normalized.npy", array_norm)
    df = pd.DataFrame(array_norm, 
                      columns=["x"]+list(range(array_norm.shape[1]-1)),
                      )
    df.to_csv(csv_path / "data_normalized.csv", sep=",")
    bkg_dict_norm = data_files_to_dict(bkg_file_norm, scan_split_index,
                                       scan_split_index2, type="bkg")
    data_bkg_dict_norm = data_files_to_dict(data_files_norm, scan_split_index,
                                            scan_split_index2, type="data")
    data_bkg_dict_norm["bkg"] = bkg_dict_norm["bkg"]
    stack_plotter(data_bkg_dict_norm, basename, data_files_ext, xtype, xunit,
                  zfill, type="scaled")
    print(f"Stack plot of normalized data files and bkg saved to the 'pdf' and "
          f"'png' folders.\n{80*'-'}\nSubtracting bkg from data files...")
    data_dict_bkg_sub = dict_bkg_subtract(data_dict_norm, bkg_dict_norm)
    print(f"Done subtracting bkg from data files.\n{80*'-'}\nWriting bkg "
          f"subtracted files...")
    data_bkg_sub_path = Path(f"{data_norm_path}_bkgsub")
    if not data_bkg_sub_path.exists():
        data_bkg_sub_path.mkdir()
    dict_bkg_sub_writer(data_dict_bkg_sub, basename, data_files_ext,
                        data_bkg_sub_path, zfill)
    print(f"Done writing bkg subtracted files.\n{80*'-'}\nMaking stack plot "
          f"of bkg subtracted files...")
    stack_plotter(data_dict_bkg_sub, basename, data_files_ext, xtype, xunit,
                  zfill, type="bkgsub")
    print(f"Stack plot of bkg subtracted files saved to the 'pdf' and 'png' "
          f"folders.\n{80*'-'}\nMaking overview plot of bkg subtracted "
          f"files...")
    xmin, xmax, xmin_index, xmax_index = extrema_collect(data_dict)
    data_dict_overview(data_dict_bkg_sub, f"{xtype} {xunit}",
                       f"{basename}_ss_bkgsub", xmin, xmax, xmin_index,
                       xmax_index)
    print(f"Overview plot of bkg subtracted files saved to the 'pdf' and 'png' "
          f"folders.\n{80*'-'}\nDone working with files. <(^^,)>")

    return None


if __name__ == '__main__':
    main()

# End of file
