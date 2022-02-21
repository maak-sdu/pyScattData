import sys
from pathlib import Path
import h5py
import numpy as np
import matplotlib.pyplot as plt
from skbeam.core.utils import twotheta_to_q


twotheta_keys = ["2th", "2theta", "twotheta"]
q_keys = ["q"]
intensity_keys = ["i", "intensity", "int"]

DPI = 300
FIGSIZE = (12,4)
FONTSIZE_LABELS = 20
FONTSIZE_TICKS = 14
LINEWIDTH = 1
COLORS = dict(bg_blue='#0B3C5D', bg_red='#B82601', bg_green='#1c6b0a',
              bg_lightblue='#328CC1', bg_darkblue='#062F4F', bg_yellow='#D9B310',
              bg_darkred='#984B43', bg_bordeaux='#76323F', bg_olivegreen='#626E60',
              bg_yellowgrey='#AB987A', bg_brownorange='#C09F80')
COLOR = COLORS["bg_blue"]


def h5_extract_to_dict(h5_file):
    f = h5py.File(h5_file, mode="r")
    d = {}
    fkeys = list(f.keys())
    for k in fkeys:
        d[k.lower()] = np.array(f[k])

    return d


def dict_to_xy_write(d, fname):
    dkeys = d.keys()
    for k in twotheta_keys:
        if k in dkeys:
            twotheta = d[k]
    for k in q_keys:
        if k in dkeys:
            q = d[k]
    for k in intensity_keys:
        if k in dkeys:
            intensity = d[k]
    if isinstance(twotheta, np.ndarray) and isinstance(intensity, np.ndarray):
        zfill = len(str(intensity.shape[0]))
        for i in range(intensity.shape[0]):
            print(f"\t\t\t{i}")
            x, y = twotheta, intensity[i,:]
            xy = np.column_stack((x,y))
            h = "2theta\tintensity"
            np.savetxt(f"xy/{fname}_{str(i).zfill(zfill)}.xy", xy, encoding="utf-8", header=h)

    return None


def dict_to_plot(d, fname):
    dkeys = d.keys()
    for k in twotheta_keys:
        if k in dkeys:
            twotheta = d[k]
    for k in q_keys:
        if k in dkeys:
            q = d[k]
    for k in intensity_keys:
        if k in dkeys:
            intensity = d[k]
    if isinstance(twotheta, np.ndarray) and isinstance(intensity, np.ndarray):
        zfill = len(str(intensity.shape[0]))
        for i in range(intensity.shape[0]):
            print(f"\t\t\t{i}")
            x, y = twotheta, intensity[i,:]
            plt.figure(dpi=DPI, figsize=FIGSIZE)
            plt.plot(x, y, c=COLOR, lw=LINEWIDTH)
            plt.xlim(np.amin(x), np.amax(x))
            plt.xlabel(r"$2\theta$ $[\degree]$", fontsize=FONTSIZE_LABELS)
            plt.ylabel(r"$I$ $[\mathrm{arb. u.}]$", fontsize=FONTSIZE_LABELS)
            plt.tick_params(axis='both', which='major', labelsize=FONTSIZE_LABELS)
            plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
            plt.savefig(f"png/{fname}_{str(i).zfill(zfill)}.png",
                        bbox_inches="tight")
            plt.savefig(f"pdf/{fname}_{str(i).zfill(zfill)}.pdf",
                        bbox_inches="tight")
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
    print("Working w. files...")
    for h5_file in h5_files:
        print(f"\t{h5_file.name}")
        fname = h5_file.stem
        d = h5_extract_to_dict(h5_file)
        print("\t\tWriting to two-column files...")
        dict_to_xy_write(d, fname)
        print("\t\tPlotting...")
        dict_to_plot(d, fname)
    print(f"\nDone working w. files.\n{80*'-'}")

    return None


if __name__ == "__main__":
    main()

# End of file.
