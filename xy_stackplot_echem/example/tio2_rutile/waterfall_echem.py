import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from diffpy.utils.parsers.loaddata import loadData
import matplotlib.ticker as ticker


DPI = 300
FIGSIZE = (12,4)
X_LABEL = r"$r$ $[\mathrm{\AA}]$"
Y_LABEL = r"$G$ $[\mathrm{\AA}^{-2}]$"
FONTSIZE_LABELS = 20
FONTSIZE_TICKS = 14
XMIN, XMAX = 1, 50
YFRACOFFSET = 0.75
PLOTFREQ = 5
COLORSCHEME = 'blue'


def scatt_load(scatt_files, plot_freq):
    scatt_files_i = [i for i in range(0, len(scatt_files))
                     if i % plot_freq == 0]
    scatt_files_picked = [scatt_files[i] for i in scatt_files_i]
    print("\nScattering data files to be plotted:")
    for e in scatt_files_picked:
        print(f"\t{e.name}")
    scatt_data = [loadData(file) for file in scatt_files_picked]

    return scatt_data


def echem_load(echem_files):
    maccor_echem_file = list((Path.cwd() / 'data').glob('*.txt'))[0]
    with open(maccor_echem_file, 'r') as input_file:
        lines = input_file.readlines()
    for i,line in enumerate(lines):
        if "Rec	Cycle P	Cycle C	Step	TestTime	StepTime" in line:
            start = i + 3
    time_min_pre, time_min, time_s, time_h, voltage = [], [], [], [], []
    for i in range(start, len(lines)):
        time = float(lines[i].split()[4])
        time_min_pre.append(time)
        voltage.append(float(lines[i].split()[9]))
    for i in range(0, len(time_min_pre)):
        time_min_corrected = time_min_pre[i] - time_min_pre[0]
        time_min.append(time_min_corrected)
        time_s.append(time_min_corrected * 60)
        time_h.append(time_min_corrected / 60)
    time, time_min_pre, voltage = np.array(time), np.array(time_min_pre), np.array(voltage)
    time_min_corrected, time_min = np.array(time_min_corrected), np.array(time_min)
    time_s, time_h = np.array(time_s), np.array(time_h)
    echem_data = np.column_stack((time_h, voltage))

    return echem_data


def waterfall_echem_plot(scatt_data, echem_data, scatt_ext, plot_freq):
    scatt_files_i = [i for i in range(0, len(scatt_data)) if i % plot_freq == 0]
    scatt_files_picked = [scatt_data[i] for i in scatt_files_i]
    data = [scatt_dataset for scatt_dataset in scatt_data]
    x = data[0][:,0]
    ymin = [np.amin(dataset[:,1]) for dataset in data]
    ymax = [np.amax(dataset[:,1]) for dataset in data]
    ymin = min(ymin)
    ymax = max(ymax)
    yoffset = [data[i][:,1] + i*YFRACOFFSET*(ymax-ymin) for i in range(0, len(data))]
    yoff_min = np.amin(yoffset)
    yoff_max = np.amax(yoffset)
    yoff_range = yoff_max - yoff_min
    yaxis_min = yoff_min - 0.01 * yoff_range
    yaxis_max = yoff_max + 0.01 * yoff_range
    scatt_ext = scatt_ext.split(".")[-1]
    time_h, voltage = echem_data[:,0], echem_data[:,1]
    if COLORSCHEME == 'grey':
        colors = plt.cm.Greys(np.linspace(0.5, 1, len(data)+1))
    elif COLORSCHEME == 'purple':
        colors = plt.cm.Purples(np.linspace(0.5, 1, len(data)+1))
    elif COLORSCHEME == 'blue':
        colors = plt.cm.Blues(np.linspace(1, 0.5, len(data)+1))
    elif COLORSCHEME == 'green':
        colors = plt.cm.Greens(np.linspace(0.5, 1, len(data)+1))
    elif COLORSCHEME == 'orange':
        colors = plt.cm.Oranges(np.linspace(0.5, 1, len(data)+1))
    elif COLORSCHEME == 'red':
        colors = plt.cm.Reds(np.linspace(0.5, 1, len(data)+1))
    fig = plt.figure(dpi=DPI, figsize=FIGSIZE, constrained_layout=True)
    gs = fig.add_gridspec(1,4)
    fig_ax0 = fig.add_subplot(gs[0,:-1])
    fig_ax1 = fig.add_subplot(gs[0,3])
    for i in range(0, len(yoffset)):
        fig_ax0.plot(x, yoffset[i], c=colors[i])
    fig_ax0.set_xlim(XMIN, XMAX)
    fig_ax0.set_ylim(yaxis_min, yaxis_max)
    fig_ax0.set_xlabel(X_LABEL, fontsize=FONTSIZE_LABELS)
    fig_ax0.set_ylabel(Y_LABEL, fontsize=FONTSIZE_LABELS)
    fig_ax0.xaxis.set_major_locator(ticker.MultipleLocator(5))
    fig_ax0.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    fig_ax0.yaxis.set_major_locator(ticker.MultipleLocator(5))
    fig_ax0.yaxis.set_minor_locator(ticker.MultipleLocator(1))
    fig_ax0.xaxis.set_tick_params(labelsize=FONTSIZE_TICKS)
    fig_ax0.yaxis.set_tick_params(labelsize=FONTSIZE_TICKS)
    fig_ax1.plot(voltage, time_h, c=colors[0])
    fig_ax1.yaxis.tick_right()
    fig_ax1.set_xlabel(r'$V$ $[\mathrm{V}]$', fontsize=FONTSIZE_LABELS)
    fig_ax1.set_ylabel(r'$t$ $[\mathrm{h}]$', fontsize=FONTSIZE_LABELS)
    fig_ax1.xaxis.set_major_locator(ticker.MultipleLocator(0.5))
    fig_ax1.xaxis.set_minor_locator(ticker.MultipleLocator(0.25))
    fig_ax1.yaxis.set_major_locator(ticker.MultipleLocator(5))
    fig_ax1.yaxis.set_minor_locator(ticker.MultipleLocator(1))
    fig_ax1.yaxis.set_label_position('right')
    fig_ax1.xaxis.set_tick_params(labelsize=FONTSIZE_TICKS)
    fig_ax1.yaxis.set_tick_params(labelsize=FONTSIZE_TICKS)
    fig_ax1.set_xlim(1, 3)
    fig_ax1.set_ylim(np.amin(time_h), np.amax(time_h))
    fig_ax1.invert_xaxis()
    scatt_ext = scatt_ext.split(".")[-1]
    plt.savefig(f"png/{scatt_ext}_waterfall.png", bbox_inches="tight")
    plt.savefig(f"pdf/{scatt_ext}_waterfall.pdf", bbox_inches="tight")
    # Vertical lines
    # plt.axvline(x=2.0, ls='--', lw=0.5, c='k')
    # plt.axvline(x=2.85, ls='--', lw=0.5, c='k')
    # plt.axvline(x=4.5, ls='--', lw=0.5, c='k')
    # Rectangles
    # ax.add_patch(patches.Rectangle((1.6, yaxis_min*0.925), 0.6, (yaxis_max - yaxis_min)*0.991,
    #                                 ls='--', lw=0.5, ec='r', fc='none'))
    # ax.add_patch(patches.Rectangle((2.7, yaxis_min*0.925), 0.6, (yaxis_max - yaxis_min)*0.991,
    #                                 ls='--', lw=0.5, ec='orange', fc='none'))
    # ax.add_patch(patches.Rectangle((4.0, yaxis_min*0.925), 0.7, (yaxis_max - yaxis_min)*0.991,
    #                                 ls='--', lw=0.5, ec='g', fc='none'))
    # ax.add_patch(patches.Rectangle((8.0, yaxis_min*0.925), 1.0, (yaxis_max - yaxis_min)*0.991,
    #                                 ls='--', lw=0.5, ec='b', fc='none'))

    return None


def main():
    data_path = Path.cwd() / "data"
    if not data_path.exists():
        data_path.mkdir()
        print(f"{80*'-'}\nA folder called 'data' has been created. Please "
              f"place your data files here and\nrerun the code.\n{80*'-'}")
        sys.exit()
    scatt_ext = input(f"{80*'-'}\nPlease provide the file extension for the "
                      f"scattering data (e.g. '.gr'): ")
    scatt_files = list(data_path.glob(f"*{scatt_ext}"))
    if len(scatt_files) == 0:
        print(f"{80*'-'}\nNo {scatt_ext} files were found in the 'data' "
              f"folder. Please place your data files here\nand rerun the code."
              f"\n{80*'-'}")
        sys.exit()
    else:
        print(f"\t{len(scatt_files)} {scatt_ext} files were found in the "
              f"'data' folder.")
    echem_ext = input(f"\nPlease provide the file extension for the "
                      f"electrochemical data (e.g. '.txt'): ")
    echem_files = list(data_path.glob(f"*{echem_ext}"))
    if len(echem_files) < 1:
        print(f"{80*'-'}\nNo {echem_ext} files were found in the 'data' "
              f"folder. Please place your data files here\nand rerun the code."
              f"\n{80*'-'}")
        sys.exit()
    elif len(echem_files) > 1:
        print(f"\t{len(echem_files)} files were found in the 'data' folder. "
              f"Please review and place only\n\tone {echem_ext} file there and "
              f"rerun the code.\n{80*'-'}")
        sys.exit()
    else:
        print(f"\techem file:\t{echem_files[0].name}")
    folders = ['png', 'pdf']
    for folder in folders:
        if not (Path.cwd() / folder).exists():
            (Path.cwd() / folder).mkdir()
    plot_freq = int(input("\nPlease provide the interval at which you like to "
                           "plot the scattering data files: "))
    scatt_data = scatt_load(scatt_files, plot_freq)
    echem_data = echem_load(echem_files)
    print(f"{80*'-'}\nPlotting...")
    waterfall_echem_plot(scatt_data, echem_data, scatt_ext, plot_freq)
    print(f"Done plotting.\n{80*'-'}\nPlease see the 'pdf' and 'png' folders."
          f"\n{80*'-'}")

    return None


if __name__ == "__main__":
    main()

# End of file.
