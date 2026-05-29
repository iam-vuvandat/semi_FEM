import os
import paths
import numpy as np 
import matplotlib.pyplot as plt

def plot_power_at_varying_current(data_processor, plot = False):
    
    # 1. Setup directories
    root_dir = paths.configure_path()
    figure_dir = os.path.join(root_dir, "data", "repo", "figures")
    if not os.path.exists(figure_dir):
        os.makedirs(figure_dir)

    # 2. Extract objects and styles
    motor = data_processor.motor
    record = motor.record
    s = data_processor.plot_style

    # Golden Ratio layout setup for individual figures
    fig_width = 14
    fig_height = fig_width / 1.618

    # 3. Data availability check
    has_data = hasattr(record, "power_at_varying_current") and record.power_at_varying_current is not None
    if not has_data:
        print("No power_at_varying_current data available for plotting.")
        return None

    current_array = record.power_at_varying_current
    stator_current_data = current_array[2]
    mbgrn_power_data = current_array[0]
    fem_power_data = current_array[1]

    # Calculate first derivative (dP/dI) using numerical gradient
    dP_dI_mbgrn = np.gradient(mbgrn_power_data, stator_current_data)
    dP_dI_fem = np.gradient(fem_power_data, stator_current_data)

    # Academic Color Palette
    color_fem = '#7F7F7F'  # Muted grey for FEM reference
    color_mrn = '#B22222'  # Deep crimson red for MBGRN proposed method

    # -------------------------------------------------------------------------
    # FIGURE 1: Mechanical Power vs Stator Current
    # -------------------------------------------------------------------------
    fig_power = plt.figure(figsize=(fig_width, fig_height))
    ax1 = plt.gca()

    label_fem_p = r'Mechanical Power (FEM)'
    label_mrn_p = r'Mechanical Power (MBGRN)'
    
    ax1.plot(stator_current_data, fem_power_data, color=color_fem, linestyle='-', marker='x', linewidth=1.5, 
             label=label_fem_p)
    ax1.plot(stator_current_data, mbgrn_power_data, color=color_mrn, linestyle='-', marker='o', linewidth=3.0, 
             label=label_mrn_p)
    
    # Calculate padding for Figure 1
    all_p_values = np.concatenate([fem_power_data, mbgrn_power_data])
    p_min, p_max = np.min(all_p_values), np.max(all_p_values)
    p_range = p_max - p_min if p_max - p_min != 0 else 1.0
    ax1.set_ylim(p_min - 0.15 * p_range, p_max + 0.15 * p_range)
    
    ax1.set_xlabel('Stator Current ($A$)', fontsize=s.label_size)
    ax1.set_ylabel('Mechanical Power ($W$)', fontsize=s.label_size)
    ax1.legend(frameon=True, loc='best', fontsize=s.legend_size)
    ax1.grid(True, which='major', linestyle='-', linewidth=s.grid_linewidth)
    ax1.margins(x=0)

    plt.tight_layout()
    power_path = os.path.join(figure_dir, "power_vs_current.png")
    fig_power.savefig(power_path, bbox_inches='tight', dpi=300)

    # -------------------------------------------------------------------------
    # FIGURE 2: Derivative dP/dI vs Stator Current
    # -------------------------------------------------------------------------
    fig_dp_di = plt.figure(figsize=(fig_width, fig_height))
    ax2 = plt.gca()

    label_fem_dp = r'd(Power)/d(Current) (FEM)'
    label_mrn_dp = r'd(Power)/d(Current) (MBGRN)'
    
    ax2.plot(stator_current_data, dP_dI_fem, color=color_fem, linestyle='--', marker='x', linewidth=1.5, 
             label=label_fem_dp)
    ax2.plot(stator_current_data, dP_dI_mbgrn, color=color_mrn, linestyle='--', marker='o', linewidth=3.0, 
             label=label_mrn_dp)
    
    # Calculate padding for Figure 2
    all_dp_values = np.concatenate([dP_dI_fem, dP_dI_mbgrn])
    dp_min, dp_max = np.min(all_dp_values), np.max(all_dp_values)
    dp_range = dp_max - dp_min if dp_max - dp_min != 0 else 1.0
    ax2.set_ylim(dp_min - 0.15 * dp_range, dp_max + 0.15 * dp_range)
    
    ax2.set_xlabel('Stator Current ($A$)', fontsize=s.label_size)
    ax2.set_ylabel('$\mathrm{d}P/\mathrm{d}I$ ($W/A$)', fontsize=s.label_size)
    ax2.legend(frameon=True, loc='best', fontsize=s.legend_size)
    ax2.grid(True, which='major', linestyle='-', linewidth=s.grid_linewidth)
    ax2.margins(x=0)

    plt.tight_layout()
    dp_di_path = os.path.join(figure_dir, "dp_di_vs_current.png")
    fig_dp_di.savefig(dp_di_path, bbox_inches='tight', dpi=300)
    
    if plot:
        plt.show()
        
    return fig_power, fig_dp_di