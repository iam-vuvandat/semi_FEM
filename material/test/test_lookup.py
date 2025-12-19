import sys
import os
import paths

def test():
    from material.core.lookup_BH_curve import lookup_BH_curve
    from material.models.MaterialDataBase import MaterialDataBase

    material_database = MaterialDataBase()

    data_out = lookup_BH_curve(
        B_input=0, 
        material_database=material_database
    )

    print(f"Mu_r       : {data_out.mu_r}")
    print(f"dMu_r/dB   : {data_out.dmu_r_dB}")

if __name__ == "__main__":
    
    current_file = os.path.abspath(__file__)
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

    if root_dir not in sys.path:
        sys.path.append(root_dir)
    
    test()
