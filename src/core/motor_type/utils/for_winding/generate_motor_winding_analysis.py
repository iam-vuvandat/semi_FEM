import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Any, Dict, List
from swat_em.datamodel import datamodel

@dataclass
class Output:
    is_valid: bool
    winding_matrix: np.ndarray
    tooth_matrix: np.ndarray
    q: Any
    p: int
    m: int
    w: int
    num_layers: int
    kw_fundamental: List[float]
    periodicity_t: int
    parallel_connections: List[int]
    radial_force_modes: List[int]
    double_linked_leakage: float
    lcmQP: int
    nu_el: np.ndarray
    kw_el: np.ndarray
    nu_mmf: np.ndarray
    c_nu_mmf: np.ndarray
    fig_layout: Any = None
    fig_polar: Any = None
    fig_star: Any = None
    fig_mmk: Any = None
    fig_wf: Any = None

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
    m = motor.winding_data.phase
    N = motor.winding_data.turns
    res = [2000, 2000]

    wdg = datamodel()
    wdg.set_machinedata(Q=Q, p=P//2, m=m)
    wdg.set_coilspan(w)
    
    manual_phases = []
    for ph in range(m):
        l1, l2 = [], []
        for slot_idx in range(Q):
            if slot_idx % m == ph:
                start = slot_idx + 1
                end = (slot_idx + w) % Q + 1
                if layers == 1:
                    l1.extend([int(start), int(-end)])
                else:
                    l1.append(int(start))
                    l2.append(int(-end))
        manual_phases.append([l1, l2])
        
    wdg.set_phases(manual_phases, w=w)
    wdg.analyse_wdg()

    winding_raw, tooth_raw = get_tooth_matrix(wdg, w)
    winding_raw *= N
    tooth_raw *= N

    nu_mmf, c_nu_mmf, _ = wdg.get_MMF_harmonics()
    nu_el, kw_el = wdg.get_windingfactor_el()

    output_data = Output(
        is_valid=wdg.get_is_symmetric(),
        winding_matrix=winding_raw.T,
        tooth_matrix=tooth_raw.T,
        q=wdg.get_q(),
        p=wdg.get_num_polepairs(),
        m=wdg.get_num_phases(),
        w=wdg.get_coilspan(),
        num_layers=wdg.get_num_layers(),
        kw_fundamental=wdg.get_fundamental_windingfactor(),
        periodicity_t=wdg.get_periodicity_t(),
        parallel_connections=wdg.get_parallel_connections(),
        radial_force_modes=wdg.get_radial_force_modes(),
        double_linked_leakage=wdg.get_double_linked_leakage(),
        lcmQP=wdg.get_lcmQP(),
        nu_el=nu_el,
        kw_el=kw_el,
        nu_mmf=nu_mmf,
        c_nu_mmf=c_nu_mmf
    )

    if debug:
        print("--- DEBUG: FULL DATA EXPLOITATION ---")
        print(f"Symmetry: {output_data.is_valid}")
        print(f"Fundamental Winding Factor: {output_data.kw_fundamental}")
        print(f"Radial Force Modes: {output_data.radial_force_modes}")
        print(f"Lcm(Q,P) for Cogging Torque: {output_data.lcmQP}")
        print(f"Winding Matrix (Slot x Phase):\n{output_data.winding_matrix}")
        print(f"Tooth Matrix (Slot x Phase):\n{output_data.tooth_matrix}")
        
        output_data.fig_layout = wdg.plot_layout(filename='debug_layout.png', res=res, show=True)
        output_data.fig_polar = wdg.plot_polar_layout(filename='debug_polar.png', res=res, draw_poles=True, show=True)
        output_data.fig_star = wdg.plot_star(filename='debug_star.png', res=res, ForceX=True, show=True)
        output_data.fig_mmk = wdg.plot_MMK(filename='debug_mmf.png', res=res, phase=0, show=True)
        output_data.fig_wf = wdg.plot_windingfactor(filename='debug_wf.png', res=res, mechanical=False, show=True)

    return output_data

if __name__ == "__main__":
    class MockMotor:
        def __init__(self):
            self.geometry_data = type('obj', (), {'stator': type('obj', (), {'slot_number': 15}), 
                                                 'rotor': type('obj', (), {'pole_number': 10})})()
            self.winding_data = type('obj', (), {'throw': 2, 'winding_layer': 2, 'phase': 3, 'turns' : 10})()
    
    result = generate_motor_winding_analysis(MockMotor(), debug=True)