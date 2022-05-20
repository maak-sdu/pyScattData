import sys
from pathlib import Path
import numpy as np
import pandas as pd
from diffpy.utils.parsers.loaddata import loadData
from scipy.constants import physical_constants
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.gridspec import GridSpec
try:
    from bg_mpl_stylesheet.bg_mpl_stylesheet import bg_mpl_style
    PLOTSTYLE = "found"
except ImportError:
    PLOTSTYLE = None


# Inputs to load echem
INDEX_TIME = 0
INDEX_VOLTAGE = 1
INDEX_CURRENT = 2

# Inputs to calculate amount of working ion transferred
WORKING_ION_CHARGE = 1
WORKING_ION_START_VALUE = 0
MOLAR_MASS = 79.866
MASS = 0.6 * 11.276 * 10**-3


VOLTAGE_LIMITS = True
VOLTAGE_MIN = 1
VOLTAGE_MAX = 3
BREAKFACTOR_X = 0.06
BREAKFACTOR_Y = 0.05
TOLERANCE_FACTOR = 10**2

# Echem labels for plots
XLABEL = "$x$ in Li$_{x}$TiO$_{2}$"
ECHEMLABEL_DICT = {"V_t[h]": dict(x = r"$t$ $[\mathrm{h}]$",
                                  y = r"$V$ $[\mathrm{V}]$"),
                   "Ewe_Li_t[h]": dict(x = r"$t$ $[\mathrm{h}]$",
                                       y = r"$E_{\mathrm{we}}$ vs." + "\n" + r"Li/Li$^{+} [\mathrm{V}]$"),
                   "Ewe_Na_t[h]": dict(x = r"$t$ $[\mathrm{h}]$",
                                       y = r"$E_{\mathrm{we}}$ vs." + "\n" + r"Na/Na$^{+} [\mathrm{V}]$")
                    }

# Plot inputs
DPI = 600
FIGSIZE = (8,6)
FONTSIZE_LABELS = 20
FONTSIZE_TICKS = 16
XLABEL_COMPS = r"$r$ $[\mathrm{\AA}]$"
YLABEL_COMPS = r"$G$ $[\mathrm{\AA}^{-2}]$"
XLABEL_PHASERATIO = r"$t$ [h]"
YLABEL_PHASERATIO = r"$W$"
XLABEL_RECON = r"$NOC$"
YLABEL_RECON = r"$RE$"
XLABEL_ECHEM = ECHEMLABEL_DICT["Ewe_Li_t[h]"]["x"]
YLABEL_ECHEM = ECHEMLABEL_DICT["Ewe_Li_t[h]"]["y"]
VOLTAGE_MIN = 1
VOLTAGE_MAX = 3
MAJOR_TICK_INDEX_TIME = 5
MAJOR_TICK_INDEX_VOLTAGE = 0.5
# MAJOR_TICK_INDEX_SCAN = 10
MAJOR_TICK_INDEX_WEIGHT = 0.2
MAJOR_TICK_INDEX_R = 5
MAJOR_TICK_INDEX_G = 0.5
MAJOR_TICK_INDEX_RE = 5
MINOR_TICKS = 5
WSPACE = 0.45
HSPACE = 0.1
COLORS = ['#0B3C5D', '#B82601', '#1c6b0a', '#328CC1',
          '#a8b6c1', '#D9B310', '#984B43', '#76323F',
          '#626E60', '#AB987A', '#C09F80', '#b0b0b0ff']

DISCHARGE_CHANGE = 5.75
DISCHARGE_END = 11.82444444
CHARGE_CHANGE = 15.25
CHARGE_END = 19.84888889
# VLINES_NMF = [12, 23.5, 30, 38.75]
# VLINES_NMF = [11, 22, 28, 37]

ECHEM_END = 22.26416667
SCAN_END = 42.25
VLINES_NMF = [(DISCHARGE_CHANGE / ECHEM_END) * SCAN_END,
              (DISCHARGE_END / ECHEM_END) * SCAN_END,
              (CHARGE_CHANGE / ECHEM_END) * SCAN_END,
              (CHARGE_END / ECHEM_END) * SCAN_END,
              ]
# VLINES_NMF = None
VLINES_ECHEM = [DISCHARGE_CHANGE, DISCHARGE_END, CHARGE_CHANGE, CHARGE_END]
# VLINES_ECHEM = None


def comp_extract(compfile):
    df = pd.read_csv(compfile)
    xcomps = [df[col].to_numpy() for col in df.columns if "Unnamed" in col][0]
    compnames = np.array([int(col)+1 for col in df.columns if not "Unnamed" in col])
    comps = [df[f"{col-1}"].to_numpy() for col in compnames]
    d_comp = {}
    for i in range(len(compnames)):
        d_comp[compnames[i]] = dict(xcomps=xcomps, comps=comps[i])

    return d_comp


def weight_extract(phasefile):
    df = pd.read_csv(phasefile)
    rows = df.to_numpy()
    scans = np.array([int(col) for col in df.columns if not "Unnamed" in col])
    names = np.array([int(rows[i][0])+1 for i in range(rows.shape[0])])
    weights = np.array([rows[i][1:] for i in range(rows.shape[0])])
    d_weights = {}
    for i in range(len(names)):
        d_weights[names[i]] = dict(scans=scans, weights=weights[i])

    return d_weights


def recon_extract(reconfile):
    df = pd.read_csv(reconfile)
    xrecon, recon = df.to_numpy()[:,0], df.to_numpy()[:,1]
    d_recon = dict(xrecon=xrecon, recon=recon)

    return d_recon


def comp_plot(d_comps):
    compnames = list(d_comps.keys())
    xcomps = [d_comps[e]["xcomps"] for e in compnames]
    comps = [d_comps[e]["comps"] for e in compnames]
    max_comps = np.array([np.amax(comp) for comp in comps])
    max_comps_sum = [np.sum(max_comps[0:i]) for i in range(len(max_comps))]
    comps_offset = comps[0]
    for i in range(1, len(max_comps)):
        comps_offset = np.vstack((comps_offset, comps[i] + max_comps_sum[i] + 0.05*max_comps_sum[-1]))
    compfig = plt.figure(dpi=DPI, figsize=FIGSIZE)
    # compfig = plt.figure()
    plt.style.use(bg_mpl_style)
    for i in range(len(compnames)):
        plt.plot(xcomps[i], comps_offset[i], label=compnames[i])
    plt.legend(loc="upper right")
    plt.xlabel(XLABEL_COMPS)#, fontsize=FONTSIZE)
    plt.ylabel(YLABEL_COMPS)#, fontsize=FONTSIZE)
    plt.xlim(np.amin(xcomps), np.amax(xcomps))
    plt.savefig("png/components.png", bbox_inches="tight")
    plt.savefig("pdf/components.pdf", bbox_inches="tight")
    plt.savefig("svg/components.svg", bbox_inches="tight")
    plt.close()

    return None


def weight_plot(d_weights):
    phasenames = list(d_weights.keys())
    scans = [d_weights[e]["scans"] for e in phasenames]
    weights = [d_weights[e]["weights"] for e in phasenames]
    phasefig = plt.figure(dpi=DPI, figsize=FIGSIZE)
    if not isinstance(PLOTSTYLE, type(None)):
        plt.style.use(bg_mpl_style)
    for i in range(len(phasenames)):
        plt.plot(scans[i], weights[i], label=phasenames[i], marker="o")
    plt.xlabel(XLABEL_PHASERATIO)
    plt.ylabel(YLABEL_PHASERATIO)
    plt.xlim(np.amin(scans), np.amax(scans))
    plt.savefig("png/weights.png", bbox_inches="tight")
    plt.savefig("pdf/weights.pdf", bbox_inches="tight")
    plt.savefig("svg/weights.svg", bbox_inches="tight")
    plt.close()

    return None


def recon_plot(d_recon):
    xrecon, recon = d_recon["xrecon"], d_recon["recon"]
    reconfig = plt.figure(dpi=DPI, figsize=FIGSIZE)
    if not isinstance(PLOTSTYLE, type(None)):
        plt.style.use(bg_mpl_style)
    plt.plot(xrecon, recon)
    plt.xlabel(XLABEL_RECON)
    plt.ylabel(YLABEL_RECON)
    plt.xticks(xrecon)
    plt.xlim(np.amin(xrecon), np.amax(xrecon))
    plt.savefig("png/recon_error.png", bbox_inches="tight")
    plt.savefig("pdf/recon_error.pdf", bbox_inches="tight")
    plt.savefig("svg/recon_error.svg", bbox_inches="tight")
    plt.close()

    return None


def recon_comp_plot(d_comps, d_recon):
    compnames = list(d_comps.keys())
    xcomps = [d_comps[e]["xcomps"] for e in compnames]
    comps = [d_comps[e]["comps"] for e in compnames]
    xrecon, recon = d_recon["xrecon"], d_recon["recon"]
    max_comps = np.array([np.amax(comp) for comp in comps])
    max_comps_sum = [np.sum(max_comps[0:i]) for i in range(len(max_comps))]
    comps_offset = comps[0]
    for i in range(1, len(max_comps)):
        comps_offset = np.vstack((comps_offset, comps[i] + max_comps_sum[i] + 0.05*max_comps_sum[-1]))
    if not isinstance(PLOTSTYLE, type(None)):
        plt.style.use(bg_mpl_style)
    fig, axs = plt.subplots(dpi=DPI, figsize=FIGSIZE, nrows=2, ncols=1)
    axs[0].plot(xrecon, recon)
    axs[0].set_xlabel(XLABEL_RECON)
    axs[0].set_ylabel("Recon. error")
    axs[0].set_xticks(xrecon)
    axs[0].tick_params(axis="x", top="True", bottom="True", labeltop=True, labelbottom=False)
    axs[0].xaxis.set_label_position("top")
    axs[0].set_xlim(np.amin(xrecon), np.amax(xrecon))
    for i in range(len(compnames)):
        axs[1].plot(xcomps[i], comps_offset[i], label=compnames[i])
    axs[1].legend(loc="upper right")
    axs[1].set_xlabel(XLABEL_COMPS)#, fontsize=FONTSIZE)
    axs[1].set_ylabel(YLABEL_COMPS)#, fontsize=FONTSIZE)
    axs[1].set_xlim(np.amin(xcomps), np.amax(xcomps))
    plt.savefig("png/recon_comp.png", bbox_inches="tight")
    plt.savefig("pdf/recon_comp.pdf", bbox_inches="tight")
    plt.savefig("svg/recon_comp.svg", bbox_inches="tight")
    plt.close()

    return None


def echem_collect(echemfile):
    d = {}
    data = loadData(echemfile)
    d["time"] = data[:,INDEX_TIME]
    d["voltage"] = data[:,INDEX_VOLTAGE]
    d["current"] = data[:,INDEX_CURRENT]

    return d


def x_from_dict_calcualte(d):
    time, current = d["time"], d["current"]
    x = [WORKING_ION_START_VALUE]
    n = MASS / MOLAR_MASS
    f = physical_constants["Faraday constant"][0]
    for i in range(1, len(time)):
        delta_q =  - current[i] * (time[i] - time[i-1]) * 60**2
        delta_x = delta_q / (n * f)
        x.append(x[i-1] + delta_x)
    change_indices = [i for i in range(1, len(current))
                      if current[i] != 0
                      and current[i] * current[i-1] <= 0]
    d["x"], d["change_indices"] = np.array(x), np.array(change_indices)

    return d


def echem_plot(d_echem):
    time, voltage = d_echem["time"], d_echem["voltage"]
    echemfig = plt.figure(dpi=DPI, figsize=FIGSIZE)
    if not isinstance(PLOTSTYLE, type(None)):
        plt.style.use(bg_mpl_style)
    plt.plot(time, voltage)
    plt.xlabel(XLABEL_ECHEM)
    plt.ylabel(YLABEL_ECHEM.replace("\n", " "))
    plt.xlim(np.amin(time), np.amax(time))
    plt.ylim(VOLTAGE_MIN, VOLTAGE_MAX)
    plt.savefig("png/echem.png", bbox_inches="tight")
    plt.savefig("pdf/echem.pdf", bbox_inches="tight")
    plt.savefig("svg/echem.svg", bbox_inches="tight")
    plt.close()

    return None


def weights_echem_plot(d_weights, d_echem):
    phasenames = list(d_weights.keys())
    scans = [d_weights[e]["scans"] for e in phasenames]
    weights = [d_weights[e]["weights"] for e in phasenames]
    time, voltage = d_echem["time"], d_echem["voltage"]
    fig, axs = plt.subplots(dpi=DPI, figsize=FIGSIZE, nrows=2, ncols=1,
                            gridspec_kw={'height_ratios': [2, 1]})
    if not isinstance(PLOTSTYLE, type(None)):
        plt.style.use(bg_mpl_style)
    for i in range(len(phasenames)):
        axs[0].plot(scans[i], weights[i], label=phasenames[i], marker="o")
    axs[0].set_xlabel(XLABEL_PHASERATIO, fontsize=FONTSIZE_LABELS)
    axs[0].set_ylabel(YLABEL_PHASERATIO, fontsize=FONTSIZE_LABELS)
    axs[0].tick_params(axis="x",
                       top="True",
                       bottom="True",
                       labeltop=True,
                       labelbottom=False)
    axs[0].tick_params(axis="both", labelsize=FONTSIZE_TICKS)
    axs[0].xaxis.set_label_position("top")
    axs[0].set_xlim(np.amin(scans[0]), np.amax(scans[0]))
    fig.legend(phasenames, loc='upper center', ncol=len(phasenames), borderaxespad=-0.2,
               edgecolor='white')
    for vline in VLINES_NMF:
        axs[0].axvline(x=vline, ls="--", c="k", lw=2)
    axs[1].plot(time, voltage)
    axs[1].set_xlabel(XLABEL_ECHEM, fontsize=FONTSIZE_LABELS)
    axs[1].set_ylabel(YLABEL_ECHEM, fontsize=FONTSIZE_LABELS)
    for vline in VLINES_ECHEM:
        axs[1].axvline(x=vline, ls="--", c="k", lw=2)
    axs[1].set_xlim(np.amin(time), np.amax(time))
    axs[1].set_ylim(VOLTAGE_MIN, VOLTAGE_MAX)
    axs[1].tick_params(axis="both", labelsize=FONTSIZE_TICKS)
    plt.savefig("png/weights_echem.png", bbox_inches="tight")
    plt.savefig("pdf/weights_echem.pdf", bbox_inches="tight")
    plt.savefig("svg/weights_echem.svg", bbox_inches="tight")
    plt.close()

    return None


def nmf_echem_plot(d_comps, d_weights, d_recon, d_echem):
    compnames = list(d_comps.keys())
    xcomps = [d_comps[e]["xcomps"] for e in compnames]
    comps = [d_comps[e]["comps"] for e in compnames]
    phasenames = list(d_weights.keys())
    scans = [d_weights[e]["scans"] for e in phasenames]
    weights = [d_weights[e]["weights"] for e in phasenames]
    xrecon, recon = d_recon["xrecon"], d_recon["recon"]
    max_comps = np.array([np.amax(comp) for comp in comps])
    max_comps_sum = [np.sum(max_comps[0:i]) for i in range(len(max_comps))]
    comps_offset = comps[0]
    for i in range(1, len(max_comps)):
        comps_offset = np.vstack((comps_offset, comps[i] + max_comps_sum[i] + 0.05*max_comps_sum[-1]))
    time, voltage = d_echem["time"], d_echem["voltage"]
    current, x = d_echem["current"], d_echem["x"]
    change_indices = d_echem["change_indices"]
    t_changes = [time[e] for e in change_indices]
    t_changes_labels = [f"{x[e]:.2f}" for e in change_indices]
    xticks_labels = [f"{e:.1f}" for e in np.arange(0, 1, 0.5)]
    xticks_labels.append(t_changes_labels[0])
    for e in np.arange(0.5, 0, -0.5):
        xticks_labels.append(f"{e:.1f}")
    xticks_labels.append(t_changes_labels[1])
    # for e in np.arange(0.5, 1, 0.5):
    #     xticks_labels.append(f"{e:.1f}")
    # print(xticks_labels)
    # sys.exit()
    t_xticks = np.array([])
    j = 0
    for i in range(0, len(x)):
        if np.isclose(np.array(xticks_labels[j], dtype=float),
                      x[i],
                      atol=abs(x[0] - x[1]) * TOLERANCE_FACTOR
                      ):
            t_xticks = np.append(t_xticks, time[i])
            j += 1
            if j == len(xticks_labels):
                break
    time_min, time_max = np.amin(time), np.amax(time)
    time_range = time_max - time_min
    voltage_min, voltage_max = np.amin(voltage), np.amax(voltage)
    voltage_range = voltage_max - voltage_min
    if not isinstance(PLOTSTYLE, type(None)):
        plt.style.use(bg_mpl_style)
    fig, axs = plt.subplots(dpi=DPI, figsize=FIGSIZE, nrows=2, ncols=2,
                            gridspec_kw={'height_ratios': [2, 1],
                                         'wspace': WSPACE,
                                         'hspace': HSPACE,
                                         }
                            )
    for i in range(len(compnames)):
        axs[0,0].plot(xcomps[i], comps_offset[i], label=compnames[i])
    axs[0,0].set_xlabel(XLABEL_COMPS)#, fontsize=FONTSIZE)
    axs[0,0].set_ylabel(YLABEL_COMPS)#, fontsize=FONTSIZE)
    axs[0,0].tick_params(axis="x", top="True", bottom="True", labeltop=True, labelbottom=False)
    axs[0,0].xaxis.set_label_position("top")
    axs[0,0].set_xlim(np.amin(xcomps), np.amax(xcomps))
    axs[0,0].xaxis.set_major_locator(MultipleLocator(MAJOR_TICK_INDEX_R))
    axs[0,0].xaxis.set_minor_locator(MultipleLocator(MAJOR_TICK_INDEX_R / MINOR_TICKS))
    axs[0,0].yaxis.set_major_locator(MultipleLocator(MAJOR_TICK_INDEX_G))
    axs[0,0].yaxis.set_minor_locator(MultipleLocator(MAJOR_TICK_INDEX_G / MINOR_TICKS))
    axs[1,0].plot(xrecon, recon, marker="o")
    axs[1,0].set_xlabel(XLABEL_RECON)
    axs[1,0].set_ylabel(YLABEL_RECON)
    axs[1,0].set_xticks(xrecon)
    axs[1,0].tick_params(axis="x", top="True", bottom="True", labeltop=False, labelbottom=True)
    axs[1,0].xaxis.set_label_position("bottom")
    axs[1,0].set_xlim(np.amin(xrecon), np.amax(xrecon))
    axs[1,0].yaxis.set_major_locator(MultipleLocator(MAJOR_TICK_INDEX_RE))
    axs[1,0].yaxis.set_minor_locator(MultipleLocator(MAJOR_TICK_INDEX_RE / MINOR_TICKS))
    for i in range(len(phasenames)):
        axs[0,1].plot(scans[i] * (time_range / (len(scans[0]) + 1)), weights[i], label=phasenames[i], marker="o")
    axs[0,1].set_xlabel(XLABEL_PHASERATIO)#, fontsize=FONTSIZE)
    axs[0,1].set_ylabel(YLABEL_PHASERATIO)#, fontsize=FONTSIZE)
    axs[0,1].set_xticks([i*10 for i in range(1, (scans[0][-1] // 10)+1)])
    axs[0,1].tick_params(axis="x", top="True", bottom="True", labeltop=True, labelbottom=False)
    axs[0,1].xaxis.set_label_position("top")
    if not isinstance(VLINES_NMF, type(None)):
        for t in t_changes:
            axs[0,1].axvline(x=0.989*t, ls="--", c="k", lw=2)
    axs[0,1].set_xlim(time_min, time_max)
    axs[0,1].xaxis.set_major_locator(MultipleLocator(MAJOR_TICK_INDEX_TIME))
    axs[0,1].xaxis.set_minor_locator(MultipleLocator(MAJOR_TICK_INDEX_TIME / MINOR_TICKS))
    axs[0,1].yaxis.set_major_locator(MultipleLocator(MAJOR_TICK_INDEX_WEIGHT))
    axs[0,1].yaxis.set_minor_locator(MultipleLocator(MAJOR_TICK_INDEX_WEIGHT / MINOR_TICKS))
    # gs = GridSpec(nrows=2,
    #               ncols=2,
    #               figure=fig,
    #               width_ratios=[1, 0.1375],
    #               height_ratios=[1, 0.4],
    #               hspace=HSPACE,
    #               )
    # axs10 = axs[1,1].add_subplot(gs[1,0])
    axs11 = axs[1,1].twiny()
    axs11.plot(time, voltage)
    axs11.set_xlim(time_min, time_max)
    axs[1,1].set_xlim(time_min, time_max)
    # axs[1,1].plot(time, voltage)
    # axs11.set_xlabel(XLABEL_ECHEM)#, fontsize=FONTSIZE)
    # axs11.set_ylabel(YLABEL_ECHEM)#, fontsize=FONTSIZE)
    axs11.tick_params(axis="x", labeltop=False, labelbottom=False)
    if not isinstance(VLINES_ECHEM, type(None)):
        # for t in t_changes:
        #     axs11.axvline(x=0.99*t, ls="--", c="k", lw=2)
        axs11.axvline(x=0.989*t_changes[0], ls="--", c="k", lw=2)
        axs11.axvline(x=0.9925*t_changes[1], ls="--", c="k", lw=2)
    # axs11.set_xlim(np.amin(time), np.amax(time))
    axs11.set_ylim(VOLTAGE_MIN, VOLTAGE_MAX)
    axs11.xaxis.set_major_locator(MultipleLocator(MAJOR_TICK_INDEX_TIME))
    axs11.xaxis.set_minor_locator(MultipleLocator(MAJOR_TICK_INDEX_TIME / MINOR_TICKS))
    axs11.yaxis.set_major_locator(MultipleLocator(MAJOR_TICK_INDEX_VOLTAGE))
    axs11.yaxis.set_minor_locator(MultipleLocator(MAJOR_TICK_INDEX_VOLTAGE / MINOR_TICKS))

    axs[1,1].set_xticks(t_xticks)
    axs[1,1].set_xticklabels(xticks_labels)
    axs[1,1].set_xlabel(XLABEL, fontsize=FONTSIZE_LABELS)
    axs[1,1].set_ylabel(YLABEL_ECHEM, fontsize=FONTSIZE_LABELS)
    axs[1,1].xaxis.set_tick_params(labelsize=FONTSIZE_TICKS)
    axs[1,1].yaxis.set_tick_params(labelsize=FONTSIZE_TICKS)
    # for i in range(len(t_changes)):
    #     axs[1,1].text(t_changes[i] - BREAKFACTOR_X * time_range,
    #              voltage_min - BREAKFACTOR_Y * voltage_range,
    #              "|",
    #              rotation=45)
    scan_time = np.array([i * (time_range / (len(scans) - 1))
                          for i in range(len(scans))])

    fig.legend(compnames, loc='upper center', ncol=len(compnames),
               borderaxespad=-0.2, edgecolor='white')
    axs[0,0].text(0.84, 0.9, "(a)", transform=axs[0,0].transAxes)
    axs[1,0].text(0.84, 0.8, "(b)", transform=axs[1,0].transAxes)
    axs[0,1].text(0.05, 0.9, "(c)", transform=axs[0,1].transAxes)
    axs[1,1].text(0.05, 0.8, "(d)", transform=axs[1,1].transAxes)
    plt.savefig("png/nmf_echem.png", bbox_inches="tight")
    plt.savefig("pdf/nmf_echem.pdf", bbox_inches="tight")
    plt.savefig("svg/nmf_echem.svg", bbox_inches="tight")
    plt.close()

    return None


def main():
    print(f"{80*'-'}\nPlease see the top of this .py file for plot settings.")
    folders = ["png", "pdf", "svg"]
    for folder in folders:
        if not (Path.cwd() / folder).exists():
            (Path.cwd() / folder).mkdir()
    csvfiles = list((Path.cwd() / "data_nmf").glob("*.csv"))
    compfile, weightfile, reconfile = csvfiles[0], csvfiles[1], csvfiles[2]
    print(f"{80*'-'}\nExtracting...\n\tcomponents")
    d_comps = comp_extract(compfile)
    print("\tweights")
    d_weights = weight_extract(weightfile)
    for k in d_weights.keys():
        for i in range(len(d_weights[k]["scans"])):
            if d_weights[k]["scans"][i] > 30:
                d_weights[k]["scans"][i] = i + 2
    print("\treconstruction error")
    d_recon = recon_extract(reconfile)
    echemfile = list((Path.cwd() / "data_echem").glob("*.txt"))[0]
    print("\techem")
    d_echem = echem_collect(echemfile)
    d_echem = x_from_dict_calcualte(d_echem)
    # for i in range(len(time)):
    #     if time[i] < 22.1:
    #         time_max_index = i + 1
    # time, voltage = time[0:time_max_index], voltage[0:time_max_index]
    print(f"{80*'-'}\nPlotting...\n\tcomponents")
    comp_plot(d_comps)
    print("\tweights")
    weight_plot(d_weights)
    print("\treconstruction error")
    recon_plot(d_recon)
    print("\techem")
    echem_plot(d_echem)
    print("\treconstruction error and components together")
    recon_comp_plot(d_comps, d_recon)
    print("\tweights and echem together")
    weights_echem_plot(d_weights, d_echem)
    print("\teverything together")
    nmf_echem_plot(d_comps, d_weights, d_recon, d_echem)
    print(f"{80*'-'}\nDone plotting.\nPlease see the plots in the output "
          f"folders.")

    return None


if __name__ == "__main__":
    main()

# End of file.
