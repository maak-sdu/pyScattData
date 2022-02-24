import sys
from pathlib import Path
import numpy as np
from diffpy.utils.parsers.loaddata import loadData


def fgr_res_to_gr(fgr_files):
    for fgr_file in fgr_files:
        print(f"\t{fgr_file.name}")
        with fgr_file.open(mode="r", encoding="utf-8") as f:
            data = loadData(f.name)
        r, g, gdiff = data[:,0], data[:,1], data[:,4]
        r_gdiff = np.column_stack((r,gdiff))
        np.savetxt(f"gr/{fgr_file.stem}.gr", r_gdiff, fmt='%.6f')

    return None


def main():
    cwd = Path.cwd()
    fgr_path = cwd / "fgr"
    gr_path = cwd / "gr"
    png_path = cwd / "png"
    pdf_path = cwd / "pdf"
    if not fgr_path.exists():
        fgr_path.mkdir()
        print(f"{'-'*80}\nA folder called 'fgr' has been created. Please place "
              f"your .fgr files there and\nrerun the code.\n{'-'*80}")
        sys.exit()
    fgr_files = list(fgr_path.glob("*.fgr"))
    if len(fgr_files) == 0:
        print(f"{'-'*80}\nNo .fgr files found in the 'fgr' folder. Please "
              f"place your .fgr files there and\nrerun the code.\n{'-'*80}")
        sys.exit()
    if not gr_path.exists():
        gr_path.mkdir()
    print(f"{80*'-'}\nWorking with .fgr files...")
    fgr_res_to_gr(fgr_files)
    print(f"Done working with .fgr files.\n{'-'*80}\nThe difference curves of "
          f"the .fgr files have been saved as .gr files to the 'gr'\ndirectory."
          f"\n{'-'*80}")

    return None


if __name__ == "__main__":
    main()

# End of file.
