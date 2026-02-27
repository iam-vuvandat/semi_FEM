import numpy as np
import matplotlib.pyplot as plt
from swat_em.datamodel import datamodel

def get_tooth_matrix(wdg, w):
    Q = wdg.get_num_slots() # [cite: 1947]
    m = wdg.get_num_phases() # [cite: 1934]
    phases = wdg.get_phases() # [cite: 1969]
    
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

def test_forced_winding(Q, P, m, w, layers):
    res = [2000, 2000]
    wdg = datamodel()
    wdg.set_machinedata(Q=Q, p=P//2, m=m) # [cite: 2083, 2087]
    
    # Thiet lap buoc day noi bo cho datamodel [cite: 2080]
    wdg.set_coilspan(w) 
    
    manual_phases = []
    num_coils_per_phase = Q // m
    for ph in range(m):
        l1 = []
        l2 = []
        for c in range(num_coils_per_phase):
            start = int((ph + c * m) % Q + 1)
            end = int((start + w - 1) % Q + 1)
            
            if layers == 1:
                l1.extend([start, -end])
            else:
                l1.append(start)
                l2.append(-end)
        manual_phases.append([l1, l2])
        
    # Cap nhat tham so w vao set_phases 
    wdg.set_phases(manual_phases, w=w) 
    wdg.analyse_wdg() # [cite: 1851]

    winding_matrix, tooth_matrix = get_tooth_matrix(wdg, w)
    
    print(f"--- CONFIG: Q={Q}, P={P}, m={m}, w={w}, layers={layers} ---")
    print("Winding Matrix (Slot):")
    print(winding_matrix)
    print("\nTooth Matrix (Overlayed):")
    print(tooth_matrix)
    
    # Tat optimize_overhang de hien thi dung buoc day cuong buc 
    wdg.plot_polar_layout(filename=f'polar_L{layers}_w{w}.png', 
                          res=res, 
                          optimize_overhang=False, 
                          draw_poles=True, 
                          show=True)
    
    wdg.plot_MMK(filename=f'mmf_L{layers}_w{w}.png', res=res, phase=0, show=True) # [cite: 2028]
    wdg.plot_star(filename=f'star_L{layers}_w{w}.png', res=res, ForceX=True, show=True) # [cite: 2056]

if __name__ == "__main__":
    test_forced_winding(Q=20, P=10, m=3, w=2, layers=2)