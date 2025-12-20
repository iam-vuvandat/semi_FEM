import sys
import os
import numpy as np
import matplotlib.pyplot as plt

def set_ieee_style():
    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Times New Roman', 'DejaVu Serif'],
        'font.size': 12,
        'axes.labelsize': 14,
        'axes.titlesize': 14,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'legend.fontsize': 12,
        'figure.titlesize': 16,
        'lines.linewidth': 1.5,
        'lines.markersize': 6,
        'axes.grid': True,
        'grid.alpha': 0.5,
        'grid.linestyle': '--',
        'grid.linewidth': 0.6,
        'mathtext.fontset': 'stix',
    })

def test():
    current_file = os.path.abspath(__file__)
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

    if root_dir not in sys.path:
        sys.path.append(root_dir)

    from material.core.lookup_BH_curve import lookup_BH_curve
    from material.models.MaterialDataBase import MaterialDataBase

    material_database = MaterialDataBase()
    B_input = np.linspace(-3.0, 3.0, 2000)

    data_out = lookup_BH_curve(
        B_input=B_input, 
        material_database=material_database,
        return_du_dB=True,
        invert=False
    )

    set_ieee_style()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8), sharex=True, constrained_layout=True)

    ax1.plot(B_input, data_out.mu_r, color='#004488', label=r'$\mu_r$ Curve')
    ax1.set_ylabel(r'Relative Permeability, $\mu_r$')
    ax1.set_title(r'Relative Permeability ($\mu_r$) vs. Flux Density ($B$)', pad=10)

    ax2.plot(B_input, data_out.dmu_r_dB, color='#AA0000', label=r'$d\mu_r/dB$ Curve')
    ax2.set_ylabel(r'Derivative, $d\mu_r/dB$ (T$^{-1}$)')
    ax2.set_xlabel(r'Magnetic Flux Density, $B$ (T)')
    ax2.set_title(r'Derivative of Permeability ($d\mu_r/dB$)', pad=10)
    
    ax2.set_xlim([B_input.min(), B_input.max()])

    ax1.legend(loc='upper right', framealpha=0.9, edgecolor='gray')
    ax2.legend(loc='upper right', framealpha=0.9, edgecolor='gray')

    plt.show()

if __name__ == "__main__":
    test()