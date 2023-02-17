from pathlib import Path
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog


D_PLOT = dict(dpi = 600,
              figsize = (12, 4),
              fontsize_labels = 20,
              fontsize_ticks = 14,
              lw = 1,
              xlabel_tt = "$2\theta\;[\degree]$",
              xlabel_q = "$Q\;[\mathrm{\AA}^{-1}]$",
              ylabel = "$I\;[\mathrm{arb.\;u.}]$",
              yoffset = 0.05,
             )


def plot(file, d, output_paths):
    data = np.loadtxt(file)
    x, y = data[:, 0], data[:, 1]
    fig, ax = plt.subplots(dpi=d["dpi"], figsize=d["figsize"])
    ax.plot(x, y, lw=d["lw"])
    xmin, xmax = np.amin(x), np.amax(x)
    ymin, ymax = np.amin(y), np.amax(y)
    yrange = ymax - ymin
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin - d["yoffset"] * yrange, ymax + d["yoffset"] * yrange)
    ax.set_xlabel(d["xlabel_q"], fontsize=d["fontsize_labels"])
    ax.set_ylabel(d["ylabel"], fontsize=d["fontsize_labels"])
    ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    ax.minorticks_on()
    for p in output_paths:
        print(f"\t\t{p.name}")
        plt.savefig(p / f"{file.stem}.{p.name}", bbox_inches="tight")
    plt.close()
             
    return None 


def main():
    print(f"{Path(__file__).name}\n{80*'-'}\nRunning pyFAI calibration gui...")
    subprocess.run("pyFAI-calib2")
    print(f"{80*'-'}\nRunning pyFAI integration gui...")
    subprocess.run("pyFAI-integrate")
    print(f"{80*'-'}\nFiles to plot...")
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.iconify()
    files = filedialog.askopenfilenames(parent=root, 
                                        title="Choose files to plot.",
                                        )
    root.destroy()
    file_paths = [Path(f) for f in files]
    for p in file_paths:
        print(f"\t{p.name}")
    file_ext = file_paths[0].suffix
    parent_path = file_paths[0].parent
    parent_parent_path = parent_path.parent
    nan_present = False
    nans = ["NAN", "NaN", "Nan", "nan"]
    with file_paths[0].open(mode="r") as f:
        s = f.read()
    for nan in nans:
        if nan in s:
            nan_present = True
            nan_type = nan
            break
    if nan_present is True:
        nan_path = parent_path / f"{file_ext[1:]}_nan_to_zero"
        if not nan_path.exists():
            nan_path.mkdir()
        for file in file_paths:
            with file.open(mode="r") as f:
                s = f.read().replace(nan_type, "0")
            output_path = nan_path / file.name
            with output_path.open(mode="w") as o:
                o.write(s)
        file_paths = list(nan_path.glob(f"*{file_ext}"))
    png_path, pdf_path = parent_parent_path / "png", parent_parent_path / "pdf" 
    svg_path = parent_parent_path / "svg"
    plot_paths = [png_path, pdf_path, svg_path]
    plot_folders = [p.name for p in plot_paths]
    for p in plot_paths:
        if not p.exists():
            p.mkdir()
    print(f"{80*'-'}\nPlotting files...")
    for file in file_paths:
        print(f"\t{file.name}")
        plot(file, D_PLOT, plot_paths)
    print(f"Done. Please see the {plot_folders} folders.")

    return None


if __name__ == "__main__":
    main()

# End of file
