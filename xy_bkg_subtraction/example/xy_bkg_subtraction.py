import sys
import re
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
from matplotlib import colormaps
import matplotlib.pyplot as plt

D_PLOT = dict(dpi=600,
              figsize=(8, 6),
              cmap="viridis",
              cmap_bad="white",
              aspect="auto",
              interpolation="antialiased",
              origin="upper",
              vmax_scale=2.5,
              fontsize_labels=20,
              fontsize_ticks=14,
              pad_labels=10,
              tick_width_major=1.5,
              tick_width_minor=0.75,
              xlabel="$t\;[\mathrm{h}]$",
              ylabel="$Q\;[\mathrm{\AA}^{-1}]$",
              cbarlabel="$I\;[\mathrm{counts}]$",
              )


def get_times(raw):
    with raw.open("rb") as f:
        rb = f.read()
    s = str(rb).split("\\x00")
    s = [e for e in s if not e == ""][1]
    s = f"{s[0:7]}20{s[7:]}"
    dt= datetime.strptime(s,"%d-%b-%Y %H:%M")
    timestamp = dt.timestamp()
    mtime = raw.stat().st_mtime
    
    return timestamp, mtime


def get_exposure_time(raw):
    with raw.open("rb") as f:
        rb = f.read()
    s = str(rb).split("\\x00")
    s = [e for e in s if not e == ""][4].split()[-1]
    value_list, unit_list = re.findall("\d", s), re.findall("\D", s)
    value, unit = "", ""
    for e in value_list:
        value += e
    for e in unit_list:
        unit += e
    if unit == "min":
        value = float(value) * 60
    elif unit == "h":
        value = float(value) * 60**2

    return value


def xy_to_dict(xy):
    data = np.loadtxt(xy)

    return dict(x=data[:, 0], y=data[:, 1])


def xy_scale(y, y_bkg, oom):
    scale = 1
    y_diff = y - (scale * y_bkg)
    if (y_diff >= 0).all():
        upscale = True
        downscale = False
    else:
        upscale = False
        downscale = True
    while upscale:
        scale += oom
        y_diff = y - (scale * y_bkg)
        if (y_diff >= 0).all():
            upscale = True
        else:
            upscale = False
            scale -= oom
    while downscale:
        scale -= oom
        y_diff = y - (scale * y_bkg)
        if (y_diff < 0).any():
            downscale = True
        else:
            downscale = False

    return scale


def dict_to_array(d):
    for i, k in enumerate(list(d.keys())):
        if i == 0:
            array = np.column_stack((d[k]["x"], d[k]["y"]))
        else:
            array = np.column_stack((array, d[k]["y"]))

    return array


def plot(array, duration_h, d_plot, basename, output_paths):
    x, y = array[:, 0], array[:, 1:]
    y_masked = np.ma.masked_where(y < 0, y)
    cmap = colormaps[d_plot["cmap"]].set_bad(color=d_plot["cmap_bad"])
    fig, ax = plt.subplots(dpi=600, figsize=(12, 5))
    im = ax.imshow(y_masked,
                   cmap=cmap,
                   interpolation=d_plot["interpolation"],
                   aspect=d_plot["aspect"],
                   origin=d_plot["origin"],
                   vmin=0,
                   vmax=np.amax(y) / d_plot["vmax_scale"],
                   extent=(0, duration_h, np.amax(x), np.amin(x)),
                   )
    ax.tick_params(axis="x",
                   which="major",
                   bottom=True,
                   labelbottom=False,
                   top=True,
                   labeltop=True,
                   direction="in",
                   labelsize=d_plot["fontsize_ticks"],
                   width=d_plot["tick_width_major"],
                   )
    ax.tick_params(axis="x",
                   which="minor",
                   bottom=True,
                   labelbottom=False,
                   top=True,
                   labeltop=True,
                   direction="in",
                   width=d_plot["tick_width_minor"],
                   )
    ax.tick_params(axis="y",
                   which="major",
                   right=True,
                   labelright=False,
                   left=True,
                   labelleft=True,
                   direction="in",
                   labelsize=d_plot["fontsize_ticks"],
                   width=d_plot["tick_width_major"],
                   )
    ax.tick_params(axis="y",
                   which="minor",
                   right=True,
                   labelright=False,
                   left=True,
                   labelleft=True,
                   direction="in",
                   width=d_plot["tick_width_minor"],
                   )    
    ax.minorticks_on()
    ax.set_xlabel(d_plot["xlabel"],
                  fontsize=d_plot["fontsize_labels"],
                  labelpad=d_plot["pad_labels"],
                  )
    ax.xaxis.set_label_position("top")
    ax.set_ylabel(d_plot["ylabel"],
                  fontsize=d_plot["fontsize_labels"],
                  labelpad=d_plot["pad_labels"],
                  )
    cbar = plt.colorbar(im)
    cbar.set_label(d_plot["cbarlabel"],
                   fontsize=d_plot["fontsize_labels"],
                   labelpad=d_plot["pad_labels"],
                   )
    cbar.formatter.set_powerlimits((0, 0))
    for p in output_paths:
        print(f"\t{p.name}")
        plt.savefig(p / f"{basename}.{p.name}", bbox_inches="tight")
    plt.close()

    return None


def main():
    print(f"{Path(__file__).name}\n{80*'-'}\nPlot settings can be found in the "
          f"top of the file.\n{80*'-'}\nCurrent plot settings:"
          )
    for k, v in D_PLOT.items():
        print(f"\t{k}: {v}")
    data_path = Path.cwd() / "data"
    if not data_path.exists():
        data_path.mkdir()
        sys.exit(f"{80*'-'}\nA folder called '{data_path.name}' has been "
                 f"created.\nPlease place your data files there and rerun the "
                 f"program.\n{80*'-'}"
                 )
    bkg_path = Path.cwd() / "bkg"
    if not bkg_path.exists():
        bkg_path.mkdir()
        sys.exit(f"{80*'-'}\nA folder called '{bkg_path.name}' has been "
                 f"created.\nPlease place your background file there and rerun "
                 f"the program.\n{80*'-'}"
                 )
    data_files = list(data_path.glob("*.*"))
    if len(data_files) == 0:
        sys.exit(f"{80*'-'}\nNo files were found in the '{data_path.name}' "
                 f"folder.\nPlease place your data files there and rerun the "
                 f"program.\n{80*'-'}"
                 )
    data_ext = []
    for e in data_files:
        if e.suffix not in data_ext:
            data_ext.append(e.suffix)
    if len(data_ext) > 1:
        sys.exit(f"{80*'-'}\n{len(data_ext)} different file extensions "
                 f"{data_ext} were found in the '{data_path.name}' folder."
                 f"\nPlease ensure that only one file extension is present in "
                 f"the '{data_path.name}' folder and\nrerun the program."
                 f"\n{80*'-'}"
                 )
    x = np.loadtxt(data_files[0])[:, 0]
    xmin, xmax = np.amin(x), np.amax(x)
    print(f"{80*'-'}\nMinimum x-value in data: {xmin}"
          f"\nMaximum x-value in data: {xmax}\n{80*'-'}"
          )
    xmin = float(input(f"Please provide the minimum x-value to plot: "))
    xmax = float(input(f"Please provide the maximum x-value to plot: "))
    xmin_index, xmax_index = 0, -1
    for i in range(len(x)):
        if xmin <= x[i]:
            xmin_index = i
            break
    for i in range(len(x)):
        if xmax <= x[i]:
            xmax_index = i
            break
    bkg_files = list(bkg_path.glob("*.*"))
    if len(bkg_files) == 0:
        sys.exit(f"{80*'-'}\nNo background file was found in the "
                 f"'{bkg_path.name}' folder.\nPlease put the background file "
                 f"in the '{bkg_path.name}' folder and rerun the program."
                 f"\n{80*'-'}"
                 )
    if len(bkg_files) > 1:
        sys.exit(f"{80*'-'}\nMore than one file was found in the "
                 f"'{bkg_path.name}' folder.\nPlease ensure that only one file "
                 f"is present in the '{bkg_path.name}' folder and rerun the\n"
                 f"program.\n{80*'-'}"
                 )
    bkg_file = bkg_files[0]
    d = {}
    print(f"{80*'-'}\nLoading data and background...")
    for i, e in enumerate(data_files):
        d[i] = xy_to_dict(e)
    d_bkg = xy_to_dict(bkg_file)
    print(f"Done.\n{80*'-'}\nObtaining scale factor...")
    scales = []
    scans = list(d.keys())
    oom = 10**-3
    for scan in scans:
        scales.append(xy_scale(d[scan]["y"], d_bkg["y"], oom))
    scale = np.amin(np.array(scales))
    scale_str = f"{scale:.3f}"
    print(f"Done.\nMaximum scale factor value for no negative intensities: "
          f"{scale_str}"
          )
    scale_path = Path.cwd() / "scale.txt"
    with scale_path.open(mode="w", encoding="utf-8") as f:
        f.write(scale_str)
    print(f"Scale factor written to {scale_path.name} file.\n{80*'-'}\nWriting "
          f"background-subtracted files..."
          )
    data_bkg_sub_path = Path.cwd() / "data_bkg-sub"
    if not data_bkg_sub_path.exists():
        data_bkg_sub_path.mkdir()
    for scan in scans:
        d[scan]["y_bkg_sub"] = d[scan]["y"] - (scale * d_bkg["y"])
        np.savetxt(data_bkg_sub_path / data_files[scan].name,
                   np.column_stack((d[scan]["x"], d[scan]["y_bkg_sub"])),
                   delimiter="\t",
                   fmt="%.8f\t%.1f",
                   encoding="utf-8",
                   )
    raw_path = Path.cwd() / "raw"
    if not raw_path.exists():
        raw_path.mkdir()
        sys.exit(f"Done.\nPlease see the '{data_bkg_sub_path}' folder."
                 f"\n{80*'-'}\nA folder called '{raw_path.name}' has been "
                 f"created.\nPlease place your .raw file(s) there and rerun "
                 f"the program.\n{80*'-'}"
                 )    
    raw_files = list(raw_path.glob("*.*"))
    if len(raw_files) == 0:
        sys.exit(f"{80*'-'}\nNo files were found in the '{raw_path.name}' "
                 f"folder.\nPlease place your .raw file(s) there and rerun the "
                 f"program.\n{80*'-'}"
                 )
    timestamps, mtimes, durations = [], [], []
    for i, raw in enumerate(raw_files):
        if i == 0:
            exp_time = get_exposure_time(raw)
            print(f"{80*'-'}\nExposure time:\t\t\t{exp_time} s")
        timestamp, mtime = get_times(raw)
        timestamps.append(timestamp)
        mtimes.append(mtime)
        durations.append(mtimes[-1] - timestamps[-1])
        print(f"{80*'-'}\nDuration of experiment {i+1}:"
              f"\t{durations[-1] / 60**2:.2f} h"
              f"\n\t\t\t\t{durations[-1] / (60**2 * 24):.2f} days"
              )
        if i == 0:
            start = timestamps[-1]
        elif i == len(raw_files) - 1:
            end = mtimes[-1]
    duration = end - start
    print(f"{80*'-'}\nTotal duration:\t\t\t{duration / 60**2:.2f} h"
          f"\n\t\t\t\t{duration / (60**2 * 24):.2f} days"
          )
    for i in range(1, len(durations)):
        deadtime = timestamps[i] - mtimes[i-1]
        n_dummies = int(deadtime / exp_time)
        print(f"{80*'-'}\nDeadtime between exp. {i} and {i+1}:"
            f"\t{deadtime / 60**2:.2f} h"
            f"\n\t\t\t\t{deadtime / (60**2 * 24):.2f} days"
            f"\nNumber of empty scans:\t\t{n_dummies} scans"
            )
    dummy_template = data_files[0]
    data_dummy_path = Path.cwd() / "data_dummy"
    if not data_dummy_path.exists():
        data_dummy_path.mkdir()
    print(f"{80*'-'}\nDummy scan template: {dummy_template.name}"
          f"\nWriting dummy scans to the '{data_dummy_path.name}' folder...."
          )
    x = np.loadtxt(dummy_template)[:, 0]
    y = np.zeros_like(x) - 1
    for i in range(1, len(durations)):
        for j in range(n_dummies):
            fname = dummy_template.stem.split(".")
            fname = f"{fname[0]}_{i}.1{str(j).zfill(3)}"
            fname += f"{dummy_template.suffix}"
            output_path = data_dummy_path / fname
            np.savetxt(output_path,
                       np.column_stack((x, y)),
                       delimiter="\t",
                       fmt="%.8f\t%i",
                       encoding="utf-8",
                       )
    data_all_path = Path.cwd() / "data_all"
    data_bkg_sub_files = list(data_bkg_sub_path.glob("*.*"))
    data_dummy_files = list(data_dummy_path.glob("*.*"))
    if not data_all_path.exists():
        data_all_path.mkdir()
    print(f"Done.\n{80*'-'}\nCopying background-subtracted and dummy files to "
          f"the '{data_all_path.name}' folder..."
          )
    for f in data_bkg_sub_files:
        (data_all_path / f.name).write_text(f.read_text())
    for f in data_dummy_files:
        (data_all_path / f.name).write_text(f.read_text())
    print(f"Done.\n{80*'-'}\nCreating matrix and writing to .npy and .csv "
          f"files..."
          )
    data_all_files = list(data_all_path.glob("*.*"))
    d = {}
    for i, e in enumerate(data_all_files):
        d[i] = xy_to_dict(e)          
    array = dict_to_array(d)
    basename = data_all_files[0].stem.split(".")[0]
    npy_path = Path.cwd() / "npy"
    if not npy_path.exists():
        npy_path.mkdir()
    np.save(npy_path / basename, array)
    csv_path = Path.cwd() / "csv"
    if not csv_path.exists():
        csv_path.mkdir()
    cols = ["x"]
    for e in range(len(data_all_files)):
        cols.append(str(e))
    df = pd.DataFrame(array, columns=cols)
    df.to_csv(csv_path / f"{basename}.csv")
    print(f"Done writing files.\nPlease see the "
          f"'{npy_path.name}' and '{csv_path.name}' folders.\n{80*'-'}"
          f"\nPlotting..."
          )
    png_path, pdf_path = Path.cwd() / "png", Path.cwd() / "pdf"
    svg_path = Path.cwd() / "svg"
    plot_paths = [png_path, pdf_path, svg_path]
    plot_folders = [p.name for p in plot_paths]
    for p in plot_paths:
        if not p.exists():
            p.mkdir()
    plot(array[xmin_index:xmax_index+1, :], 
         duration / 60**2, 
         D_PLOT, 
         basename, 
         plot_paths,
         )
    print(f"Done plotting.\nPlease see the {plot_folders} folders.\n{80*'-'}\n"
          f"Program done."
          )

    return None


if __name__ == "__main__":
    main()

# End of file
