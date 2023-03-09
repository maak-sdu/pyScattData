import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt


D_PLOT = dict(dpi=600,
              figsize=(8, 6),
              fontsize_labels=20,
              fontsize_ticks=14,
              xlabel="$x\;[\mathrm{pixels}]$",
              ylabel="$y\;[\mathrm{pixels}]$",
              oom=-4
              )


def npy_plot(npy, d, output_paths):
    data = np.load(npy)
    fig, ax = plt.subplots(dpi=d["dpi"], figsize=d["figsize"])
    im = ax.imshow(data, vmin=0, vmax=np.amax(data)*10**d["oom"])
    # ax.set_xlabel(d["xlabel"], fontsize=d["fontsize_labels"])
    ax.set_title(d["xlabel"], fontsize=d["fontsize_labels"])
    ax.set_ylabel(d["ylabel"], fontsize=d["fontsize_labels"])
    ax.tick_params(axis="x",
                   which="both",
                   labelbottom=False,
                   labeltop=True,
                   bottom=False,
                   top=True,
                   )
    cb = fig.colorbar(im)
    cb.formatter.set_powerlimits((0, 0))
    ax.minorticks_on()
    for p in output_paths:
        print(f"\t\t{p.name}")
        plt.savefig(p / f"{npy.name}_oom={d['oom']}.{p.name}", bbox_inches="tight")
    plt.close()

    return None


def main():
    print(Path(__file__).name)
    npy_path = Path.cwd() / "npy"
    if not npy_path.exists():
        npy_path.mkdir()
        sys.exit(f"{80*'-'}\nA folder called '{npy_path.name}' has been created."
                 f"\nPlease put your .{npy_path.name} files there and rerun "
                 f"the program.")
    npy_files = list(npy_path.glob("*.npy"))
    if len(npy_files) == 0:
        sys.exit(f"{80*'-'}\nNo .{npy_path.name} files were found in the "
                 f"'{npy_path.name}' folder.\nPlease place your "
                 f".{npy_path.name} files there and rerun the program.")
    png_path, pdf_path = Path.cwd() / "png", Path.cwd() / "pdf"
    svg_path = Path.cwd() / "svg"
    output_paths = [png_path, pdf_path, svg_path]
    for p in output_paths:
        if not p.exists():
            p.mkdir()
    print(f"{80*'-'}\nPlotting...")
    for npy in npy_files:
        print(f"\t{npy.name}")
        npy_plot(npy, D_PLOT, output_paths)

    return None


if __name__ == "__main__":
    main()

# End of file
