import sys
from pathlib import Path
import fabio
import numpy as np
import matplotlib.pyplot as plt


def npy_to_tif(npy, tif_path):
    npy_inv = np.load(npy)
    for j in range(npy_inv.shape[0]):
        for k in range(npy_inv.shape[1]):
            if npy_inv[j][k] == 0:
                npy_inv[j][k] = 1
            elif npy_inv[j][k] == 1:
                npy_inv[j][k] = -1
    img = fabio.open(npy)
    img.data = npy_inv
    img.convert("tif").save(tif_path / f"{npy.stem}.tif")

    return None


def main():
    npy_path, tif_path = Path.cwd() / "npy", Path.cwd() / "tif"
    if not npy_path.exists():
        npy_path.mkdir()
        print(f"{80*'-'}\n{npy_path.name} folder created.\n{80*'-'}")
        sys.exit()
    npy_files = list(npy_path.glob("*.npy"))
    if len(npy_files) == 0:
        print(f"{80*'-'}\nlen(npy_files) == 0\n{80*'-'}")
        sys.exit()
    if not tif_path.exists():
        tif_path.mkdir()
    print(f"{80*'-'}\nInverting .npy masks and saving to .tif files...")
    for npy in npy_files:
        print(f"\t{npy.name}")
        npy_to_tif(npy, tif_path)
    print(f"Done inverting .npy masks and saving to tifs.\n{80*'-'}")

    return None


if __name__ == "__main__":
    main()


# End of file.
