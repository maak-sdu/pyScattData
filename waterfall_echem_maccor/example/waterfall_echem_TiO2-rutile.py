import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from diffpy.utils.parsers.loaddata import loadData
import matplotlib.ticker as ticker

# INPUT SECTION
FILE_EXT = 'gr'
X_COLUMN = 0
Y_COLUMN = 1

DPI = 300
FIGSIZE = (12,4)
FONTSIZE = 20
XMIN = 1
XMAX = 50
YFRACOFFSET = 0.75
PLOTFREQ = 5

X_LABEL = r"$r$ $[\mathrm{\AA}]$"
Y_LABEL = r"$G$ $[\mathrm{\AA}^{-2}]$"

COLORSCHEME = 'blue'

# ----------------------------------------------------------------------
# DATA SECTION
filepaths= list((Path.cwd() / 'data').glob('*.' + FILE_EXT))
filepaths_i = [i for i in range(0, len(filepaths)) if i % PLOTFREQ == 0]
filepaths = [filepaths[i] for i in filepaths_i]
data = [loadData(file) for file in filepaths]
x = data[0][:,X_COLUMN]
ymin = [np.amin(dataset[:,1]) for dataset in data]
ymax = [np.amax(dataset[:,1]) for dataset in data]
ymin = min(ymin)
ymax = max(ymax)
yoffset = [data[i][:,Y_COLUMN] + i*YFRACOFFSET*(ymax-ymin) for i in range(0, len(data))]
yoff_min = np.amin(yoffset)
yoff_max = np.amax(yoffset)
yoff_range = yoff_max - yoff_min
yaxis_min = yoff_min - 0.01 * yoff_range
yaxis_max = yoff_max + 0.01 * yoff_range

# PLOT SECTION
if COLORSCHEME == 'grey':
    colors = plt.cm.Greys(np.linspace(0.5, 1, len(data)+1))
elif COLORSCHEME == 'purple':
    colors = plt.cm.Purples(np.linspace(0.5, 1, len(data)+1))
elif COLORSCHEME == 'blue':
    colors = plt.cm.Blues(np.linspace(1, 0.5, len(data)+1))
elif COLORSCHEME == 'green':
    colors = plt.cm.Greens(np.linspace(0.5, 1, len(data)+1))
elif COLORSCHEME == 'orange':
    colors = plt.cm.Oranges(np.linspace(0.5, 1, len(data)+1))
elif COLORSCHEME == 'red':
    colors = plt.cm.Reds(np.linspace(0.5, 1, len(data)+1))


maccor_echem_file = list((Path.cwd() / 'data').glob('*.txt'))[0]
with open(maccor_echem_file, 'r') as input_file:
    lines = input_file.readlines()
for i,line in enumerate(lines):
    if "Rec	Cycle P	Cycle C	Step	TestTime	StepTime" in line:
        start = i + 3
time_min_pre, time_min, time_s, time_h, voltage = [], [], [], [], []
for i in range(start, len(lines)):
    time = float(lines[i].split()[4])
    time_min_pre.append(time)
    voltage.append(float(lines[i].split()[9]))
for i in range(0, len(time_min_pre)):
    time_min_corrected = time_min_pre[i] - time_min_pre[0]
    time_min.append(time_min_corrected)
    time_s.append(time_min_corrected * 60)
    time_h.append(time_min_corrected / 60)
time, time_min_pre, voltage = np.array(time), np.array(time_min_pre), np.array(voltage)
time_min_corrected, time_min = np.array(time_min_corrected), np.array(time_min)
time_s, time_h = np.array(time_s), np.array(time_h)

# fig, axs = plt.subplots(dpi=DPI, figsize=FIGSIZE, ncols=2)
fig = plt.figure(dpi=DPI, figsize=FIGSIZE, constrained_layout=True)
gs = fig.add_gridspec(1,4)
fig_ax0 = fig.add_subplot(gs[0,:-1])
fig_ax1 = fig.add_subplot(gs[0,3])
for i in range(0, len(yoffset)):
    if i < 4:
        fig_ax0.plot(x, yoffset[i], c=colors[i*2])
    else:
        fig_ax0.plot(x, yoffset[i], c=colors[8])
fig_ax0.set_xlim(XMIN, XMAX)
fig_ax0.set_ylim(yaxis_min, yaxis_max)
fig_ax0.set_xlabel(X_LABEL, fontsize=FONTSIZE)
fig_ax0.set_ylabel(Y_LABEL, fontsize=FONTSIZE)
fig_ax0.xaxis.set_major_locator(ticker.MultipleLocator(5))
fig_ax0.xaxis.set_minor_locator(ticker.MultipleLocator(1))
fig_ax0.yaxis.set_major_locator(ticker.MultipleLocator(5))
fig_ax0.yaxis.set_minor_locator(ticker.MultipleLocator(1))
# axs[0].set_xticks(fontsize=0.8*FONTSIZE)
# axs[0].set_yticks(fontsize=0.8*FONTSIZE)
for i in range(len(voltage)):
    if voltage[i] <= 1.0001:
        voltage_index = i
        break
    elif time_h[i] <= 2:
        time_index1 = i
    elif time_h[i] <= 4:
        time_index2 = i
    elif time_h[i] <= 7:
        time_index3 = i
fig_ax1.plot(voltage[:time_index1:], time_h[:time_index1:], c=colors[0])
fig_ax1.plot(voltage[time_index1:time_index2:], time_h[time_index1:time_index2:], c=colors[2])
fig_ax1.plot(voltage[time_index2:time_index3:], time_h[time_index2:time_index3:], c=colors[4])
fig_ax1.plot(voltage[time_index3:voltage_index:], time_h[time_index3:voltage_index:], c=colors[6])
fig_ax1.plot(voltage[voltage_index::], time_h[voltage_index:], c=colors[8])
fig_ax1.yaxis.tick_right()
fig_ax1.set_xlabel(r'$V$ $[\mathrm{V}]$', fontsize=FONTSIZE)
fig_ax1.set_ylabel(r'$t$ $[\mathrm{h}]$', fontsize=FONTSIZE)
fig_ax1.xaxis.set_major_locator(ticker.MultipleLocator(0.5))
fig_ax1.xaxis.set_minor_locator(ticker.MultipleLocator(0.25))
fig_ax1.yaxis.set_major_locator(ticker.MultipleLocator(5))
fig_ax1.yaxis.set_minor_locator(ticker.MultipleLocator(1))
fig_ax1.yaxis.set_label_position('right')
fig_ax1.set_xlim(1, 3)
fig_ax1.set_ylim(np.amin(time_h), np.amax(time_h))
fig_ax1.invert_xaxis()

# Vertical lines
# plt.axvline(x=2.0, ls='--', lw=0.5, c='k')
# plt.axvline(x=2.85, ls='--', lw=0.5, c='k')
# plt.axvline(x=4.5, ls='--', lw=0.5, c='k')

# Rectangles
# ax.add_patch(patches.Rectangle((1.6, yaxis_min*0.925), 0.6, (yaxis_max - yaxis_min)*0.991,
#                                 ls='--', lw=0.5, ec='r', fc='none'))
# ax.add_patch(patches.Rectangle((2.7, yaxis_min*0.925), 0.6, (yaxis_max - yaxis_min)*0.991,
#                                 ls='--', lw=0.5, ec='orange', fc='none'))
# ax.add_patch(patches.Rectangle((4.0, yaxis_min*0.925), 0.7, (yaxis_max - yaxis_min)*0.991,
#                                 ls='--', lw=0.5, ec='g', fc='none'))
# ax.add_patch(patches.Rectangle((8.0, yaxis_min*0.925), 1.0, (yaxis_max - yaxis_min)*0.991,
#                                 ls='--', lw=0.5, ec='b', fc='none'))

paths = [Path.cwd() / 'png', Path.cwd() / 'pdf']
for path in paths:
    if not path.exists():
        path.mkdir()
    plt.savefig(path / (FILE_EXT + "_waterfall_TiO2-rutile." + str(path.stem)), bbox_inches="tight")
