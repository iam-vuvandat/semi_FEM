import os
import paths
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Any, Optional, List
from swat_em.datamodel import datamodel

@dataclass
class Output:
    is_valid: bool
    winding_matrix: np.ndarray
    tooth_matrix: np.ndarray
    fig_layout: Any = None
    fig_polar: Any = None
    fig_star: Any = None
    fig_mmf: Any = None
    fig_wf: Any = None
    fig_overhang: Any = None
    kw_fundamental: Optional[List[float]] = None
    lcmQP: Optional[int] = None
    periodicity_t: Optional[int] = None

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
    root_folder_path = paths.configure_path()
    figure_dir = os.path.join(root_folder_path, "data", "figure")
    if not os.path.exists(figure_dir):
        os.makedirs(figure_dir)

    Q = motor.geometry_data.stator.slot_number
    P = motor.geometry_data.rotor.pole_number
    w = motor.winding_data.throw
    layers = motor.winding_data.winding_layer
    m = 3 
    turns = getattr(motor.winding_data, 'turns', 1)
    res = [800, 800] 

    wdg = datamodel()
    wdg.set_machinedata(Q=Q, p=P//2, m=m)
    wdg.set_coilspan(w)
    
    manual_phases = []
    slots_per_phase = Q // m
    for ph in range(m):
        l1, l2 = [], []
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

    w_raw, t_raw = get_tooth_matrix(wdg, w)
    
    output_data = Output(
        is_valid=wdg.get_is_symmetric(),
        winding_matrix=(w_raw * turns).T,
        tooth_matrix=(t_raw * turns).T,
        kw_fundamental=wdg.get_fundamental_windingfactor(),
        lcmQP=wdg.get_lcmQP(),
        periodicity_t=wdg.get_periodicity_t()
    )

    output_data.fig_layout = wdg.plot_layout(filename=os.path.join(figure_dir, 'layout.png'), res=res, show=debug)
    output_data.fig_polar = wdg.plot_polar_layout(filename=os.path.join(figure_dir, 'polar.png'), res=res, draw_poles=True, show=debug)
    output_data.fig_star = wdg.plot_star(filename=os.path.join(figure_dir, 'star.png'), res=res, ForceX=True, show=debug)
    output_data.fig_mmf = wdg.plot_MMK(filename=os.path.join(figure_dir, 'mmf.png'), res=res, phase=0, show=debug)
    output_data.fig_wf = wdg.plot_windingfactor(filename=os.path.join(figure_dir, 'wf.png'), res=res, mechanical=False, show=debug)
    output_data.fig_overhang = wdg.plot_overhang(filename=os.path.join(figure_dir, 'overhang.png'), res=res, show=debug)

    if debug:
        print("\n" + "="*30)
        print("DEBUG: WINDING MATRICES (Slot x Phase)")
        print("-" * 30)
        print("1. WINDING MATRIX:")
        print(output_data.winding_matrix)
        print("\n2. TOOTH MATRIX:")
        print(output_data.tooth_matrix)
        print("="*30 + "\n")
        plt.show() 

    return output_data

if __name__ == "__main__":
    class Container:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    class MockMotor:
        def __init__(self):
            self.geometry_data = Container(stator=Container(slot_number=15), rotor=Container(pole_number=6))
            self.winding_data = Container(throw=7, winding_layer=2, turns=15)

    print("--- DANG CHAY TEST: DO THI SE HIEN RA VA LUU VAO DATA/FIGURE ---")
    result = generate_motor_winding_analysis(MockMotor(), debug=True)
    print(f"Ket qua doi xung: {result.is_valid}")