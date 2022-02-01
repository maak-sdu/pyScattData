import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from diffpy.utils.parsers.loaddata import loadData

DPI = 300
FIGSIZE = (8,4)
FONTSIZE = 12
LINEWIDTH = 1
COLORS = dict(bg_blue='#0B3C5D', bg_red='#B82601', bg_green='#1c6b0a',
              bg_lightblue='#328CC1', bg_darkblue='#062F4F', bg_yellow='#D9B310',
              bg_darkred='#984B43', bg_bordeaux='#76323F', bg_olivegreen='#626E60',
              bg_yellowgrey='#AB987A', bg_brownorange='#C09F80')


def iq_sq_fq_gr_plotter(datafiles):
    d = {}
    for f in datafiles:
        xy = loadData(f)
        d[str(f.suffix).split('.')[-1]] = xy
    fig, axs = plt.subplots(dpi=DPI, nrows=2, ncols=2, figsize=FIGSIZE)
    axs[0,0].plot(d['iq'][:,0], d['iq'][:,1], lw=LINEWIDTH, c=COLORS['bg_lightblue'])
    axs[0,0].set_xlabel(r'$Q$ $[\mathrm{\AA}^{-1}]$')
    axs[0,0].set_ylabel(r'$I$ $[\mathrm{a.u.}]$')
    axs[0,0].ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    axs[0,0].set_xlim(min(d['iq'][:,0]), max(d['iq'][:,0]))
    axs[0,1].plot(d['sq'][:,0], d['sq'][:,1], lw=LINEWIDTH, c=COLORS['bg_blue'])
    axs[0,1].set_xlabel(r'$Q$ $[\mathrm{\AA}^{-1}]$')
    axs[0,1].set_ylabel(r'$S$ $[\mathrm{a.u.}]$')
    axs[0,1].set_xlim(min(d['sq'][:,0]), max(d['sq'][:,0]))
    axs[1,1].plot(d['fq'][:,0], d['fq'][:,1], lw=LINEWIDTH, c=COLORS['bg_green'])
    axs[1,1].set_xlabel(r'$Q$ $[\mathrm{\AA}^{-1}]$')
    axs[1,1].set_ylabel(r'$F$ $[\mathrm{\AA}^{-1}]$')
    axs[1,1].set_xlim(min(d['fq'][:,0]), max(d['fq'][:,0]))
    axs[1,0].plot(d['gr'][:,0], d['gr'][:,1], lw=LINEWIDTH, c=COLORS['bg_red'])
    axs[1,0].set_xlabel(r'$r$ $[\mathrm{\AA}]$')
    axs[1,0].set_ylabel(r'$G$ $[\mathrm{\AA}^{-2}]$')
    axs[1,0].set_xlim(min(d['gr'][:,0]), max(d['gr'][:,0]))
    plt.figtext(0.485, 0.725, r'$\rightarrow$', fontsize=20)
    plt.figtext(0.75, 0.46, r'$\downarrow$', fontsize=20)
    plt.figtext(0.485, 0.285, r'$\leftarrow$', fontsize=20)
    fig.tight_layout(pad=2)
    plt.savefig(f"png/iq_fq_sq_gr.png", bbox_inches='tight')
    plt.savefig(f"pdf/iq_fq_sq_gr.pdf", bbox_inches='tight')
    plt.close()

    return None


def main():
    data_path = Path.cwd() / "data"
    if not data_path.exists():
        data_path.mkdir()
        print(f"{80*'-'}\nA folder called 'data' has been created.\
                \nPlease place your .iq, .sq, .fq, and .gr files there and rerun the code.\
                \n{80*'-'}")
        sys.exit()
    datafiles = list((Path.cwd() / 'data').glob('*.*'))
    filename = datafiles[0].stem
    dataexts = [e.suffix for e in datafiles]
    filexts = [".iq", ".fq", ".sq", ".gr"]
    missing_exts = []
    for e in filexts:
        if e not in dataexts:
            missing_exts.append(e)
    if len(missing_exts) != 0:
        print(f"{80*'-'}\nNo {missing_exts} files were found in the 'data' folder.\
                \nPlease place them there and rerun the code.\
                \n{80*'-'}")
        sys.exit()
    folders = ['png', 'pdf']
    for folder in folders:
        if not (Path.cwd() / folder).exists():
            (Path.cwd() / folder).mkdir()
    print(f"{80*'-'}\nPlotting...")
    iq_sq_fq_gr_plotter(datafiles)
    print(f"Done plotting.\n{80*'-'}\
            \nPlease see the 'pdf' and 'png' folders.")

    return None


if __name__ == "__main__":
    main()

# End of file.
