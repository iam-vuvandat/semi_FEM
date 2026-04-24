import numpy as np 
import matplotlib.pyplot as plt
from src.core.solver.utils.get_waveform_nrmse import get_waveform_nrmse
from types import SimpleNamespace

def plot_back_emf(data_processor, horizontal_axis = "mechanical_position", 
                     show_fem = True, show_all_phases = False, plot = False):
    
    motor = data_processor.motor
    record = motor.record
    n_phase = motor.winding_data.phase
    s = data_processor.plot_style
    shaft_speed = (motor.mechanical_data.shaft_speed * np.pi * 2) / 60 

    def get_x_axis(theta_data):
        if horizontal_axis == "time":
            return theta_data / shaft_speed, r'Time ($s$)'
        else:
            return theta_data, r'Rotor Position ($rad$)'

    has_sf = hasattr(record, "back_emf")
    has_fem = hasattr(record, "back_emf_fem")
    
    if plot:
        fig, ax = plt.subplots(figsize=(16, 10))
        x_label = ""
        phase_indices = range(n_phase) if show_all_phases else [0]

        if has_fem and show_fem:
            data_fem = record.back_emf_fem
            x_fem, x_label = get_x_axis(record.flux_linkage_fem[-1, :])
            for i in phase_indices:
                color = s.phase_colors[i % 3] if n_phase == 3 else s.colors[i % len(s.colors)]
                ax.plot(x_fem, data_fem[i, :], color=color, linestyle='--', alpha=0.6, label=f'Phase {chr(65+i)} (FEM)')

        if has_sf:
            data_sf = record.back_emf
            x_sf, x_label = get_x_axis(record.flux_linkage[-1, :])
            for i in phase_indices:
                color = s.phase_colors[i % 3] if n_phase == 3 else s.colors[i % len(s.colors)]
                ax.plot(x_sf, data_sf[i, :], color=color, label=f'Phase {chr(65+i)} (SF)', linewidth=2.0)

        ax.set_xlabel(x_label, fontsize=s.label_size)
        ax.set_ylabel(r'Back EMF ($V$)', fontsize=s.label_size)
        ax.legend(frameon=True, loc='best', ncol=2)
        ax.grid(True, linestyle='-', linewidth=s.grid_linewidth)
        plt.tight_layout()
        plt.show()