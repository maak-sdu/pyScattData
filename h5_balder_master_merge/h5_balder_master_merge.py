import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import h5py
import hdf5plugin

DATA_TO_MERGE = ["data_000005",
                 "data_000006",
                 "data_000007",
                 "data_000008",
                 ]

D_PLOT= dict(dpi=600,
             figsize=(8,6),
             fontsize_labels=20,
             fontsize_ticks=14,
             xlabel="$x$",
             ylabel="$y$",
             cbarlabel="counts",
             scale=5,
             )


def h5_master_to_dict(h5_master):
    f = h5py.File(h5_master, "r")
    data_keys = list(f["entry"]["data"].keys())
    d = {}
    for k in data_keys:
        d[k] = np.array(f["entry"]["data"][k])
        
    return d


def plot(name, data, d_plot, output_paths):
    fig, ax = plt.subplots(dpi=d_plot["dpi"], figsize=d_plot["figsize"])
    im = ax.imshow(data, vmin=0, vmax=np.median(data) * d_plot["scale"])
    ax.set_xlabel(d_plot["xlabel"], fontsize=d_plot["fontsize_labels"])
    ax.set_ylabel(d_plot["ylabel"], fontsize=d_plot["fontsize_labels"])
    cbar = fig.colorbar(im)
    cbar.set_label(d_plot["cbarlabel"])
    cbar.formatter.set_powerlimits((0, 0))
    for p in output_paths:
        print(f"\t\t{name}.{p.name}")
        plt.savefig(p / f"{name}.{p.name}", bbox_inches="tight")
    plt.close()

    return None


def main():
    print(Path(__file__).name)
    h5_path = Path.cwd() / "h5"
    if not h5_path.exists():
        h5_path.mkdir()
        sys.exit(f"{80*'-'}\nA folder called '{h5_path.name}' has been created."
                 f"\nPlease place your .h5 file(s) there and rerun the code.")
    h5_files = list(h5_path.glob("*.h5"))
    if len(h5_files) == 0:
        sys.exit(f"{80*'-'}\nNo .h5 files were found in the '{h5_path.name}' "
                 f"folder.\nPlease place your .h5 file(s) there and rerun the "
                 f"code.")
    h5_master = None
    for f in h5_files:
        if "master" in f.name:
            h5_master = f
            print(f"{80*'-'}\n{h5_master.name}")
    if isinstance(h5_master, type(None)):
        sys.exit(f"{80*'-'}\nNo .h5 master file was found.\nPlease place your "
                 f".h5 master file there and rerun the code.")
    d = h5_master_to_dict(h5_master)
    npy_path = Path.cwd() / "npy"
    if not npy_path.exists():
        npy_path.mkdir()
    png_path, pdf_path = Path.cwd() / "png", Path.cwd() / "pdf"
    svg_path = Path.cwd() / "svg"
    plot_paths = [png_path, pdf_path, svg_path]
    for p in plot_paths:
        if not p.exists():
            p.mkdir()    
    # print(f"{80*'-'}\nPlotting files to merge...")
    # for k in list(d.keys()):
    #     if k in DATA_TO_MERGE:
    #         print(f"\t{k}")
    #         plot(f"{k}_sum", np.sum(d[k], axis=0), D_PLOT, plot_paths)
    #         plot(f"{k}_avg", np.mean(d[k], axis=0), D_PLOT, plot_paths)
    data_stack = d[DATA_TO_MERGE[0]]
    for i in range(1, len(DATA_TO_MERGE)):
        data_stack = np.concatenate((data_stack, d[DATA_TO_MERGE[i]]), axis=0)
    data_stack_sum = np.sum(data_stack, axis=0)
    data_stack_avg = np.mean(data_stack, axis=0)
    print(f"{80*'-'}\nPlotting merged data...\n\tmerged")
    plot(f"merged_sum", data_stack_sum, D_PLOT, plot_paths)
    plot(f"merged_avg", data_stack_avg, D_PLOT, plot_paths)
    plot_folders = [p.name for p in plot_paths]
    print(f"Done. Please see the {plot_folders} folders."
          f"\n{80*'-'}\nSaving .npy files...\n\tmerged_sum")
    np.save(npy_path / "merged_sum", data_stack_sum)
    print(f"\tmerged_avg")
    np.save(npy_path / "merged_avg", data_stack_avg)
    print(f"Done. Please see the '{npy_path.name}' folder.")
    return None


if __name__ == "__main__":
    main()

# End of file
