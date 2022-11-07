import sys
from pathlib import Path
import pandas as pd
import numpy as np


def comp_extract(compfile, output_path):
    df = pd.read_csv(compfile)
    xcomps = [df[col].to_numpy() for col in df.columns if "Unnamed" in col][0]
    compnames = np.array([int(col)+1 for col in df.columns if not "Unnamed" in col])
    comps = [df[f"{col-1}"].to_numpy() for col in compnames]
    for i in range(len(comps)):
        np.savetxt(output_path / f"nmf_comp_{i+1}.{output_path.name}",
                   np.column_stack((xcomps, comps[i])),
                   fmt="%.6f",
                   delimiter="\t",
                   )

    return None


def main():
    data_path = Path.cwd() / "data"
    file = list(data_path.glob("*.*"))[0]
    output_ext = input(f"{80*'-'}\nPlease provide the extension for the output "
                       f"file (e.g. '.gr'): ")
    output_path = Path.cwd()  / output_ext.strip(".")
    if not output_path.exists():
        output_path.mkdir()
    print(f"{80*'-'}\nExtracting components...")
    comp_extract(file, output_path)
    print(f"Done.\n{80*'-'}\nComponents have been extracted and written to "
          f"files in the '{output_path.name}' directory.")

    return None


if __name__ == "__main__":
    main()

# End of file
