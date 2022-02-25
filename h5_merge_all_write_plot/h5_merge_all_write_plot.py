import sys
from pathlib import Path
import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


TWOTHETA_KEYS = ["2th", "2theta", "twotheta"]
Q_KEYS = ["q"]
INTENSITY_KEYS = ["i", "intensity", "int"]
STACK_INDICES_KEY = "stack_indices"
SCANS_KEY = "scans"

DPI = 300
FIGSIZE = (12,4)
FONTSIZE_LABELS = 20
FONTSIZE_TICKS = 14
LINEWIDTH = 1

TICKINDEX_SCAN_MAJOR = 5
TICKINDEX_SCAN_MINOR = 1
TICKINDEX_SCATT_MAJOR = 5
TICKINDEX_SCATT_MINOR = 1

COLORS = dict(bg_blue='#0B3C5D', bg_red='#B82601', bg_green='#1c6b0a',
              bg_lightblue='#328CC1', bg_darkblue='#062F4F',
              bg_yellow='#D9B310', bg_darkred='#984B43', bg_bordeaux='#76323F',
              bg_olivegreen='#626E60', bg_yellowgrey='#AB987A',
              bg_brownorange='#C09F80')
COLOR = COLORS['bg_blue']

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
CMAP = CMAPS[0]


def h5_extract_to_dict(h5_file):
    f = h5py.File(h5_file, mode="r")
    d = {}
    fkeys = list(f.keys())
    if "entry" in fkeys:
        fkeys = list(f["entry"].keys())
    for k in fkeys:
        d[k.lower()] = np.array(f[k])

    return d


def dict_to_xy_write(d, fname):
    scannumber = int(str(fname).split("-")[-1])
    twotheta, q, intensity = None, None, None
    dkeys = d.keys()
    for k in TWOTHETA_KEYS:
        if k in dkeys:
            twotheta = d[k]
    for k in Q_KEYS:
        if k in dkeys:
            q = d[k]
    if SCANS_KEY in dkeys:
        intensity = d[SCANS_KEY][scannumber]
    if isinstance(twotheta, np.ndarray) and isinstance(intensity, np.ndarray):
        x, y = twotheta, intensity
        xy = np.column_stack((x,y))
        h = "2theta\tintensity"
    elif isinstance(q, np.ndarray) and isinstance(intensity, np.ndarray):
        x, y = q, intensity
        xy = np.column_stack((x,y))
        h = "2theta\tintensity"
    np.savetxt(f"xy/{fname}.xy", xy, encoding="utf-8", header=h)

    return None


def dict_to_plot(d, fname):
    scannumber = int(str(fname).split("-")[-1])
    twotheta, q, intensity = None, None, None
    dkeys = d.keys()
    for k in TWOTHETA_KEYS:
        if k in dkeys:
            twotheta = d[k]
    for k in Q_KEYS:
        if k in dkeys:
            q = d[k]
    if SCANS_KEY in dkeys:
        intensity = d[SCANS_KEY][scannumber]
    if isinstance(twotheta, np.ndarray) and isinstance(intensity, np.ndarray):
        x, y = twotheta, intensity
        xlabel = r"$2\theta$ $[\degree]$"
    elif isinstance(q, np.ndarray) and isinstance(intensity, np.ndarray):
        x, y = q, intensity
        xlabel = r"$Q$ $[\mathrm{\AA}^{-1}]$"
    plt.figure(dpi=DPI, figsize=FIGSIZE)
    plt.plot(x, y, c=COLOR, lw=LINEWIDTH)
    plt.xlim(np.amin(x), np.amax(x))
    plt.xlabel(xlabel, fontsize=FONTSIZE_LABELS)
    plt.ylabel(r"$I$ $[\mathrm{arb. u.}]$", fontsize=FONTSIZE_LABELS)
    plt.tick_params(axis='both', which='major', labelsize=FONTSIZE_LABELS)
    plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
    plt.savefig(f"png/{fname}.png", bbox_inches="tight")
    plt.savefig(f"pdf/{fname}.pdf", bbox_inches="tight")
    plt.close()

    return None


def merge_dict_subscans(d):
    twotheta, q, intensity = None, None, None
    dkeys = d.keys()
    d_merged = {}
    for k in TWOTHETA_KEYS:
        if k in dkeys:
            twotheta = d[k]
            d_merged[k] = twotheta
    for k in Q_KEYS:
        if k in dkeys:
            q = d[k]
            d_merged[k] = q
    for k in INTENSITY_KEYS:
        if k in dkeys:
            intensity = d[k]
            intensity_key = k
    if isinstance(intensity, np.ndarray):
        number_of_scans = intensity.shape[0]
        stack = intensity[0, :]
        for i in range(1, number_of_scans):
            stack += intensity[i, :]

    return stack


def dict_to_overview_plot(d, fname):
    fname = str(fname).split("-")[0:-1][0]
    twotheta, q, = None, None
    dkeys = d.keys()
    for k in TWOTHETA_KEYS:
        if k in dkeys:
            twotheta = d[k]
    for k in Q_KEYS:
        if k in dkeys:
            q = d[k]
    scannumbers = list(d[SCANS_KEY].keys())
    intensities = d[SCANS_KEY][scannumbers[0]]
    for i in range(1, len(scannumbers)):
        intensities = np.column_stack((intensities,
                                       d[SCANS_KEY][scannumbers[i]]))
    if isinstance(twotheta, np.ndarray):
        x = twotheta
        xlabel = r"$2\theta$ $[\degree]$"
    elif isinstance(q, np.ndarray):
        x = q
        xlabel = r"$Q$ $[\mathrm{\AA}^{-1}]$"
    y = intensities
    fig, ax = plt.subplots(dpi=DPI, figsize=FIGSIZE)
    im = plt.imshow(intensities,
                    interpolation='nearest',
                    origin='lower',
                    vmin=np.amin(y),vmax=np.amax(y),
                    extent=(0, len(scannumbers), np.amax(x), np.amin(x)),
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
    plt.savefig(f"png/{fname}_overview.png", bbox_inches="tight")
    plt.savefig(f"pdf/{fname}_overview.pdf", bbox_inches="tight")
    plt.close()

    return None


def main():
    h5_path = Path.cwd() / "h5"
    if not h5_path.exists():
        h5_path.mkdir()
        print(f"{80*'-'}\nA folder called 'h5' has been created. Please "
              f"place your .h5 files there and\nrerun the code.\n{80*'-'}")
        sys.exit()
    h5_files = list(h5_path.glob("*.h5"))
    if len(h5_files) == 0:
        print(f"{80*'-'}\nNo .h5 files were found in the 'h5' folder. Please "
              f"place your .h5 files there\nand rerun the code.\n{80*'-'}")
        sys.exit()
    output_paths = ["xy", "png", "pdf"]
    for e in output_paths:
        p = Path.cwd() / e
        if not p.exists():
            p.mkdir()
    d_merged = {"scans":{}}
    plotreq = input(f"{80*'-'}\nPlease state whether you would like individual "
                    f"plots of all merged scans (y/n): ")
    while plotreq.lower() not in ["y", "n"]:
        plotreq = input("Please state whether you would like individual plots"
                    " of all merged scans (y/n): ")
    print(f"{80*'-'}\nWriting files...")
    for h5_file in h5_files:
        print(f"\t{h5_file.name}")
        d = h5_extract_to_dict(h5_file)
        for k in TWOTHETA_KEYS:
            if k in d.keys() and k not in d_merged.keys():
                d_merged[k] = d[k]
        for k in Q_KEYS:
            if k in d.keys() and k not in d_merged.keys():
                d_merged[k] = d[k]
        fname = h5_file.stem
        scannumber = int(str(h5_file.stem).split("-")[-1])
        stack = merge_dict_subscans(d)
        d_merged[SCANS_KEY][scannumber] = stack
        dict_to_xy_write(d_merged, fname)
    print("Done writing files.")
    if plotreq.lower() == "y":
        print(f"{80*'-'}\nPlotting individual merged scans...")
        for h5_file in h5_files:
            print(f"\t\t{h5_file.name}")
            fname = h5_file.stem
            dict_to_plot(d_merged, fname)
        print("Done plotting merged scans individually.")
    print(f"{80*'-'}\nPlotting all merged scans in overwiew plot...")
    dict_to_overview_plot(d_merged, fname)
    print(f"Done with overview plot.\n{80*'-'}\nPlease see the 'xy' folder for "
          f".xy files containing merged scans. Please see the\n'pdf' and 'png' "
          f"folders for plots.\n{80*'-'}")

    return None


if __name__ == "__main__":
    main()

# End of file.
