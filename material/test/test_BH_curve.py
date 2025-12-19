import sys
import os
import numpy as np
import matplotlib.pyplot as plt

def test():
    from material.core.lookup_BH_curve import lookup_BH_curve
    from material.models.MaterialDataBase import MaterialDataBase

    material_database = MaterialDataBase()
    
    B_input = np.linspace(-3.0, 3.0, 1000)

    data_out = lookup_BH_curve(
        B_input=B_input, 
        material_database=material_database,
        return_du_dB=True,
        invert=False
    )

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    ax1.plot(B_input, data_out.mu_r)
    ax1.set_ylabel('mu_r')
    ax1.set_title('Mu_r vs B')
    ax1.grid(True)

    ax2.plot(B_input, data_out.dmu_r_dB)
    ax2.set_xlabel('B (T)')
    ax2.set_ylabel('dMu_r/dB')
    ax2.set_title('dMu_r/dB vs B')
    ax2.grid(True)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    current_file = os.path.abspath(__file__)
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

    if root_dir not in sys.path:
        sys.path.append(root_dir)
    
    test()