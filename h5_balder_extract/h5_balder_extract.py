import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from bg_mpl_stylesheet.bg_mpl_stylesheet import bg_mpl_style
import hdf5plugin
import h5py
import fabio


def h5_extract(h5):
    f = h5py.File(h5)
    d = {}
    for k in f["entry"]["data"].keys():
        data = np.array(f["entry"]["data"][k])
        if data.shape[0] > 1:
            dim = "3dsumto2d"
        else:
            dim = "2d"
        d[f"{h5.stem}_{k}_{dim}"] = np.sum(data, axis=0)
        data = d[f"{h5.stem}_{k}_{dim}"]

    return d


def plot(npy, output_path):
    plt.style.use(bg_mpl_style)
    fig, ax = plt.subplots(dpi=600,
                           figsize=(8,6),
                           )
    im = ax.imshow(npy,
                   vmin=0,
                   vmax=np.median(npy) * 3,
                   )
    cb = fig.colorbar(im)
    cb.formatter.set_powerlimits((0, 0))
    cb.ax.yaxis.set_offset_position("left")
    cb.update_ticks()
    ax.minorticks_on()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()

    return None


def main():
    h5_path, tif_path = Path.cwd() / "h5", Path.cwd() / "tif"
    npy_path, png_path = Path.cwd() / "npy", Path.cwd() / "png"
    if not h5_path.exists():
        h5_path.mkdir()
        sys.exit(f"{80*'-'}\nA folder called 'h5' has been created.\n"
                  f"Please place your .h5 files here and rerun the code.\n"
                  f"{80*'-'}")
    h5_files = list(h5_path.glob("*.h5"))
    h5_files_master = [h5 for h5 in h5_files if "master" in h5.name]
    if len(h5_files) == 0:
        sys.exit(f"{80*'-'}\nNo .h5 files were found in the 'h5' folder.\n"
                  f"Please place your .h5 files there and rerun the code.\n"
                  f"{80*'-'}")
    for p in [png_path, npy_path, tif_path]:
        if not p.exists():
            p.mkdir()
    output_folders = [npy_path.name, tif_path.name, png_path.name]
    print(f"{80*'-'}\nWorking with files...")
    for h5 in h5_files_master:
        print(f"\t{h5.name}\n\t\tExtracting data.")
        d = h5_extract(h5)
        print("\t\tDone extracting data.\n\n\t\tSaving to .npy, .tif, and .png "
              "files...")
        for k in d.keys():
            print(f"\t\t\t{k}")
            npy_file_path = npy_path / f"{k}.npy"
            np.save(npy_file_path, d[k])
            tif_file_path = tif_path / f"{npy_file_path.stem}.tif"
            fabio.open(npy_file_path).convert("tif").save(tif_file_path)
            png_file_path = png_path / f"{k}.png"
            plot(d[k], png_file_path)
        print(f"\t\tDone. Please see the {output_folders} folders.")
    print(f"{80*'-'}\nDone working with files.")

    return None


if __name__ == "__main__":
    main()

# End of file
