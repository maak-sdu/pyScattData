# Import section
import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy import constants
import Dans_Diffraction as dif
from skbeam.core.utils import twotheta_to_q

# Input section

# Diffraction inputs
wavelengths = dict(Ag = 0.5994,
                   Cu = 1.5406,
                   Mo = 1.7902,
                   Fe = 1.9373,
                   APS201903 = 0.2113,
                   PETRA201907 = 0.20721,
                   PETRA201909 = 0.20736,
                   PETRA201912 = 0.20712,
                   PETRA202006 = 0.20696)

WAVELENGTH = wavelengths['PETRA201907']
TWOTHETAMIN = 0
TWOTHETAMAX = 15
PEAKWIDTH = 0.01

# Plot inputs
DPI = 300
FIGSIZE = (12,4)
COLOR = "#0B3C5D"
LINEWIDTH = 0.5

# Data section
def wavelength_angstrom_to_energy_kev(wavelength):
    e_j = constants.Planck * constants.speed_of_light / (WAVELENGTH * 10**-10)
    e_ev = e_j / constants.elementary_charge
    e_kev = e_ev * 10**-3

    return e_kev
    # End of function.

def powder_pattern_simulator(cif, e_kev):
    xtl = dif.Crystal(cif)
    xtl.Scatter._scattering_min_twotheta = TWOTHETAMIN
    xtl.Scatter._scattering_max_twotheta = TWOTHETAMAX
    xtl.Plot.simulate_powder(energy_kev=e_kev, peak_width=PEAKWIDTH)
    # plt.show()
    data = plt.gca().get_lines()[0].get_xydata()
    plt.close()
    tt = data[:,0]
    int_calc = data[:,1]
    int_scaled = int_calc / np.amax(int_calc)
    q = twotheta_to_q(np.radians(tt), WAVELENGTH)
    np.savetxt(f'txt/iq/{cif.stem}.txt',
               np.column_stack((q, int_scaled)),
               fmt='%.6e',
               delimiter='\t',
               newline='\n',
               header='Q [Å^-1]\tI_scaled [a.u.]')
    np.savetxt(f'txt/itwotheta/{cif.stem}.txt',
               np.column_stack((tt, int_scaled)),
               fmt='%.6e',
               delimiter='\t',
               newline='\n',
               header=f'2theta [deg]\tI_scaled [a.u.]\tWavelength = {WAVELENGTH} Å')
    plt.figure(dpi=DPI, figsize=FIGSIZE)
    plt.plot(q, int_scaled, lw=LINEWIDTH, c=COLOR)
    plt.xlabel(r'$Q$ $[\mathrm{\AA}^{-1}]$')
    plt.ylabel(r'$I$ $[\mathrm{a.u.}]$')
    plt.xlim(np.amin(q), np.amax(q))
    plt.savefig(f'png/iq/{cif.stem}.png', bbox_inches='tight')
    plt.close()
    plt.figure(dpi=DPI, figsize=FIGSIZE)
    plt.plot(tt, int_scaled, lw=LINEWIDTH, c=COLOR)
    plt.xlabel(r'$2\theta$ $[\degree]$')
    plt.ylabel(r'$I$ $[\mathrm{a.u.}]$')
    plt.xlim(np.amin(tt), np.amax(tt))
    lambda_str = fr'$\lambda={WAVELENGTH}'
    lambda_str += r'\;\mathrm{\AA}$'
    plt.text(np.amin(tt), 1.075*np.amax(int_scaled), s=lambda_str)
    plt.savefig(f'png/itwotheta/{cif.stem}.png', bbox_inches='tight')
    plt.close()

    return None
    # End of function.

def main():
    cwd = Path.cwd()
    cifdir = cwd / 'cif'
    pngdir = cwd / 'png'
    pngittdir = pngdir / 'itwotheta'
    pngiqdir = pngdir / 'iq'
    txtdir = cwd / 'txt'
    txtittdir = txtdir / 'itwotheta'
    txtiqdir = txtdir / 'iq'
    folders = [pngdir, txtdir, pngittdir, pngiqdir, txtittdir, txtiqdir]
    for folder in folders:
        if not folder.is_dir():
            folder.mkdir()
    cifdir = Path.cwd() / 'cif'
    if not cifdir.exists():
        cifdir.mkdir()
        print(f"A folder called 'cif' has been made.\
                Plese place your .cif files in here and rerun the code.")
        sys.exit()
    ciffiles = cifdir.glob('*.cif')
    e_kev = wavelength_angstrom_to_energy_kev(WAVELENGTH)
    print(f"{90*'-'}\nSimulating diffraction patterns for...")
    for cif in ciffiles:
        print(f'\t{cif.name}')
        powder_pattern_simulator(cif, e_kev)
    print(f"Done simulating diffraction patterns.\
            \nPlots and textfiles have been saved to the png and txt directories.\
            \n{90*'-'}")
    return None
    # End of function.

if __name__ == '__main__':
    main()

# End of file.
