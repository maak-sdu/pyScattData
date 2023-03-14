import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

D_PLOT = dict(dpi=600,
              figsize=(8, 6),
              cmap="viridis",
              aspect="auto",
              interpolation="antialiased",
              ymax_scale=1,
              )

def xy_to_dict(xy):
    d = {}
    data = np.loadtxt(xy)
    d["x"], d["y"] = data[:, 0], data[:, 1]

    return d


def xy_scale(y, y_bkg):
    scale = 1
    y_diff = y - (scale * y_bkg)
    if (y_diff >= 0).all():
        upscale = True
        downscale = False
    else:
        upscale = False
        downscale = True
    while upscale:
        scale += 0.01
        y_diff = y - (scale * y_bkg)
        if (y_diff >= 0).all():
            upscale = True
        else:
            upscale = False
            scale -= 0.01
    while downscale:
        scale -= 0.01
        y_diff = y - (scale * y_bkg)
        if (y_diff < 0).any():
            downscale = True
        else:
            downscale = False

    return scale


def dict_to_array(d):
    keys = list(d.keys())
    for i, k in enumerate(keys):
        if i == 0:
            array = np.column_stack((d[k]["x"], d[k]["y"]))
        else:
            array = np.column_stack((array, d[k]["y"]))

    return array


def plot(array, basename, output_paths):
    x, y = array[:, 0], array[:, 1:]
    fig, ax = plt.subplots(dpi=600, figsize=(12, 5))
    im = ax.imshow(y,
                   cmap="viridis",
                   interpolation="antialiased",
                   aspect="auto",
                   origin="upper",
                   vmin=0,
                   vmax=np.amax(y) / 2.5,
                   extent=(0, y.shape[1], np.amax(x), np.amin(x)),
                   )
    ax.tick_params(axis="x",
                   which="major",
                   bottom=True,
                   labelbottom=False,
                   top=True,
                   labeltop=True,
                   direction="in",
                   labelsize=14,
                   width=1.5,
                   )
    ax.tick_params(axis="x",
                   which="minor",
                   bottom=True,
                   labelbottom=False,
                   top=True,
                   labeltop=True,
                   direction="in",
                   width=0.75,
                   )
    ax.tick_params(axis="y",
                   which="major",
                   right=True,
                   labelright=False,
                   left=True,
                   labelleft=True,
                   direction="in",
                   labelsize=14,
                   width=1.5,
                   )
    ax.tick_params(axis="y",
                   which="minor",
                   right=True,
                   labelright=False,
                   left=True,
                   labelleft=True,
                   direction="in",
                   width=0.75,
                   )    
    ax.minorticks_on()
    ax.set_xlabel("Scan number",
                  fontsize=20,
                  labelpad=10,
                  )
    ax.xaxis.set_label_position("top")
    ax.set_ylabel("$Q\;[\mathrm{\AA}^{-1}]$",
                  fontsize=20,
                  labelpad=10,)
    cbar = plt.colorbar(im)
    cbar.set_label("$I\;[\mathrm{counts}]$",
                   fontsize=20,
                   labelpad=10,
                   )
    cbar.formatter.set_powerlimits((0, 0))
    # plt.show()
    for p in output_paths:
        print(f"\t{p.name}")
        plt.savefig(p / f"{basename}.{p.name}", bbox_inches="tight")
    plt.close()

    return None


def main():
    print(Path(__file__).name)
    data_path = Path.cwd() / "data"
    if not data_path.exists():
        data_path.mkdir()
        sys.exit(f"{80*'-'}\nA folder called '{data_path.name}' has been "
                 f"created.\nPlease place your data files there and rerun the "
                 f"program.\n{80*'-'}")
    bkg_path = Path.cwd() / "bkg"
    if not bkg_path.exists():
        bkg_path.mkdir()
        sys.exit(f"{80*'-'}\nA folder called '{bkg_path.name}' has been "
                 f"created.\nPlease place your background file there and rerun "
                 f"the program.\n{80*'-'}")
    data_files = list(data_path.glob("*.*"))
    if len(data_files) == 0:
        sys.exit(f"{80*'-'}\nNo files were found in the '{data_path.name}' "
            f"folder.\nPlease place your data files there and rerun the "
            f"program.\n{80*'-'}")
    data_ext = []
    for e in data_files:
        if e.suffix not in data_ext:
            data_ext.append(e.suffix)
    if len(data_ext) > 1:
        sys.exit(f"{80*'-'}\n{len(data_ext)} different file extensions "
                 f"{data_ext} were found in the '{data_path.name}' folder."
                 f"\nPlease ensure that only one file extension is present in "
                 f"the '{data_path.name}' folder and\nrerun the program."
                 f"\n{80*'-'}")
    bkg_files = list(bkg_path.glob("*.*"))
    if len(bkg_files) == 0:
        sys.exit(f"{80*'-'}\nNo background file was found in the "
                 f"'{bkg_path.name}' folder.\nPlease put the background file "
                 f"in the '{bkg_path.name}' folder and rerun the program."
                 f"\n{80*'-'}")
    if len(bkg_files) > 1:
        sys.exit(f"{80*'-'}\nMore than one file was found in the "
                 f"'{bkg_path.name}' folder.\nPlease ensure that only one file "
                 f"is present in the '{bkg_path.name}' folder and rerun the\n"
                 f"program.\n{80*'-'}")
    bkg_file = bkg_files[0]
    d = {}
    print(f"{80*'-'}\nLoading data and background...")
    for i, e in enumerate(data_files):
        d[i] = xy_to_dict(e)
    d_bkg = xy_to_dict(bkg_file)
    print(f"Done loading data and background.\n{80*'-'}\nObtaining scale "
          f"factor...")
    scales = []
    scans = list(d.keys())
    for scan in scans:
        scales.append(xy_scale(d[scan]["y"], d_bkg["y"]))
    scale = np.amin(np.array(scales))
    scale_str = f"{scale:.2f}"
    print(f"Maximum scale value for no negative intensities: {scale_str}")
    scale_path = Path.cwd() / "scale.txt"
    with scale_path.open(mode="w", encoding="utf-8") as f:
        f.write(scale_str)
    print(f"Scale written to {scale_path.name} file.\n{80*'-'}\nWriting "
          f"background-subtracted files, including .csv with all\n"
          f"background-subtracted data...")
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
    array = dict_to_array(d)
    basename = data_files[0].stem.split(".")[0]
    npy_path = Path.cwd() / "npy"
    if not npy_path.exists():
        npy_path.mkdir()
    np.save(npy_path / basename, array)
    csv_path = Path.cwd() / "csv"
    if not csv_path.exists():
        csv_path.mkdir()
    header = "x"
    for e in scans:
        header+= f", {e}"
    cols = ["x"]
    for e in scans:
        cols.append(str(e))
    df = pd.DataFrame(array, columns=cols)
    df.to_csv(csv_path / f"{basename}.csv")
    np.savetxt(csv_path / f"{basename}.csv",
               array,
               comments="",
               header = header,
               delimiter=",",
               fmt="%.8f" + len(scans) * ", %i",
               encoding="utf-8",
               )
    print(f"Done writing files.\n{80*'-'}\nPlease see the "
          f"'{data_bkg_sub_path.name}' and {csv_path.name}.\n{80*'-'}\n"
          f"Plotting...")
    png_path, pdf_path = Path.cwd() / "png", Path.cwd() / "pdf"
    svg_path = Path.cwd() / "svg"
    plot_paths = [png_path, pdf_path, svg_path]
    plot_folders = [p.name for p in plot_paths]
    for p in plot_paths:
        if not p.exists():
            p.mkdir()
    array = np.load(npy_path / f"{basename}.npy")
    plot(array, basename, plot_paths)
    print(f"Done plotting.\nPlease see the {plot_folders} folders.\n{80*'-'}\n"
          f"Program done.")

    return None


if __name__ == "__main__":
    main()

# End of file
