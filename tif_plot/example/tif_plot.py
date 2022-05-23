import sys
from pathlib import Path
import matplotlib.pyplot as plt
import fabio


DPI = 600
# FIGSIZE = (6,4)
CMAP = "viridis"


def tif_plot(tif_files, output_folders):
    for f in tif_files:
        tif = fabio.open(f).data
        fig, ax = plt.subplots(dpi=DPI)#, figsize=FIGSIZE)
        im = ax.imshow(tif, cmap=CMAP, aspect="equal")
        ax.tick_params(axis="x",
                        top=True,
                        bottom=False,
                        labeltop=True,
                        labelbottom=False)
        ax.tick_params(axis="y",
                        left=True,
                        right=False,
                        labelleft=True,
                        labelright=False)
        cbar = fig.colorbar(im, ax=ax)
        cbar.formatter.set_powerlimits((0,0))
        for e in output_folders:
            plt.savefig(f"{e}/{f.stem}.{e}", bbox_inches="tight")
        plt.close()

    return None


def main():
    tif_path = Path.cwd() / "tif"
    if not tif_path.exists():
        tif_path.mkdir()
        print(f"{80*'-'}\nA folder called '{tif_path.name}' has been created.\n"
              f"Please place your .tif files there and rerun the program."
              f"\n{80*'-'}")
        sys.exit()
    tif_files = list(tif_path.glob("*.tif"))
    if len(tif_files) == 0:
        print(f"{80*'-'}\nNo .tif files were found in the '{tif_path.name}' "
              f"folder.\nPlease place your .{tif_path.name} files there and "
              f"rerun the program.\n{80*'-'}")
        sys.exit()
    output_folders = ["png",
                      # "pdf",
                      # "svg",
                      ]
    for e in output_folders:
        if not (Path.cwd() / e).exists():
            (Path.cwd() / e).mkdir()
    print(f"{80*'-'}\nPlotting .tif files...")
    tif_plot(tif_files, output_folders)
    print(f"{80*'-'}\nDone plotting.\n{80*'-'}\nPlease see the "
          f"{output_folders} folder(s).\n{80*'-'}")


    return None


if __name__ == "__main__":
    main()

# End of file.
