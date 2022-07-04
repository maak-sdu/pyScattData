import sys
from pathlib import Path
# import hdf5plugin
import h5py
import fabio
import numpy as np


def h5_tif_extract(h5, output_folder):
    f = h5py.File(h5, "r")
    keys = list(f.keys())
    for k in keys:
        print(f"\t\t{k}")
        data = np.array(f[k]["measurement"]["pilatus"])
        mean = np.mean(data, axis=0)
        image = fabio.numpyimage.NumpyImage(data=mean, header=None)
        image.convert("tif").save(f"{output_folder}/{k}.tif")

    return None


def main():
    cwd_content = list(Path.cwd().glob("*"))
    folders = [e for e in cwd_content if e.is_dir()]
    print(f"{80*'-'}\n{Path(__file__).name}:\nFor extracting .tif files from "
          f".h5 master files from DanMAX.\n{80*'-'}\nThe following folders "
          f"were found:")
    for folder in folders:
        print(f"\t{folder.name}")
    user_req = input(f"{80*'-'}\nDo you want to extract .tif files from the "
                     f"master.h5 files in these folders?\n([y]/n): ")
    if not user_req.lower() in ["", "y"]:
        print(f"{80*'-'}\nExiting program.")
        sys.exit()
    for folder in folders:
        output_folder = folder / "tif"
        if not output_folder.exists():
            output_folder.mkdir()
        h5_files = list(folder.glob("*.h5"))
        h5_master = [h5 for h5 in h5_files if not "pilatus" in h5.stem][0]
        print(f"{80*'-'}\n{folder.name}\n\t{h5_master.name}")
        try:
            h5_tif_extract(h5_master, output_folder)
        except KeyError:
            break
    print(f"{80*'-'}\nDone extracting .tif files.\nPlease see the 'tif' folder "
          f"that has been created in each folder containing .h5\nfiles.")

    return None


if __name__ == "__main__":
    main()

# End of file
