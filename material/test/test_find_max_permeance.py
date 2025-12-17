import sys
import os

def test():
    from material.utils.find_maximum_permeance import find_maximum_permeance
    from material.models.MaterialDataBase import MaterialDataBase

    material_database = MaterialDataBase()
    data_out = find_maximum_permeance(material_database=material_database)
    print(data_out.B_at_max,data_out.H_at_max,data_out.mu_r_max)
    

if __name__ == "__main__":
    current_file = os.path.abspath(__file__)
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

    if root_dir not in sys.path:
        sys.path.append(root_dir)
    
    test()
