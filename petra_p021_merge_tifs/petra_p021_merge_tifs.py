import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import fabio
import matplotlib.pyplot as plt


DPI = 300
CMAP = "viridis"


def dict_basename_cyclenumber_sort(tifs, filename_syntax):
    d = {}
    for tif in tifs:
        tifname = tif.stem
        if filename_syntax == "cyclenumber":
            basename_split = tifname.split("_")
        elif filename_syntax == "basename":
            basename_split = tifname.split("-")
        basename = basename_split[0]
        for i in range(1, len(basename_split)-1):
            basename += f"_{basename_split[i]}"
        try:
            d[basename]
        except KeyError:
            d[basename] = defaultdict(list)
        if filename_syntax == "cyclenumber":
            cycle_number = tifname.split("-")[0].split("_")[-1]
            d[basename][cycle_number].append(tif)
        elif filename_syntax == "basename":
            d[basename]["0"].append(tif)

    return d


def tif_merge_log(d_tif, filename_syntax, subframes_exp, output_path):
    d_merged = {}
    dt = str(datetime.now()).split("-")
    y, m, d_h_min_s = dt[0][2:], dt[1], dt[2].split()
    d, h_min_s= d_h_min_s[0], d_h_min_s[1].split(":")
    h, min, s = h_min_s[0], h_min_s[1], h_min_s[2][0:2]
    log_path = output_path / f"{Path(__file__).stem}_{y}{m}{d}-{h}{min}{s}.log"
    log = (f"{Path(__file__).name} log\n\nExpected number of subframes: "
          f"{subframes_exp}\n\nBelow, the basenames, cycle numbers, and "
          f"filenames are stated for all merged\n.tif files, where the number "
          f"of files merged does not equal the number of\nexpected subframes. "
          f"If whole cycle numbers (all subframes) are missing, this\nwill "
          f"also be reported.")
    with log_path.open(mode="w", encoding="utf-8") as o:
        o.write(log)
    for basename in d_tif.keys():
        print(f"{80*'-'}\nBasename: {basename}")
        output_path_tif_stack = output_path / basename
        d_merged[basename] = {}
        cycle_numbers = sorted([int(k) for k in d_tif[basename].keys()])
        cycle_numbers_missing = []
        with log_path.open(mode="a", encoding="utf-8") as o:
            o.write(f"\n\nBasename: {basename}")
        for cycle_number in cycle_numbers:
            print(f"\nCycle number: {cycle_number}")
            tifs = d_tif[basename][str(cycle_number)]
            for i in range(len(tifs)):
                print(tifs[i].name)
                tifname = tifs[i].stem
                seq_number = tifname.split("-")[-1]
                if i == 0:
                    tif_stack = fabio.open(tifs[i])
                    tif_array = tif_stack.data
                    start = seq_number
                else:
                    tif_array += fabio.open(tifs[i]).data
                if i == len(tifs)-1:
                    end = seq_number
            output_name = f"{basename}_{cycle_number}_{start}-{end}.tif"
            d_merged[basename][cycle_number] = dict(tif=tif_array,
                                                    name=output_name)
            tif_stack.data = tif_array
            tif_stack.write(output_path_tif_stack / output_name)
            log_cycles = None
            if int(end) - int(start) != subframes_exp - 1:
                log_cycles = f"\n\tCycle number: {cycle_number}"
                for tif in tifs:
                    log_cycles += f"\n\t\t{tif.name}"
        if isinstance(log_cycles, str):
            with log_path.open(mode="a", encoding="utf-8") as o:
                o.write(log_cycles)
        cycle_numbers = sorted(cycle_numbers)
        for i in range(1, len(cycle_numbers)):
            difference = int(cycle_numbers[i]) - int(cycle_numbers[i-1])
            if difference != 1:
                for j in range(1, difference):
                    cycle_numbers_missing.append(f"{int(cycle_numbers[i-1])+j}")
        if len(cycle_numbers_missing) != 0:
            log_cycles_missing = "\n\tMissing cycle numbers:"
            for e in cycle_numbers_missing:
                log_cycles_missing += f"\n\t\t{basename}_{e}.tif"
            with log_path.open(mode="a", encoding="utf-8") as o:
                o.write(log_cycles_missing)

    return d_merged


def tif_plot(d_merged, output_path):
    for basename in d_merged.keys():
        png_path = output_path / basename / "png"
        if not png_path.exists():
            png_path.mkdir()
        print(f"Basename: {basename}")
        for cycle_number in d_merged[basename].keys():
            tif = d_merged[basename][cycle_number]["tif"]
            name = d_merged[basename][cycle_number]["name"]
            print(f"\t{name}")
            data = tif
            plt.figure(dpi=DPI)
            plt.imshow(data, cmap=CMAP)
            plt.colorbar()
            plt.savefig(f"{png_path}/{name.split('.')[0]}.png",
                        bbox_inches="tight")
            plt.close()

    return None


def main():
    print(f"{80*'-'}\nPlease remove 'junk' .tif files from the input "
          f"directory before running the code\nto ensure that .tif files are "
          f"properly merged.")
    input_path = input(f"{80*'-'}\nPlease provide the absolute path to the "
                       f"directory of the input files.\n(You can just copy "
                       f"and paste from the file explorer.)\nInput path: ")
    while not Path(input_path).exists():
        input_path = input(f"\nThe input path provided does not exists. Please "
                           f"review the input path provided\nand resubmit:\n"
                           f"Input path: ")
    output_path = input(f"{80*'-'}\nPlease provide the absolute path to the "
                       f"directory of the output files.\n(You can just copy "
                       f"and paste from the file explorer.)\nOutput path: ")
    while not Path(output_path).exists():
        output_path = input(f"\nThe output path provided does not exists. "
                           f"Please review the output path provided\nand "
                           f"resubmit:\nOutput path: ")
    input_path, output_path = Path(input_path), Path(output_path)
    print(f"{80*'-'}\Filename syntax:\n\t1\tbasename_cyclenumber-"
          f"sequentialnumber\n\t2\tbasename-sequentialnumber")
    filename_syntax = input("Please provide the filename syntax: ")
    while filename_syntax not in ["1", "2"]:
        filename_syntax = input("Please provide the filename syntax: ")
    if filename_syntax == "1":
        filename_syntax = "cyclenumber"
    elif filename_syntax == "2":
        filename_syntax = "basename"
    subframes_exp = int(input(f"{80*'-'}\nPlease provide the expected number "
                              f"of subframes to merge: "))
    plotreq = input(f"{80*'-'}\nDo you want to plot all merged tifs? (y/n): ")
    while plotreq.lower() not in ["y", "n"]:
        plotreq = input(f"Do you want to plot all merged tifs? (y/n): ")
    print(f"{80*'-'}\nCollecting .tif files from the current directory, while "
          f"ignoring darks...")
    tif_w_darks = list(input_path.glob("*.tif"))
    tifs = [tif_w_darks[i] for i in range(len(tif_w_darks))
            if not "dark" in tif_w_darks[i].stem]
    print(".tif files collected.")
    if filename_syntax == "1":
        print(f"\n{80*'-'}\nSorting .tif files in dictionary according to "
              f"basename and cycle number...")
    elif filename_syntax == "2":
        print(f"\n{80*'-'}\nSorting .tif files in dictionary according to "
              f"basename...")
    d = dict_basename_cyclenumber_sort(tifs, filename_syntax)
    if not (output_path / "tif_sum").exists():
        (output_path / "tif_sum").mkdir()
    output_path = output_path / "tif_sum"
    for basename in d.keys():
        if not (output_path / basename).exists():
            (output_path / basename).mkdir()
    print(f"Done sorting .tif files.\n{80*'-'}\nMerging tifs and preparing "
          f"dictionary for plotting...")
    d_merged = tif_merge_log(d, filename_syntax, subframes_exp, output_path)
    print(f"{80*'-'}\nDone merging. Please see merged .tif files in the "
          f"'tif_sum' folder created in\nthe provided output directory."
          f"\n{80*'-'}\nPlease review the .log file in the output dorectory to "
          f"see merging notes like\nmissing scans, etc.")
    if plotreq.lower() == "y":
        print(f"{80*'-'}\nPlotting merged .tif files...")
        tif_plot(d_merged, output_path)
        print(f"Done plotting. Please see the 'png' folders, created for each "
              f"basename in the\noutput directory.")
    print(f"{80*'-'}\nDone working with .tif files. <(^^,)>")

    return None


if __name__ == "__main__":
    main()


# End of file.
