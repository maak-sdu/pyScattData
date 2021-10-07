import sys
from pathlib import Path
import h5py
import numpy as np
import matplotlib.pyplot as plt

DPI = 300
FIGSIZE = (12,4)
FONTSIZE = 16
YLABEL = r"$I$ $[\mathrm{counts}]$"

# Billinge group colors
COLOR_DICT = dict(BG_BLUE='#0B3C5D', BG_RED='#B82601',
                  BG_GREEN='#1c6b0a', BG_LIGHTBLUE='#328CC1',
                  BG_DARKBLUE='#062F4F', BG_YELLOW='#D9B310',
                  BG_DARKRED='#984B43', BG_BORDEAUX='#76323F',
                  BG_OLIVEGREEN='#626E60', BG_YELLOWREY='#AB987A',
                  BG_BROWNORANGE='#C09F80')

COLOR = COLOR_DICT['BG_BLUE']

def h5_extract_write_plot():
    h5path = Path.cwd() / 'h5'
    if not h5path.exists():
        h5path.mkdir()
        print(f"{90*'-'}\nA folder named 'h5' has just been made.\
                \nPlease place your .h5 files here and run the script again.\
                \n{90*'-'}")
        sys.exit()
    files = list((Path.cwd() / 'h5').glob('*.h5'))
    if len(files) == 0:
        print(f"{90*'-'}\nPlease place your .h5 files in the h5 folder and run the script again.\
                \n{90*'-'}")
        sys.exit()
    print(f"{90*'-'}\nPlease provide the desired file extenstion for the summed data file. (e.g. '.xy')")
    fileext = input()
    print(f"{90*'-'}\nPlease provide the desired number of files to be sum to each .{fileext} file. (e.g. 0, 5, or 'all')")
    subframes_to_sum = input()
    print(f"{90*'-'}\nPlease state whether you want to plots (png and pdf) of your .{fileext} files. (y/n)")
    plot_req = input()
    print(f"{90*'-'}\nPlease state whether you want to verbose print to the terminal. (y/n)")
    print_req = input()
    if plot_req == 'y' or plot_req == "'y'":
        print(f"{90*'-'}\nPlease state the x quantity. ('twotheta' or 'q')")
        xquantity = input()
        if xquantity.lower() == 'q':
            print(f"{90*'-'}\nPlease state the (reciprocal) x unit. ('nm' or 'angstrom')")
            xunit = input()
            if xunit.lower() == 'nm':
                xlabel = r"$Q$ $[\mathrm{nm}^{-1}]$"
            elif xunit.lower() == 'angstrom':
                xlabel = r"$Q$ $[\mathrm{\AA}^{-1}]$"
        elif xquantity.lower() == 'twotheta':
            xlabel = r"$2\theta$ $[\degree]$"
        print(f"{90*'-'}\nSumming .h5 files, writing them to .{fileext} files, and plotting...")
    else:
        print(f"{90*'-'}\nSumming .h5 files, writing them to .{fileext} files...")
    if fileext[0] == "'" or fileext[0] == "\"":
        fileext = fileext[1:-1]
        fileext = fileext[1::]
    elif fileext[0] == ".":
        fileext = fileext[1::]
    folders = ['png', 'pdf', fileext]
    for folder in folders:
        folderpath = Path.cwd() / folder
        if not folderpath.exists():
            folderpath.mkdir()
    skipped = []
    for file in files:
        f = h5py.File(file, 'r')
        fkeys = list(f.keys())
        d = {}
        for k in fkeys:
            d[k] = f[k]
        try:
            x = d[fkeys[1]][0::]
            print(f"\t{file.name}")
        except IndexError:
            skipped.append(file.name)
            continue
        if not subframes_to_sum in ['all', "'all'", '0', '1']:
            subframes_to_sum = int(subframes_to_sum)
            subframes = d[fkeys[0]].shape[0]
            full_merges = subframes // subframes_to_sum
            remainder = subframes % subframes_to_sum
            oom_scans_merged = int(np.log10(full_merges)) + 1
            oom_scans = int(np.log10(subframes)) + 1
            for i in range(full_merges):
                scan_lower, scan_upper = 0+(i*subframes_to_sum), (subframes_to_sum-1)+(i*subframes_to_sum)
                y = np.sum(d[fkeys[0]][scan_lower:scan_upper], axis=0)
                scan_lower, scan_upper = str(scan_lower).zfill(oom_scans), str(scan_upper).zfill(oom_scans)
                i_oom = str(i).zfill(oom_scans_merged)
                if print_req == 'y':
                    print(f"\t\t{file.stem}_{i_oom}_{scan_lower}-{scan_upper}")
                xy = np.column_stack((x, y))
                np.savetxt(f'{fileext}/{file.stem}_{i_oom}_{scan_lower}-{scan_upper}.{fileext}', xy, fmt='%.10e')
                if plot_req == 'y':
                    fig = h5_to_xy_figure(x, y, xlabel)
                    plt.savefig(f"png/{file.stem}_{i_oom}_{scan_lower}-{scan_upper}.png", bbox_inches='tight')
                    plt.savefig(f"pdf/{file.stem}_{i_oom}_{scan_lower}-{scan_upper}.pdf", bbox_inches='tight')
                    plt.close()
            scan_lower, scan_upper = subframes - remainder, subframes
            y = np.sum(d[fkeys[0]][scan_lower:scan_upper], axis=0)
            scan_lower, scan_upper = str(scan_lower).zfill(oom_scans), str(scan_upper).zfill(oom_scans)
            i = i + 1
            i_oom = str(i).zfill(oom_scans_merged)
            if print_req == 'y':
                print(f"\t\t{file.stem}_{i_oom}_{scan_lower}-{scan_upper}")
            xy = np.column_stack((x, y))
            np.savetxt(f'{fileext}/{file.stem}_{i_oom}_{scan_lower}-{scan_upper}.{fileext}', xy, fmt='%.10e')
            if plot_req == 'y':
                fig = h5_to_xy_figure(x, y, xlabel)
                plt.savefig(f"png/{file.stem}_{i_oom}_{scan_lower}-{scan_upper}.png", bbox_inches='tight')
                plt.savefig(f"pdf/{file.stem}_{i_oom}_{scan_lower}-{scan_upper}.pdf", bbox_inches='tight')
                plt.close()
        elif subframes_to_sum == '0' or subframes_to_sum == '1':
            for i in range(d[fkeys[0]].shape[0]):
                y = d[fkeys[0]][i]
                xy = np.column_stack((x, y))
                oom_scans = int(np.log10(d[fkeys[0]].shape[0])) + 1
                i_oom = str(i).zfill(oom_scans)
                if print_req == 'y':
                    print(f"\t\t{file.stem}_{i_oom}")
                np.savetxt(f'{fileext}/{file.stem}_{i_oom}.{fileext}', xy, fmt='%.10e')
                if plot_req == 'y':
                    fig = h5_to_xy_figure(x, y, xlabel)
                    plt.savefig(f"png/{file.stem}_{i_oom}.png", bbox_inches='tight')
                    plt.savefig(f"pdf/{file.stem}_{i_oom}.pdf", bbox_inches='tight')
                    plt.close()
        elif subframes_to_sum == "all" or subframes_to_sum == "'all'":
            y = np.sum(d[fkeys[0]], axis=0)
            xy = np.column_stack((x, y))
            oom = int(np.log10(d[fkeys[0]].shape[0])) + 1
            scan_lower, scan_upper = str(0).zfill(oom), str(d[fkeys[0]].shape[0]).zfill(oom)
            if print_req == 'y':
                print(f"\t\t{file.stem}_{scan_lower}-{scan_upper}")
            np.savetxt(f'{fileext}/{file.stem}_{scan_lower}-{scan_upper}.{fileext}', xy, fmt='%.10e')
            if plot_req == 'y':
                fig = h5_to_xy_figure(x, y, xlabel)
                plt.savefig(f"png/{file.stem}_{scan_lower}-{scan_upper}.png", bbox_inches='tight')
                plt.savefig(f"pdf/{file.stem}_{scan_lower}-{scan_upper}.pdf", bbox_inches='tight')
                plt.close()
    if len(skipped) != 0:
        print(f"{90*'-'}\nLooks like one or more non-integrated .h5 files are present in the h5 folder:")
        for e in skipped:
            print(f"\t{e}")
        print("\nThe abovementioned files were not summed as they need to be azimuthally integrated.")
    print(f"{90*'-'}\n.{fileext} files have been written to the {fileext} folder.\
            \nPlots have been saved to the png and pdf folders.\n{90*'-'}")

    return None


def h5_to_xy_figure(x, y, xlabel):
    fig = plt.figure(dpi=DPI, figsize=FIGSIZE)
    plt.plot(x, y, c=COLOR)
    plt.xlim(np.amin(x), np.amax(x))
    plt.xlabel(xlabel, fontsize=FONTSIZE)
    plt.ylabel(YLABEL, fontsize=FONTSIZE)
    plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0))

    return fig


def main():
    h5_extract_write_plot()

    return None


if __name__ == '__main__':
    main()

# End of file.
