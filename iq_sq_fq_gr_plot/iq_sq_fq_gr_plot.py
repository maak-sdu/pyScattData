import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from diffpy.utils.parsers.loaddata import loadData

DPI = 300
FIGSIZE = (8,4)
FONTSIZE = 12
LINEWIDTH = 1
COLORSCHEME = 'blue'
COLORS = ["#0B3C5D", "#B82601", "#1c6b0a", "#328CC1", "#062F4F", "#D9B310",
          "#984B43", "#76323F", "#626E60", "#AB987A", "#C09F80"]

folders = ['png', 'pdf']
for folder in folders:
    if not (Path.cwd() / folder).exists():
        (Path.cwd() / folder).mkdir()
d = {}
datafiles = (Path.cwd() / 'data').glob('*.*')
for f in datafiles:
    xy = loadData(f)
    d[str(f.suffix).split('.')[-1]] = xy
fig, axs = plt.subplots(dpi=DPI, nrows=2, ncols=2, figsize=FIGSIZE)
axs[0,0].plot(d['iq'][:,0], d['iq'][:,1], lw=LINEWIDTH, c=COLORS[3])
axs[0,0].set_xlabel(r'$Q$ $[\mathrm{\AA}^{-1}]$')
axs[0,0].set_ylabel(r'$I$ $[\mathrm{a.u.}]$')
axs[0,0].ticklabel_format(style='sci', axis='y', scilimits=(0,0))
axs[0,0].set_xlim(min(d['iq'][:,0]), max(d['iq'][:,0]))
axs[0,1].plot(d['sq'][:,0], d['sq'][:,1], lw=LINEWIDTH, c=COLORS[0])
axs[0,1].set_xlabel(r'$Q$ $[\mathrm{\AA}^{-1}]$')
axs[0,1].set_ylabel(r'$S$ $[\mathrm{a.u.}]$')
axs[0,1].set_xlim(min(d['sq'][:,0]), max(d['sq'][:,0]))
axs[1,1].plot(d['fq'][:,0], d['fq'][:,1], lw=LINEWIDTH, c=COLORS[2])
axs[1,1].set_xlabel(r'$Q$ $[\mathrm{\AA}^{-1}]$')
axs[1,1].set_ylabel(r'$F$ $[\mathrm{\AA}^{-1}]$')
axs[1,1].set_xlim(min(d['fq'][:,0]), max(d['fq'][:,0]))
axs[1,0].plot(d['gr'][:,0], d['gr'][:,1], lw=LINEWIDTH, c=COLORS[1])
axs[1,0].set_xlabel(r'$r$ $[\mathrm{\AA}]$')
axs[1,0].set_ylabel(r'$G$ $[\mathrm{\AA}^{-2}]$')
axs[1,0].set_xlim(min(d['gr'][:,0]), max(d['gr'][:,0]))
plt.figtext(0.485, 0.725, r'$\rightarrow$', fontsize=20)
plt.figtext(0.75, 0.46, r'$\downarrow$', fontsize=20)
plt.figtext(0.485, 0.285, r'$\leftarrow$', fontsize=20)
fig.tight_layout(pad=2)
for folder in folders:
    plt.savefig(f"{folder}/iq_fq_sq_gr.{folder}", bbox_inches='tight')

# End of file.
