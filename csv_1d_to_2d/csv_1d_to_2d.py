import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

DPI = 300
XLABEL = r"$\mathrm{Horizontal\,pos.}$ $[\mathrm{mm}]$"
YLABEL = r"$\mathrm{Vertical\,pos.}$ $[\mathrm{mm}]$"
PIXELSIZE = 50*10**-3
SHRINK = 0.935
FONTSIZE_LABELS = 20
FONTSIZE_TICKS = 14
CBAR_SCILIMIT = 10**3
CMAPS = {0:'viridis', 1:'plasma', 2:'inferno', 3:'magma', 4:'Greys',
         5:'Purples', 6:'Blues', 7:'Greens', 8:'Oranges', 9:'Reds',
         10: 'YlOrBr', 11:'YlOrRd', 12:'OrRd', 13:'PuRd', 14:'RdPu',
         15:'BuPu', 16:'GnBu', 17:'PuBu', 18:'YlGnBu', 19:'PuBuGn',
         20:'BuGn', 21:'YlGn', 22:'binary', 23:'gist_yarg', 24:'gist_gray',
         25:'gray', 26:'bone', 27:'pink', 28:'spring', 29:'summer',
         30:'autumn', 31:'winter', 32:'cool', 33:'Wistia', 34:'hot',
         35:'afmhot', 36:'gist_heat', 37:'copper', 38:'PiYG', 39:'PRGn',
         40:'BrBG', 41:'PuOr', 42:'RdGy', 43:'RdBu', 44:'RdYlBu',
         45:'RdYlGn', 46:'Spectral', 47:'coolwarm', 48:'bwr', 49:'seismic',
         50:'twilight', 51:'twilight_shifted', 52:'hsv', 53:'ocean', 54:'gist_earth',
         55:'terrain', 56:'gist_stern', 57:'gnuplot', 58:'gnuplot2', 59:'CMRmap',
         60:'cubehelix', 61:'brg', 62:'gist_rainbow', 63:'rainbow', 64:'jet',
         65:'turbo', 66:'nipy_spectral', 67:'gist_ncar'}


def one_to_two_d(file):
    d = {}
    print(f"File:\t{file.name}")
    df = pd.read_csv(file, delimiter='\t')
    cols = df.columns
    for i in range(1, len(cols)):
        df[cols[i]] = df[cols[i]].astype(float)
    d[cols[0]] = list(df[cols[0]])
    for i in range(1, len(cols)):
        d[cols[i]] = df[cols[i]].to_numpy()
    print(f"\n\tThe following quantities are present:")
    for k in d.keys():
        if not 'unnamed' in k.lower():
            print(f"\t\t{k}")
    col_len = len(d[list(d.keys())[0]])
    nor = int(input(f"\n\tThe length of the 1D column is: {col_len}\
            \n\n\tPlease provide the desired number of rows for the new matrix: "))
    noc = int(col_len / nor)
    print(f"\tNumber of columns: {noc}")
    # pixelsize = float(input(f"\tPlease provide the pixelsize in µm: "))
    pixelsize = PIXELSIZE
    plot_default = input("\n\tDo you want to plot all quantities with default settings? (y/n): ")
    if plot_default == "n":
        print("\tNumber\tColormap")
        for k,v in CMAPS.items():
            print(f"\t{k}:\t{v}")
        cmap_desire = CMAPS[int(input("\n\tPlease select the number of the desired colormap: "))]
        print(f"\tColormap '{cmap_desire}' was selected.")
    else:
        cmap_desire = CMAPS[0]
    print(f"\n\tWriting txt files and plotting...")
    for k in d.keys():
        try:
            if isinstance(d[k], np.ndarray) and 'unnamed' not in k.lower():
                print(f"\t\t{k}")
                num_header = '1'
                for i in range(1, noc):
                    num_header += f"\t{i+1}"
                new_array = np.reshape(d[k], (nor, noc))
                np.savetxt(f"{file.stem}/txt/{file.stem}_{k}.txt", new_array,
                           fmt='%.5e', encoding='utf-8', header=num_header,
                           comments='')
                if plot_default == "n":
                    plot_desire = input(f"\t\t\tDo you want to plot '{k}'? (y/n): ")
                    if plot_desire == "y":
                        cbar_limits = input("\t\t\t\tPlease provide min, max for colorbar: ")
                    else:
                        continue
                else:
                    cbar_limits = None
                two_d_array_plot(new_array, k, file, pixelsize, cmap_desire, cbar_limits)
        except ValueError:
            print(f"{90*'-'}\nValueError: cannot reshape array of size {col_len} into shape ({nor},{noc})\
                    \nPlease rerun the code and provide a proper number of columns for the 2D array.\
                    \n{90*'-'}")
            sys.exit()
    print(f"\n\ttxt files containing {new_array.shape} arrays have been saved to the txt directory.\
            \n\tPlots have been saved to the 'pdf' and 'png' directories.\
            \n{90*'-'}")

    return plot_default, cmap_desire


def delimiter_fix(file):
    with open(file) as f:
        lines = f.readlines()
        header = lines[0].split()
        noc = len(header)
    new_del = []
    for line in lines:
        cols = line.split()
        s = ''
        for col in cols:
            s += f"{col}\t"
        new_del.append(f"{s}\n")
    with open(f"delimiter_fix/{file.stem}.txt", 'w') as o:
        o.writelines(new_del)

    return None


def two_d_array_plot(two_d_array, column_name, file, pixelsize, cmap_desire, cbar_limits):
    if "unnamed" in column_name.lower():
        return None
    else:
        fig, ax = plt.subplots(dpi=DPI)
        im = plt.imshow(two_d_array,
                   extent=[0, two_d_array.shape[1] * pixelsize,
                           two_d_array.shape[0] * pixelsize, 0],
                   cmap=cmap_desire
                   )
        plt.xlabel(XLABEL, fontsize=FONTSIZE_LABELS)
        plt.ylabel(YLABEL, fontsize=FONTSIZE_LABELS)
        ax.tick_params(axis='both', labelsize=FONTSIZE_TICKS)
        ax.xaxis.set_label_position('top')
        ax.xaxis.tick_top()
        cbar = plt.colorbar(im, ax=ax, anchor=(0,1), shrink=SHRINK)
        cbar.ax.tick_params(labelsize=FONTSIZE_TICKS)
        if column_name.lower() == 'scan_number':
            cbar.set_label(label=r"Scan Number", size=FONTSIZE_LABELS)
        elif column_name.lower() == 'r_wp':
            cbar.set_label(label=r"$r_{\mathrm{wp}}$", size=FONTSIZE_LABELS)
        elif column_name.lower() == 'scale_total':
            cbar.set_label(label=r"Scale Total", size=FONTSIZE_LABELS)
        elif column_name.lower() == 'scale_lfp':
            cbar.set_label(label=r"Scale LFP", size=FONTSIZE_LABELS)
        elif column_name.lower() == 'lp1_a':
            cbar.set_label(label=r"$a_{1}$ $[\mathrm{\AA}]$", size=FONTSIZE_LABELS)
        elif column_name.lower() == 'lp1_b':
            cbar.set_label(label=r"$b_{1}$ $[\mathrm{\AA}]$", size=FONTSIZE_LABELS)
        elif column_name.lower() == 'lp1_c':
            cbar.set_label(label=r"$c_{1}$ $[\mathrm{\AA}]$", size=FONTSIZE_LABELS)
        elif column_name.lower() == 'rbragg_1':
            cbar.set_label(label=r"$r_{\mathrm{Bragg,1}}$", size=FONTSIZE_LABELS)
        elif column_name.lower() == 'wp_1':
            cbar.set_label(label=r"$wp_{1}$", size=FONTSIZE_LABELS)
        elif column_name.lower() == 'lp2_a':
            cbar.set_label(label=r"$a_{2}$ $[\mathrm{\AA}]$", size=FONTSIZE_LABELS)
        elif column_name.lower() == 'lp2_b':
            cbar.set_label(label=r"$b_{2}$ $[\mathrm{\AA}]$", size=FONTSIZE_LABELS)
        elif column_name.lower() == 'lp2_c':
            cbar.set_label(label=r"$c_{2}$ $[\mathrm{\AA}]$", size=FONTSIZE_LABELS)
        elif column_name.lower() == 'rbragg_2':
            cbar.set_label(label=r"$r_{\mathrm{Bragg,2}}$", size=FONTSIZE_LABELS)
        elif column_name.lower() == 'wp_2':
            cbar.set_label(label=r"$wp_{2}$", size=FONTSIZE_LABELS)
        else:
            plt.colorbar(label=column_name)
        if not isinstance(cbar_limits, type(None)):
            cbar_min, cbar_max = float(cbar_limits.split(",")[0]), float(cbar_limits.split(",")[1])
            plt.clim(cbar_min, cbar_max)
            plt.savefig(f"{file.stem}/png/{file.stem}_{column_name}_{cbar_min}-{cbar_max}.png", bbox_inches='tight')
            plt.savefig(f"{file.stem}/pdf/{file.stem}_{column_name}_{cbar_min}-{cbar_max}.pdf", bbox_inches='tight')
        else:
            cbar.ax.ticklabel_format(style="sci", scilimits=(0,0))
            plt.savefig(f"{file.stem}/png/{file.stem}_{column_name}.png", bbox_inches='tight')
            plt.savefig(f"{file.stem}/pdf/{file.stem}_{column_name}.pdf", bbox_inches='tight')
        plt.close()

    return None


def main():
    if not (Path.cwd() / 'data').exists():
        (Path.cwd() / 'data').mkdir()
        print(f"{90*'-'}\nPlease place your data in the data folder and rerun the code.\
                \n{90*'-'}")
        sys.exit()
    files = list((Path.cwd() / 'data').glob(f"*.*"))
    if len(files) == 0:
        print(f"{90*'-'}\nPlease place your {FILEEXT} files in the data and rerun the code.\
                \n{90*'-'}")
        sys.exit()
    print(f"{90*'-'}")
    if not (Path.cwd() / 'delimiter_fix').exists():
        (Path.cwd() / 'delimiter_fix').mkdir()
    for file in files:
        if not (Path.cwd() / f"{file.stem}").exists():
            (Path.cwd() / f"{file.stem}").mkdir()
        folders = ['txt', 'png', 'pdf']
        for folder in folders:
            if not ((Path.cwd() / f"{file.stem}") / folder).exists():
                ((Path.cwd() / f"{file.stem}") / folder).mkdir()
        delimiter_fix(file)
    files = list((Path.cwd() / 'delimiter_fix').glob(f"*.*"))
    for file in files:
        plot_default, cmap_desire = one_to_two_d(file)
    print(f"Done with all files.\nWell done! (^^,)\n{90*'-'}")

    return None


if __name__ == '__main__':
    main()

# End of file.
