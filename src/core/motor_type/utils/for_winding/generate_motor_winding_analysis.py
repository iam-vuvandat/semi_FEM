import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Any, Optional
from swat_em.datamodel import datamodel

@dataclass
class Output:
    is_valid: bool
    winding_matrix: np.ndarray
    tooth_matrix: np.ndarray
    fig_polar: Any = None
    fig_mmf: Any = None
    fig_star: Any = None

def get_tooth_matrix(wdg, w):
    Q = wdg.get_num_slots()
    m = wdg.get_num_phases()
    phases = wdg.get_phases()
    
    winding_matrix = np.zeros((m, Q))
    for p_idx in range(m):
        for layer in phases[p_idx]:
            for slot in layer:
                slot_idx = abs(slot) - 1
                direction = 1 if slot > 0 else -1
                winding_matrix[p_idx, slot_idx] += direction
    
    tooth_matrix = np.zeros((m, Q))
    for p_idx in range(m):
        row = winding_matrix[p_idx]
        pos_indices = np.where(row > 0)[0]
        
        for i_in in pos_indices:
            val_in = row[i_in]
            idx_r = (i_in + w) % Q
            if row[idx_r] < 0:
                mag = min(val_in, abs(row[idx_r]))
                for step in range(w):
                    t_idx = (i_in + step) % Q
                    tooth_matrix[p_idx, t_idx] += mag
            
            idx_l = (i_in - w) % Q
            if row[idx_l] < 0:
                mag = min(val_in, abs(row[idx_l]))
                for step in range(w):
                    t_idx = (idx_l + step) % Q
                    tooth_matrix[p_idx, t_idx] -= mag
                    
    return winding_matrix, tooth_matrix

def generate_motor_winding_analysis(motor, debug=False) -> Output:
    Q = motor.geometry_data.stator.slot_number
    P = motor.geometry_data.rotor.pole_number
    w = motor.winding_data.throw
    layers = motor.winding_data.winding_layer
    m = 3 
    res = [2000, 2000]

    wdg = datamodel()
    wdg.set_machinedata(Q=Q, p=P//2, m=m)
    wdg.set_coilspan(w)
    
    manual_phases = []
    slots_per_phase = Q // m
    for ph in range(m):
        l1 = []
        l2 = []
        for c in range(slots_per_phase):
            start = int((ph + c * m) % Q + 1)
            end = int((start + w - 1) % Q + 1)
            if layers == 1:
                l1.extend([start, -end])
            else:
                l1.append(start)
                l2.append(-end)
        manual_phases.append([l1, l2])
        
    wdg.set_phases(manual_phases, w=w)
    wdg.analyse_wdg()

    is_symmetric = wdg.get_is_symmetric()
    winding_matrix, tooth_matrix = get_tooth_matrix(wdg, w)
    
    output_data = Output(
        is_valid=is_symmetric,
        winding_matrix=winding_matrix,
        tooth_matrix=tooth_matrix
    )

    if debug:
        print("--- DEBUG MODE ---")
        print(f"Symmetry: {is_symmetric}")
        print("Winding Matrix:\n", winding_matrix)
        print("Tooth Matrix:\n", tooth_matrix)
        
        # Luu file va hien thi cua so tuong tac
        output_data.fig_polar = wdg.plot_polar_layout(filename='debug_polar.png', res=res, optimize_overhang=False, draw_poles=True, show=True)
        output_data.fig_mmf = wdg.plot_MMK(filename='debug_mmf.png', res=res, phase=0, show=True)
        output_data.fig_star = wdg.plot_star(filename='debug_star.png', res=res, ForceX=True, show=True)

    return output_data

if __name__ == "__main__":
    class Stator:
        def __init__(self): self.slot_number = 15
    class Rotor:
        def __init__(self): self.pole_number = 10
    class GeometryData:
        def __init__(self):
            self.stator = Stator()
            self.rotor = Rotor()
    class WindingData:
        def __init__(self):
            self.throw = 5
            self.winding_layer = 2
    class Motor:
        def __init__(self):
            self.geometry_data = GeometryData()
            self.winding_data = WindingData()

    my_motor = Motor()
    result = generate_motor_winding_analysis(my_motor, debug=True)
    print(f"Symmetry Result: {result.is_valid}")