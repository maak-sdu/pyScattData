import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cycler
# from bg_mpl_stylesheet.bg_mpl_stylesheet import bg_mpl_style

DPI = 600
FIGSIZE = (8,6)
XLABEL_COMPS = r"$r$ $[\mathrm{\AA}]$"
YLABEL_COMPS = r"$G$ $[\mathrm{\AA}^{-2}]$"
XLABEL_PHASERATIO = "Scan number"
YLABEL_PHASERATIO = "Weight"
XLABEL_RECON = "Number of components"
YLABEL_RECON = "RE"
XLABEL_ECHEM = r"$t$ $[\mathrm{h}]$"
YLABEL_ECHEM = r"$V$ $[\mathrm{V}]$"
COLORS = ['#0B3C5D', '#B82601', '#1c6b0a', '#328CC1',
          '#a8b6c1', '#D9B310', '#984B43', '#76323F',
          '#626E60', '#AB987A', '#C09F80', '#b0b0b0ff']

DISCHARGE_CHANGE = 5.75
DISCHARGE_END = 11.82444444
CHARGE_CHANGE = 15.25
CHARGE_END = 19.84888889
VLINES_NMF = [12, 23.5, 30, 38.75]
VLINES_ECHEM = [DISCHARGE_CHANGE, DISCHARGE_END, CHARGE_CHANGE, CHARGE_END]

bg_mpl_style = {
    ####################
    # lines properties #
    ####################
    'lines.linewidth':       2.50,
    'lines.markeredgewidth': 0.25,
    'lines.markersize':      6.00,
    'lines.solid_capstyle': 'round',

    ###################
    # font properties #
    ###################
    'font.size': 15.0,
    'font.family': ['sans-serif'],
    'font.sans-serif': ['DejaVu Sans',
                        'Bitstream Vera Sans',
                        'Computer Modern Sans Serif',
                        'Lucida Grande',
                        'Verdana',
                        'Geneva',
                        'Lucid',
                        'Arial',
                        'Helvetica',
                        'Avant Garde',
                        'sans-serif',
                        'cm'],

    ###################
    # axes properties #
    ###################
    'axes.titlesize': 14.0,

    'axes.labelsize': 16.0,
    'axes.labelcolor': 'k',

    'axes.linewidth':  2.5,
    'axes.edgecolor':  'k',

    'axes.prop_cycle': cycler('color',
                              ['#0B3C5D', '#B82601', '#1c6b0a', '#328CC1',
                               '#a8b6c1', '#D9B310', '#984B43', '#76323F',
                               '#626E60', '#AB987A', '#C09F80', '#b0b0b0ff']),

    ####################
    # xtick properties #
    ####################
    'xtick.top': True,
    'xtick.direction': 'in',
    'xtick.color': 'k',
    'xtick.labelsize':   15.0,
    'xtick.minor.width':  0.5,
    'xtick.major.width':  1.7,
    'xtick.major.pad':    5.0,

    ####################
    # ytick properties #
    ####################
    'ytick.right': True,
    'ytick.direction': 'in',
    'ytick.color': 'k',
    'ytick.labelsize':   15.0,
    'ytick.minor.width':  0.5,
    'ytick.major.width':  1.7,
    'ytick.major.pad':    5.0,

    ###################
    # grid properties #
    ###################
    'grid.color': '#b2b2b2',
    'grid.linestyle': '--',
    'grid.linewidth': 1.0,

    #####################
    # figure properties #
    #####################
    'figure.facecolor': 'w',

    'savefig.bbox': 'tight'
}

def comp_extracter(compfile):
    df = pd.read_csv(compfile)
    xcomps = [df[col].to_numpy() for col in df.columns if "Unnamed" in col][0]
    compnames = np.array([int(col)+1 for col in df.columns if not "Unnamed" in col])
    comps = [df[f"{col-1}"].to_numpy() for col in compnames]

    return xcomps, compnames, comps


def phase_extracter(phasefile):
    df = pd.read_csv(phasefile)
    rows = df.to_numpy()
    scans = np.array([int(col)+1 for col in df.columns if not "Unnamed" in col])
    phasenames = np.array([int(rows[i][0])+1 for i in range(rows.shape[0])])
    phaseratios = np.array([rows[i][1:] for i in range(rows.shape[0])])

    return scans, phasenames, phaseratios


def recon_extracter(reconfile):
    df = pd.read_csv(reconfile)
    xrecon, recon = df.to_numpy()[:,0], df.to_numpy()[:,1]

    return xrecon, recon


def comp_plotter(xcomps, compnames, comps):
    max_comps = np.array([np.amax(comp) for comp in comps])
    max_comps_sum = [np.sum(max_comps[0:i]) for i in range(len(max_comps))]
    comps_offset = comps[0]
    for i in range(1, len(max_comps)):
        comps_offset = np.vstack((comps_offset, comps[i] + max_comps_sum[i] + 0.05*max_comps_sum[-1]))
    compfig = plt.figure(dpi=DPI, figsize=FIGSIZE)
    # compfig = plt.figure()
    plt.style.use(bg_mpl_style)
    for i in range(len(compnames)):
        plt.plot(xcomps, comps_offset[i], label=compnames[i])
    plt.legend(loc="upper right")
    # plt.xlim(np.amin(xcomps), np.amax(xcomps))
    plt.xlabel(XLABEL_COMPS)#, fontsize=FONTSIZE)
    plt.ylabel(YLABEL_COMPS)#, fontsize=FONTSIZE)
    # plt.show()
    plt.savefig("png/components.png", bbox_inches="tight")
    plt.savefig("pdf/components.pdf", bbox_inches="tight")
    plt.close()

    return None


def phase_plotter(scans, phasenames, phaseratios):
    phasefig = plt.figure(dpi=DPI, figsize=FIGSIZE)
    # phasefig = plt.figure()
    plt.style.use(bg_mpl_style)
    for i in range(len(phasenames)):
        plt.plot(scans, phaseratios[i], label=phasenames[i], marker="o")
    plt.xlabel(XLABEL_PHASERATIO)#, fontsize=FONTSIZE)
    plt.ylabel(YLABEL_PHASERATIO)#, fontsize=FONTSIZE)
    # plt.xlim(np.amin(scans), np.amax(scans))
    # plt.ylim(-0.025, 1+0.025)
    # plt.show()
    plt.savefig("png/phase_ratio.png", bbox_inches="tight")
    plt.savefig("pdf/phase_ratio.pdf", bbox_inches="tight")
    plt.close()

    return None


def recon_plotter(xrecon, recon):
    reconfig = plt.figure(dpi=DPI, figsize=FIGSIZE)
    # reconfig = plt.figure()
    plt.style.use(bg_mpl_style)
    plt.plot(xrecon, recon)
    plt.xlabel(XLABEL_RECON)
    plt.ylabel(YLABEL_RECON)
    plt.xticks(xrecon)
    # plt.show()
    plt.savefig("png/recon_error.png", bbox_inches="tight")
    plt.savefig("pdf/recon_error.pdf", bbox_inches="tight")
    plt.close()

    return None


def recon_comp_plotter(xcomps, compnames, comps, xrecon, recon):
    max_comps = np.array([np.amax(comp) for comp in comps])
    max_comps_sum = [np.sum(max_comps[0:i]) for i in range(len(max_comps))]
    comps_offset = comps[0]
    for i in range(1, len(max_comps)):
        comps_offset = np.vstack((comps_offset, comps[i] + max_comps_sum[i] + 0.05*max_comps_sum[-1]))
    fig, axs = plt.subplots(dpi=DPI, figsize=FIGSIZE, nrows=2, ncols=1)
    # fig, axs = plt.subplots(nrows=2, ncols=1)
    # print(plt.rcParams.keys())
    # sys.exit()
    axs[0].plot(xrecon, recon)
    axs[0].set_xlabel(XLABEL_RECON)
    axs[0].set_ylabel("Recon. error")
    axs[0].set_xticks(xrecon)
    axs[0].tick_params(axis="x", top="True", bottom="True", labeltop=True, labelbottom=False)
    axs[0].xaxis.set_label_position("top")
    for i in range(len(compnames)):
        axs[1].plot(xcomps, comps_offset[i], label=compnames[i])
    axs[1].legend(loc="upper right")
    # plt.xlim(np.amin(xcomps), np.amax(xcomps))
    axs[1].set_xlabel(XLABEL_COMPS)#, fontsize=FONTSIZE)
    axs[1].set_ylabel(YLABEL_COMPS)#, fontsize=FONTSIZE)
    # plt.show()
    plt.savefig("png/recon_comp.png", bbox_inches="tight")
    plt.savefig("pdf/recon_comp.pdf", bbox_inches="tight")
    plt.close()

    return None


def echem_collector(echemfile):
    data = np.loadtxt(echemfile)
    time, voltage = data[:,0], data[:,1]

    return time, voltage


def echem_plotter(time, voltage):
    echemfig = plt.figure(dpi=DPI, figsize=FIGSIZE)
    plt.style.use(bg_mpl_style)
    plt.plot(time, voltage)
    plt.xlabel(XLABEL_ECHEM)
    plt.ylabel(YLABEL_ECHEM)
    # plt.show()
    plt.savefig("png/echem.png", bbox_inches="tight")
    plt.savefig("pdf/echem.pdf", bbox_inches="tight")
    plt.close()

    return None


def phase_chem_plotter(scans, phasenames, phaseratios, time, voltage):
    fig, axs = plt.subplots(dpi=DPI, figsize=FIGSIZE, nrows=2, ncols=1,
                            gridspec_kw={'height_ratios': [2, 1]})
    # phasefig = plt.figure()
    plt.style.use(bg_mpl_style)
    for i in range(len(phasenames)):
        axs[0].plot(scans, phaseratios[i], label=phasenames[i], marker="o")
    axs[0].set_xlabel(XLABEL_PHASERATIO)#, fontsize=FONTSIZE)
    axs[0].set_ylabel(YLABEL_PHASERATIO)#, fontsize=FONTSIZE)
    axs[0].tick_params(axis="x", top="True", bottom="True", labeltop=True, labelbottom=False)
    axs[0].xaxis.set_label_position("top")
    fig.legend(phasenames, loc='upper center', ncol=len(phasenames), borderaxespad=-0.2,
               edgecolor='white')
    for vline in VLINES_NMF:
        axs[0].axvline(x=vline, ls="--", c="k", lw=2)
    axs[1].plot(time, voltage)
    axs[1].set_xlabel(XLABEL_ECHEM)#, fontsize=FONTSIZE)
    axs[1].set_ylabel(YLABEL_ECHEM)#, fontsize=FONTSIZE)
    for vline in VLINES_ECHEM:
        axs[1].axvline(x=vline, ls="--", c="k", lw=2)
    # plt.show()
    plt.subplots_adjust(hspace=0.1)
    plt.savefig("png/phaseratio_echem.png", bbox_inches="tight")
    plt.savefig("pdf/phaseratio_echem.pdf", bbox_inches="tight")
    plt.close()

    return None


def nmf_echem_plotter(xcomps, compnames, comps,
                      scans, phasenames, phaseratios,
                      xrecon, recon,
                      time, voltage):
    max_comps = np.array([np.amax(comp) for comp in comps])
    max_comps_sum = [np.sum(max_comps[0:i]) for i in range(len(max_comps))]
    comps_offset = comps[0]
    for i in range(1, len(max_comps)):
        comps_offset = np.vstack((comps_offset, comps[i] + max_comps_sum[i] + 0.05*max_comps_sum[-1]))
    fig, axs = plt.subplots(dpi=DPI, figsize=FIGSIZE, nrows=2, ncols=2,
                            gridspec_kw={'height_ratios': [2, 1],
                                         'wspace':0.35,
                                         'hspace':0.2,
                                         }
                            )
    plt.style.use(bg_mpl_style)
    axs[1,0].plot(xrecon, recon)
    axs[1,0].set_xlabel(XLABEL_RECON)
    axs[1,0].set_ylabel(YLABEL_RECON)
    axs[1,0].set_xticks(xrecon)
    axs[1,0].tick_params(axis="x", top="True", bottom="True", labeltop=False, labelbottom=True)
    axs[1,0].xaxis.set_label_position("bottom")
    # axs[1,0].text(min(xcomps), 0.9*max(recon), "(c)")
    for i in range(len(compnames)):
        axs[0,0].plot(xcomps, comps_offset[i], label=compnames[i])
    # axs[0,0].legend(loc="upper right")
    # plt.xlim(np.amin(xcomps), np.amax(xcomps))
    axs[0,0].set_xlabel(XLABEL_COMPS)#, fontsize=FONTSIZE)
    axs[0,0].set_ylabel(YLABEL_COMPS)#, fontsize=FONTSIZE)
    axs[0,0].tick_params(axis="x", top="True", bottom="True", labeltop=True, labelbottom=False)
    axs[0,0].xaxis.set_label_position("top")
    # axs[0,0].text(min(xcomps), 0.9*max(comps_offset[-1]), "(a)")
    for i in range(len(phasenames)):
        axs[0,1].plot(scans, phaseratios[i], label=phasenames[i], marker="o")
    axs[0,1].set_xlabel(XLABEL_PHASERATIO)#, fontsize=FONTSIZE)
    axs[0,1].set_ylabel(YLABEL_PHASERATIO)#, fontsize=FONTSIZE)
    axs[0,1].set_xticks([i*10 for i in range(1, (scans[-1] // 10)+1)])
    # axs[0,1].set_xticks([i*2 for i in range(1, (scans[-1] // 2)+1)], minor=True)
    axs[0,1].tick_params(axis="x", top="True", bottom="True", labeltop=True, labelbottom=False)
    # axs[0,1].tick_params(axis="x", which="minor", length=2, width=1.5)
    axs[0,1].xaxis.set_label_position("top")
    for vline in VLINES_NMF:
        axs[0,1].axvline(x=vline, ls="--", c="k", lw=2)
    # axs[0,1].legend(loc="upper right")
    axs[1,1].plot(time, voltage)
    axs[1,1].set_xlabel(XLABEL_ECHEM)#, fontsize=FONTSIZE)
    axs[1,1].set_ylabel(YLABEL_ECHEM)#, fontsize=FONTSIZE)
    for vline in VLINES_ECHEM:
        axs[1,1].axvline(x=vline, ls="--", c="k", lw=2)
    # props = dict(fc="w", alpha=0.5, ec="None")
    for i,ax in enumerate(axs.flat, start=97):
        if i < 99:
            t = ax.text(0.05, 0.9, f"({chr(i)})",
                        transform=ax.transAxes,
                        # bbox=props
                        )
        else:
            ax.text(0.05, 0.8, f"({chr(i)})",
                    transform=ax.transAxes,
                    # bbox=props,
                    )
    plt.subplots_adjust(wspace=0.3, hspace=0.1)
    fig.legend(compnames, loc='upper center', ncol=len(compnames), borderaxespad=-0.2,
               edgecolor='white')
    plt.savefig("png/nmf_echem.png", bbox_inches="tight")
    plt.savefig("pdf/nmf_echem.pdf", bbox_inches="tight")
    plt.close()

    return None


def main():
    folders = ["png", "pdf"]
    for folder in folders:
        if not (Path.cwd() / folder).exists():
            (Path.cwd() / folder).mkdir()
    csvfiles = list((Path.cwd() / "data").glob("*.csv"))
    compfile, phasefile, reconfile = csvfiles[0], csvfiles[1], csvfiles[2]
    xcomps, compnames, comps = comp_extracter(compfile)
    scans, phasenames, phasecomps = phase_extracter(phasefile)
    for i in range(len(scans)):
        if scans[i] > 30:
            scans[i] = scans[i]+2
    xrecon, recon = recon_extracter(reconfile)
    comp_plotter(xcomps, compnames, comps)
    phase_plotter(scans, phasenames, phasecomps)
    recon_plotter(xrecon, recon)
    recon_comp_plotter(xcomps, compnames, comps, xrecon, recon)
    echemfile = list((Path.cwd() / "data").glob("*.txt"))[0]
    time, voltage = echem_collector(echemfile)
    for i in range(len(time)):
        if time[i] < 22.1:
            time_max_index = i + 1
    time, voltage = time[0:time_max_index], voltage[0:time_max_index]
    echem_plotter(time, voltage)
    phase_chem_plotter(scans, phasenames, phasecomps, time, voltage)
    nmf_echem_plotter(xcomps, compnames, comps,
                          scans, phasenames, phasecomps,
                          xrecon, recon,
                          time, voltage)

    return None


if __name__ == "__main__":
    main()

# End of file.
