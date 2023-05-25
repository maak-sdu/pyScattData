import sys
from pathlib import Path
import json
from diffpy.structure import loadStructure
from diffpy.srreal.bondcalculator import BondCalculator

RMIN, RMAX = 1, 10

def bond_distances_to_dict(cif, rmin=1, rmax=10):
    stru = loadStructure(str(cif))
    bc = BondCalculator(rmin=rmin, rmax=rmax)
    bc(stru)
    d = dict(distances=bc.distances, types0=bc.types0, types1=bc.types1)

    return d


def sort_dict(d):
    distances, types0, types1 = d["distances"], d["types0"], d["types1"]
    d_sort = {}
    for i in range(len(distances)):
        dist, type0, type1 = distances[i], types0[i], types1[i]
        dist = f"{dist:.6f}"
        if not dist in d_sort.keys():
            d_sort[dist] = {}
            d_sort[dist]["pair"] = {}
            d_sort[dist]["pair"][f"{type0}, {type1}"] = 1
        else:
            if f"{type0}, {type1}" in d_sort[dist]["pair"].keys():
                d_sort[dist]["pair"][f"{type0}, {type1}"] += 1
            elif f"{type1}, {type0}" in d_sort[dist]["pair"].keys():
                d_sort[dist]["pair"][f"{type1}, {type0}"] += 1
            else:
                d_sort[dist]["pair"][f"{type0}, {type1}"] = 1

    return d_sort


def main():
    cif_path = Path.cwd() / "cif"
    if not cif_path.exists():
        cif_path.mkdir()
        sys.exit(f"{80*'-'}\nA folder called '{cif_path.name}' has been "
                 f"created.\nPlease put your .cif file(s) there and rerun the "
                 f"code.\n{80*'-'}")
    cif_files = list(cif_path.glob("*.cif"))
    txt_path = Path.cwd() / "txt"
    if not txt_path.exists():
        txt_path.mkdir()
    json_path = Path.cwd() / "json"
    if not json_path.exists():
        json_path.mkdir()
    print(f"{80*'-'}\nWorking w. cifs...")
    for cif in cif_files:
        print(f"\t{cif.name}")
        d = bond_distances_to_dict(cif, RMIN, RMAX)
        d_sort = sort_dict(d)
        output_json_path = json_path / f"{cif.stem}.json"
        with output_json_path.open(mode="w") as o:
            json.dump(d_sort, o, sort_keys=True, indent=4)
        s = ""
        for k in list(d_sort.keys()):
            s += f"{k}\t{d_sort[k]['pair']}\n"
        output_txt_path = txt_path / f"{cif.stem}.txt"
        with output_txt_path.open(mode="w") as o:
            o.write(s)
    output_folders = [json_path.name, txt_path.name]
    print(f"{80*'-'}\nDone working w. cifs. Please see the {output_folders} "
          f"folders.")

    return None


if __name__ == "__main__":
    main()

# End of file
