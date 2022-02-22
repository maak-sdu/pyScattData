import sys
from pathlib import Path
import h5py
import numpy as np
import matplotlib.pyplot as plt


TWOTHETA_KEYS = ["2th", "2theta", "twotheta"]
Q_KEYS = ["q"]
INTENSITY_KEYS = ["i", "intensity", "int"]
STACK_INDICES_KEY = "stack_indices"

DPI = 300
FIGSIZE = (12,4)
FONTSIZE_LABELS = 20
FONTSIZE_TICKS = 14
LINEWIDTH = 1
COLORS = dict(bg_blue='#0B3C5D', bg_red='#B82601', bg_green='#1c6b0a',
              bg_lightblue='#328CC1', bg_darkblue='#062F4F',
              bg_yellow='#D9B310', bg_darkred='#984B43', bg_bordeaux='#76323F',
              bg_olivegreen='#626E60', bg_yellowgrey='#AB987A',
              bg_brownorange='#C09F80')
COLOR = COLORS["bg_blue"]


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
    twotheta, q, intensity = None, None, None
    dkeys = d.keys()
    for k in TWOTHETA_KEYS:
        if k in dkeys:
            twotheta = d[k]
    for k in Q_KEYS:
        if k in dkeys:
            q = d[k]
    for k in INTENSITY_KEYS:
        if k in dkeys:
            intensity = d[k]
    if STACK_INDICES_KEY in dkeys:
        stack_indices = d[STACK_INDICES_KEY]
    if isinstance(twotheta, np.ndarray) and isinstance(intensity, np.ndarray):
        zfill = len(str(intensity.shape[0]))
        for i in range(intensity.shape[0]):
            if STACK_INDICES_KEY in dkeys:
                print(f"\t\t\t{stack_indices[i]}")
            else:
                print(f"\t\t\t{i}")
            x, y = twotheta, intensity[i,:]
            xy = np.column_stack((x,y))
            h = "2theta\tintensity"
            if STACK_INDICES_KEY in dkeys:
                np.savetxt(f"xy/{fname}_{stack_indices[i]}.xy", xy,
                           encoding="utf-8", header=h)
            else:
                np.savetxt(f"xy/{fname}_{str(i).zfill(zfill)}.xy", xy,
                           encoding="utf-8", header=h)
    elif isinstance(q, np.ndarray) and isinstance(intensity, np.ndarray):
        zfill = len(str(intensity.shape[0]))
        for i in range(intensity.shape[0]):
            if STACK_INDICES_KEY in dkeys:
                print(f"\t\t\t{stack_indices[i]}")
            else:
                print(f"\t\t\t{i}")
            x, y = q, intensity[i,:]
            xy = np.column_stack((x,y))
            h = "q\tintensity"
            if STACK_INDICES_KEY in dkeys:
                np.savetxt(f"xy/{fname}_{stack_indices[i]}.xy", xy,
                           encoding="utf-8", header=h)
            else:
                np.savetxt(f"xy/{fname}_{str(i).zfill(zfill)}.xy", xy,
                           encoding="utf-8", header=h)

    return None


def dict_to_plot(d, fname):
    twotheta, q, intensity = None, None, None
    dkeys = d.keys()
    for k in TWOTHETA_KEYS:
        if k in dkeys:
            twotheta = d[k]
    for k in Q_KEYS:
        if k in dkeys:
            q = d[k]
    for k in INTENSITY_KEYS:
        if k in dkeys:
            intensity = d[k]
    if STACK_INDICES_KEY in dkeys:
        stack_indices = d[STACK_INDICES_KEY]
    if isinstance(twotheta, np.ndarray) and isinstance(intensity, np.ndarray):
        zfill = len(str(intensity.shape[0]))
        for i in range(intensity.shape[0]):
            if STACK_INDICES_KEY in dkeys:
                print(f"\t\t\t{stack_indices[i]}")
            else:
                print(f"\t\t\t{i}")
            x, y = twotheta, intensity[i,:]
            plt.figure(dpi=DPI, figsize=FIGSIZE)
            plt.plot(x, y, c=COLOR, lw=LINEWIDTH)
            plt.xlim(np.amin(x), np.amax(x))
            plt.xlabel(r"$2\theta$ $[\degree]$", fontsize=FONTSIZE_LABELS)
            plt.ylabel(r"$I$ $[\mathrm{arb. u.}]$", fontsize=FONTSIZE_LABELS)
            plt.tick_params(axis='both', which='major',
                            labelsize=FONTSIZE_LABELS)
            plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
            if STACK_INDICES_KEY in dkeys:
                plt.savefig(f"png/{fname}_{stack_indices[i]}.png",
                            bbox_inches="tight")
                plt.savefig(f"pdf/{fname}_{stack_indices[i]}.pdf",
                            bbox_inches="tight")
            else:
                plt.savefig(f"png/{fname}_{str(i).zfill(zfill)}.png",
                            bbox_inches="tight")
                plt.savefig(f"pdf/{fname}_{str(i).zfill(zfill)}.pdf",
                            bbox_inches="tight")
            plt.close()
    if isinstance(q, np.ndarray) and isinstance(intensity, np.ndarray):
        zfill = len(str(intensity.shape[0]))
        for i in range(intensity.shape[0]):
            if STACK_INDICES_KEY in dkeys:
                print(f"\t\t\t{stack_indices[i]}")
            else:
                print(f"\t\t\t{i}")
            x, y = q, intensity[i,:]
            plt.figure(dpi=DPI, figsize=FIGSIZE)
            plt.plot(x, y, c=COLOR, lw=LINEWIDTH)
            plt.xlim(np.amin(x), np.amax(x))
            if np.amax(q) > 40 :
                plt.xlabel(r"$Q$ $[\mathrm{nm}^{-1}]$",
                           fontsize=FONTSIZE_LABELS)
            else:
                plt.xlabel(r"$Q$ $[\mathrm{\AA}^{-1}]$",
                           fontsize=FONTSIZE_LABELS)
            plt.ylabel(r"$I$ $[\mathrm{arb. u.}]$", fontsize=FONTSIZE_LABELS)
            plt.tick_params(axis='both', which='major',
                            labelsize=FONTSIZE_LABELS)
            plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
            if STACK_INDICES_KEY in dkeys:
                plt.savefig(f"png/{fname}_{stack_indices[i]}.png",
                            bbox_inches="tight")
                plt.savefig(f"pdf/{fname}_{stack_indices[i]}.pdf",
                            bbox_inches="tight")
            else:
                plt.savefig(f"png/{fname}_{str(i).zfill(zfill)}.png",
                            bbox_inches="tight")
                plt.savefig(f"pdf/{fname}_{str(i).zfill(zfill)}.pdf",
                            bbox_inches="tight")
            plt.close()

    return None


def merge_dict(d):
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
        zfill = len(str(intensity.shape[0]))
        number_of_scans = intensity.shape[0]
        scans_to_stack = int(input("\t\t\tHow many scans should stacked "
                                   "together?: "))
        full_stacks = number_of_scans // scans_to_stack
        remainder_to_stack = number_of_scans % scans_to_stack
        stack_indices = []
        for i in range(full_stacks):
            stack = intensity[i*scans_to_stack, :]
            stack_indices_str = str(i*scans_to_stack).zfill(zfill)
            for j in range(1, scans_to_stack):
                stack += intensity[i*scans_to_stack+j, :]
            stack_indices.append(f"{stack_indices_str}-"
                                 f"{str(i*scans_to_stack+j).zfill(zfill)}")
            if i == 0:
                d_merged[intensity_key] = stack
            else:
                d_merged[intensity_key] = np.vstack((d_merged[intensity_key],
                                                     stack))
        if remainder_to_stack != 0:
            stack = intensity[(full_stacks * scans_to_stack),:]
            stack_indices_str = str(full_stacks * scans_to_stack).zfill(zfill)
            for j in range(1, remainder_to_stack-1):
                stack = intensity[(full_stacks * scans_to_stack) + 1 + j,:]
            if remainder_to_stack == 1:
                stack_indices.append(f"{stack_indices_str}")
            else:
                last_scan = str((full_stacks*scans_to_stack)+1+j).zfill(zfill)
                stack_indices.append(f"{stack_indices_str}-{last_scan}")
            d_merged[intensity_key] = np.vstack((d_merged[intensity_key],
                                                 stack))
        d_merged[STACK_INDICES_KEY] = stack_indices

    return d_merged


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
        try:
            print(f"{80*'-'}\n\tFile: {h5_file.name}")
            fname = h5_file.stem
            d = h5_extract_to_dict(h5_file)
            for k in INTENSITY_KEYS:
                if k in d.keys():
                    print(f"\t\tNumber of scans: {d[k].shape[0]}")
            mergereq = input("\t\tDo you want to merge any of the scans? "
                             "(y/n): ")
            while mergereq not in ["y", "n"]:
                mergereq = input("\t\tDo you want to merge any of the scans? "
                                 "(y/n): ")
            if mergereq == "y":
                writereq = input("\t\tDo you want to write .xy files for all "
                                 "merged scans? (y/n): ")
                while writereq not in ["y", "n"]:
                    writereq = input("\t\tDo you want to write .xy files for "
                                     "all merged scans? (y/n): ")
            else:
                writereq = input("\t\tDo you want to write .xy files for all "
                                 "scans? (y/n): ")
                while writereq not in ["y", "n"]:
                    writereq = input("\t\tDo you want to write .xy files for "
                                     "merged scans? (y/n): ")
            if mergereq == "y":
                plotreq = input("\t\tDo you want to plot all merged scans? "
                                "(y/n): ")
                while plotreq not in ["y", "n"]:
                    plotreq = input("\t\tDo you want to plot all merged scans? "
                                     "(y/n): ")
            else:
                plotreq = input("\t\tDo you want to plot all scans? (y/n): ")
                while plotreq not in ["y", "n"]:
                    plotreq = input("\t\tDo you want to plot all scans? "
                                     "(y/n): ")
            if mergereq.lower() == "y":
                d_merged = merge_dict(d)
                if writereq == "y":
                    print("\t\tWriting to two-column files of merged scans...")
                    dict_to_xy_write(d_merged, fname)
                    print("\t\tPlotting merged scans...")
                if plotreq == "y":
                    dict_to_plot(d_merged, fname)
            else:
                if writereq == "y":
                    print("\t\tWriting to two-column files for each scan...")
                    dict_to_xy_write(d, fname)
                if plotreq == "y":
                    print("\t\tPlotting each scan...")
                    dict_to_plot(d, fname)
        except KeyError:
            print(f"\t\tThis file seems to contain non-integrated data. File "
                   "skipped.")
    print(f"{80*'-'}\nDone working w. files.\n{80*'-'}")

    return None


if __name__ == "__main__":
    main()

# End of file.
