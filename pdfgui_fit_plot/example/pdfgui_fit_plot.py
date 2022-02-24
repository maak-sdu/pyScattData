import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from diffpy.utils.parsers.loaddata import loadData

DPI = 300
FIGSIZE = (8,4)

SIZE_SCATTER = 10
LINEWIDTH_SCATTER = 0.5
LINEWIDTH_PLOT = 1
LINEWIDTH_LEGEND = 2

FONTSIZE_LABELS = 16
FONTSIZE_LEGEND = 12
FONTSIZE_RW = FONTSIZE_LEGEND

G_OFFSET = 1.1


def pdfgui_fit_plot(fgr_files, gr_files, res_files):
    for i in range(len(fgr_files)):
        print(f"\t{fgr_files[i].stem}")
        with gr_files[i].open(mode="r", encoding="utf-8") as f:
            gr_data = loadData(f.name)
        r_gr, g_gr = gr_data[:,0], gr_data[:,1]
        with fgr_files[i].open(mode="r", encoding="utf-8") as f:
            fgr_data = loadData(f.name)
        with res_files[i].open(mode="r", encoding="utf-8") as f:
            res_data = f.readlines()
        for j in range(len(res_data)):
            if "Rw - value" in res_data[j]:
                rw_index = j
        rw = f"{float(res_data[rw_index].split()[-1].strip()):.2f}"
        RW = r"$R_{\mathrm{w}}=$"
        rw = fr"{RW}${rw}$"
        r_fgr, g_fgr, gdiff_fgr = fgr_data[:,0], fgr_data[:,1], fgr_data[:,4]
        g_min, gdiff_max = np.amin(g_fgr), np.amax(gdiff_fgr)
        g_offset = G_OFFSET * (abs(g_min) + abs(gdiff_max))
        gdiff_offset = gdiff_fgr - g_offset
        r_min, r_max = np.amin(r_fgr), np.amax(r_fgr)
        bg_blue, bg_red, bg_green = '#0B3C5D', '#B82601', '#1c6b0a'
        fig, ax = plt.subplots(dpi=DPI, figsize=FIGSIZE)
        plt.scatter(r_gr, g_gr, s=SIZE_SCATTER, lw=LINEWIDTH_SCATTER,
                    edgecolors=bg_blue, facecolors="none",
                    label=r"$G_{\mathrm{exp}}$")
        plt.plot(r_fgr, g_fgr, c=bg_red, lw=LINEWIDTH_PLOT,
                 label=r"$G_{\mathrm{calc}}$")
        plt.plot(r_fgr, gdiff_offset, c=bg_green, lw=LINEWIDTH_PLOT,
                 label=r"$G_{\mathrm{diff}}$")
        plt.xlim(r_min, r_max)
        plt.xlabel(r"$r$ $[\mathrm{\AA}]$", fontsize=FONTSIZE_LABELS)
        plt.ylabel(r"$G$ $[\mathrm{\AA}^{-2}]$", fontsize=FONTSIZE_LABELS)
        blue_marker = plt.scatter([], [], marker='o', facecolors='none',
                                  edgecolors=bg_blue)
        blue_marker.remove()
        red_line = Line2D([], [], color=bg_red, linewidth=LINEWIDTH_LEGEND)
        green_line = Line2D([], [], color=bg_green, linewidth=LINEWIDTH_LEGEND)
        props = dict(boxstyle='round', facecolor='white', alpha=0.0)
        legend = plt.legend(handles=[(blue_marker), (red_line), (green_line)],
                            labels=['$G_{\mathrm{exp}}$', '$G_{\mathrm{calc}}$',
                                    '$G_{\mathrm{diff}}$'],
                            ncol=3, prop={'size' : FONTSIZE_LEGEND},
                            bbox_to_anchor=(0.014, 1.04, 1.0, 0.102),
                            )
        ax.text(0.01, 1.075, rw, transform=ax.transAxes, fontsize=FONTSIZE_RW,
                verticalalignment='top', bbox=props)
        plt.savefig(f"png/{gr_files[i].stem}.png", bbox_inches="tight")
        plt.savefig(f"pdf/{gr_files[i].stem}.pdf", bbox_inches="tight")

    return None


def main():
    cwd = Path.cwd()
    fgr_path = cwd / "fgr"
    gr_path = cwd / "gr"
    res_path = cwd / "res"
    plotfolders = ["png", "pdf"]
    print(f"{80*'-'}\nFor plot setting, please see the top of this .py file.\n"
          f"{80*'-'}\nPlease be aware that your .fgr, .gr, and .res files "
          f"should share files names,\nexcept from the file extension, such "
          f"that they are paired in the right way in\nthe plots. "
          f"Alternatively, consider to prefix enumerate the files like:\n"
          f"\t00_fgr_file.fgr\n\t00_gr_file.gr\n\t00_res_file.res")
    if not fgr_path.exists() and not gr_path.exists() and not res_path.exists():
        fgr_path.mkdir()
        gr_path.mkdir()
        res_path.mkdir()
        print(f"{80*'-'}\nFolders called 'fgr', 'gr', and 'res' have been "
              f"made. Please place you .fgr,\n.gr, and .res files there and "
              f"rerun the code.\n{80*'-'}")
        sys.exit()
    elif not fgr_path.exists():
        fgr_path.mkdir()
        print(f"{80*'-'}\nA folder called 'fgr' has been made. Please place "
              f"your .fgr there and rerun the\ncode.\n{80*'-'}")
        sys.exit()
    elif not gr_path.exists():
        gr_path.mkdir()
        print(f"{80*'-'}\nA folder called 'gr' has been made. Please place "
              f"your .gr there and rerun the\ncode.\n{80*'-'}")
        sys.exit()
    elif not res_path.exists():
        res_path.mkdir()
        print(f"{80*'-'}\nA folder called 'res' has been made. Please place "
              f"your .res there and rerun the\ncode.\n{80*'-'}")
        sys.exit()
    fgr_files = list(fgr_path.glob("*.fgr"))
    gr_files = list(gr_path.glob("*.gr"))
    res_files = list(res_path.glob("*.res"))
    if len(fgr_files) == 0 and len(gr_files) == 0 and len(res_files) == 0:
        print(f"{80*'-'}\nNo .fgr, .gr, and .res files found in the 'fgr', "
              f"'gr', and 'res' folders. Please\nplace you .fgr, .gr, and .res "
              f"files there and rerun the code.\n{80*'-'}")
        sys.exit()
    elif len(fgr_files) == 0:
        print(f"{80*'-'}\nNo .fgr files found in the 'fgr' folder. Please "
              f"place your .gr files there and\nrerun the code.\n{80*'-'}")
        sys.exit()
    elif len(gr_files) == 0:
        print(f"{80*'-'}\nNo .gr files found in the 'gr' folder. Please place "
              f"your .gr files there and rerun the code.\n{80*'-'}")
    elif len(res_files) == 0:
        print(f"{80*'-'}\nNo .res files found in the 'res' folder. Please "
              f"place your .res files there and\nrerun the code.\n{80*'-'}")
        sys.exit()
    for plotfolder in plotfolders:
        if not (cwd / plotfolder).exists():
            (cwd / plotfolder).mkdir()
    print(f"{80*'-'}\nPlotting files...")
    pdfgui_fit_plot(fgr_files, gr_files, res_files)
    print(f"Done plotting files.\n{80*'-'}\nPlease see the 'png' and 'pdf' "
          f"folders.\n{80*'-'}")

    return None


if __name__ == "__main__":
    main()

# End of file.
