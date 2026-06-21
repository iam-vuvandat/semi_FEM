import os
import math
import pickle
import numpy as np

# KHẮC PHỤC LỖI KẸT: Ép Matplotlib sử dụng backend không tương tác ngay từ đầu
import matplotlib
matplotlib.use('Agg') 

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import paths
import scienceplots
from types import SimpleNamespace
from src.core.storage.core.MotorIO import MotorIO
from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
from src.core.ansys_maxwell.rmxprt.setup.init_window import init_window

def apply_journal_style():
    plt.style.use(['science', 'no-latex'])
    config = {
        'font.size': 20,
        'axes.titlesize': 30,
        'axes.labelsize': 25,
        'xtick.labelsize': 18,
        'ytick.labelsize': 18,
        'legend.fontsize': 16,
        'mathtext.fontset': 'stix',
        'font.family': 'serif',
        'font.serif': ['Times New Roman'],
        'axes.grid': True,
        'grid.linestyle': '-',
        'grid.linewidth': 0.005,
        'xtick.direction': 'in',
        'ytick.direction': 'in',
    }
    plt.rcParams.update(config)
    colors = [
        '#EE6677', '#CCBB44', '#4477AA', '#228833', '#AA3377', '#66CCEE', '#BBBBBB'
    ]
    phase_colors = [colors[2], colors[0], colors[1]]
    markers = ['s', 'v', 'o', '^', 'X', 'D', 'P', 'h']
    linestyles = ['-', '--', ':']
    return SimpleNamespace(
        colors=colors,
        phase_colors=phase_colors,
        markers=markers,
        linestyles=linestyles,
        font_size=config['font.size'],
        title_size=config['axes.titlesize'],
        label_size=config['axes.labelsize'],  
        tick_size=config['xtick.labelsize'],
        legend_size=config['legend.fontsize'],
        font_family=config['font.serif'][0],
        grid_linewidth=config['grid.linewidth']
    )

pi = math.pi
io = MotorIO()
solve = False

file_name = "motor_for_paper" 
max_relative_residual = 0.01 * 1e-2

relax_values = [0.01, 0.1, 0.2, 0.3, 0.5, 1.0]

scenarios = []
for r in relax_values:
    scenarios.append({"relax": r, "decay": 1.00, "label": f"$\\alpha = {r}, \\beta = 1.00$"})

for r in relax_values:
    scenarios.append({"relax": r, "decay": 0.50, "label": f"$\\alpha = {r}, \\beta = 0.50$"})

convergence_data = {}
root_dir = paths.configure_path()
pickle_dir = os.path.join(root_dir, "data", "repo", "processed")
pickle_path = os.path.join(pickle_dir, "solver_comprehensive_study_data.pkl")

if solve:
    init_window()
    for idx, case in enumerate(scenarios):
        aft = io.load(path=file_name)
        aft.calculation_data.convergence_settings.enable_potential_tracking = True
        aft.calculation_data.convergence_settings.max_iteration = 100
        aft.calculation_data.general_options.solve_cogging = False
        aft.calculation_data.general_options.solve_standard = True
        aft.calculation_data.general_options.solve_under_no_load = False
        aft.calculation_data.general_options.solve_only_1_step = True
        aft.calculation_data.convergence_settings.max_relative_residual = max_relative_residual
        aft.calculation_data.convergence_settings.force_use_full_iteration = True
        aft.calculation_data.convergence_settings.material_relax = case["relax"]
        aft.calculation_data.convergence_settings.relaxation_decay = case["decay"]
        aft.just_changed('calculation_data')
        aft.analysis_motor()
        if hasattr(aft.record, 'solver_history') and len(aft.record.solver_history) > 0:
            pot_hist = aft.record.magnetic_potential_history[0].copy() if (hasattr(aft.record, 'magnetic_potential_history') and len(aft.record.magnetic_potential_history) > 0) else None
            convergence_data[idx] = {
                "matrix": aft.record.solver_history[0].copy(),
                "label": case["label"],
                "potential_history": pot_hist
            }
    if not os.path.exists(pickle_dir):
        os.makedirs(pickle_dir)
    with open(pickle_path, 'wb') as f:
        pickle.dump(convergence_data, f)
    print(f"\033[92mData successfully simulated and saved to [{pickle_path}]\033[0m")
else:
    with open(pickle_path, 'rb') as f:
        convergence_data = pickle.load(f)
    print(f"\033[94mData successfully loaded from [{pickle_path}]\033[0m")

s = apply_journal_style()
figure_dir = os.path.join(root_dir, "data", "repo", "figures")
if not os.path.exists(figure_dir):
    os.makedirs(figure_dir)

convergence_threshold = max_relative_residual

# -----------------------------------------------------------------
# GRAPH 1: Limitations of Fixed Relaxation Factors
# -----------------------------------------------------------------
plt.figure(figsize=(11, 7))
plt.axhline(y=convergence_threshold, color='#FF0000', linestyle=':', linewidth=1.5, label='Convergence Threshold')

fixed_indices = [0, 1, 2, 3, 4, 5] 
for plot_idx, src_idx in enumerate(fixed_indices):
    if src_idx in convergence_data:
        matrix = convergence_data[src_idx]["matrix"]
        label = convergence_data[src_idx]["label"]
        iterations = matrix[:, 0]
        residuals = matrix[:, 1]
        
        plt.plot(
            iterations, residuals, 
            marker=s.markers[plot_idx], markevery=4, 
            linestyle='-', linewidth=1.5, 
            color=s.colors[plot_idx], label=label
        )

plt.xlabel('Iteration', fontsize=s.label_size)
plt.ylabel('Relative Residual', fontsize=s.label_size)
plt.yscale('log')
plt.xlim(0, 100)
plt.gca().yaxis.set_major_formatter(mticker.LogFormatterMathtext())
plt.grid(True, which="both", linestyle="-", linewidth=s.grid_linewidth)
plt.legend(loc='upper right', fontsize=s.legend_size, frameon=True)
plt.tight_layout()

save_path_1 = os.path.join(figure_dir, "material_relax_1.png")
plt.savefig(save_path_1, bbox_inches='tight', dpi=300)
print(f"\033[92mGraph 1 saved to [{save_path_1}]\033[0m")
plt.close()

# -----------------------------------------------------------------
# GRAPH 2: Adaptive Decay Mechanism
# -----------------------------------------------------------------
plt.figure(figsize=(11, 7))
plt.axhline(y=convergence_threshold, color='#FF0000', linestyle=':', linewidth=1.5, label='Convergence Threshold')

adaptive_indices = [6, 7, 8, 9, 10, 11] 
for plot_idx, src_idx in enumerate(adaptive_indices):
    if src_idx in convergence_data:
        matrix = convergence_data[src_idx]["matrix"]
        label = convergence_data[src_idx]["label"]
        iterations = matrix[:, 0]
        residuals = matrix[:, 1]
        
        plt.plot(
            iterations, residuals, 
            marker=s.markers[plot_idx], markevery=2, 
            linestyle='-', linewidth=1.5, 
            color=s.colors[plot_idx], label=label
        )

plt.xlabel('Iteration', fontsize=s.label_size)
plt.ylabel('Relative Residual', fontsize=s.label_size)
plt.yscale('log')
# ĐÃ SỬA: Thay đổi giới hạn xlim từ 30 về 22 để loại bỏ khoảng trắng lệch trái
plt.xlim(0, 22)
plt.gca().yaxis.set_major_formatter(mticker.LogFormatterMathtext())
plt.grid(True, which="both", linestyle="-", linewidth=s.grid_linewidth)
plt.legend(loc='upper right', fontsize=s.legend_size, frameon=True)
plt.tight_layout()

save_path_2 = os.path.join(figure_dir, "material_relax_2.png")
plt.savefig(save_path_2, bbox_inches='tight', dpi=300)
print(f"\033[92mGraph 2 saved to [{save_path_2}]\033[0m")
plt.close()

# -----------------------------------------------------------------
# EXTRACT REFERENCE SOLUTION (A_star)
# -----------------------------------------------------------------
A_star = None
norm_A_star = 1.0
if 11 in convergence_data and convergence_data[11].get("potential_history") is not None:
    A_star = convergence_data[11]["potential_history"][-1]
    norm_A_star = np.linalg.norm(A_star) + 1e-12

# -----------------------------------------------------------------
# GRAPH 3: Dynamic Error Evolution for Fixed Factors (decay = 1.0)
# -----------------------------------------------------------------
if A_star is not None:
    plt.figure(figsize=(11, 7))
    plt.axhline(y=convergence_threshold, color='#FF0000', linestyle=':', linewidth=1.5, label='Convergence Threshold')
    
    fixed_indices = [0, 1, 2, 3, 4, 5]
    for plot_idx, src_idx in enumerate(fixed_indices):
        if src_idx in convergence_data and convergence_data[src_idx].get("potential_history") is not None:
            pot_hist = convergence_data[src_idx]["potential_history"]
            matrix = convergence_data[src_idx]["matrix"]
            iterations = matrix[:, 0]
            
            relative_errors = [np.linalg.norm(pot - A_star) / norm_A_star for pot in pot_hist]
            
            plt.plot(
                iterations, relative_errors, 
                marker=s.markers[plot_idx], markevery=4 if src_idx != 0 else 1, 
                linestyle='-', linewidth=1.5, 
                color=s.colors[plot_idx], label=convergence_data[src_idx]["label"]
            )

    plt.xlabel('Iteration', fontsize=s.label_size)
    plt.ylabel('Global Relative Error', fontsize=s.label_size)
    plt.yscale('log')
    plt.xlim(0, 100)
    plt.gca().yaxis.set_major_formatter(mticker.LogFormatterMathtext())
    plt.grid(True, which="both", linestyle="-", linewidth=s.grid_linewidth)
    plt.legend(loc='upper right', fontsize=s.legend_size, frameon=True)
    plt.tight_layout()
    
    save_path_3 = os.path.join(figure_dir, "material_relax_3.png")
    plt.savefig(save_path_3, bbox_inches='tight', dpi=300)
    print(f"\033[92mGraph 3 saved to [{save_path_3}]\033[0m")
    plt.close()

# -----------------------------------------------------------------
# GRAPH 4: Dynamic Error Evolution for Adaptive Scenarios (decay = 0.5)
# -----------------------------------------------------------------
if A_star is not None:
    plt.figure(figsize=(11, 7))
    plt.axhline(y=convergence_threshold, color='#FF0000', linestyle=':', linewidth=1.5, label='Convergence Threshold')
    
    adaptive_indices = [6, 7, 8, 9, 10, 11]
    for plot_idx, src_idx in enumerate(adaptive_indices):
        if src_idx in convergence_data and convergence_data[src_idx].get("potential_history") is not None:
            pot_hist = convergence_data[src_idx]["potential_history"]
            matrix = convergence_data[src_idx]["matrix"]
            iterations = matrix[:, 0]
            
            relative_errors = [np.linalg.norm(pot - A_star) / norm_A_star for pot in pot_hist]
            
            plt.plot(
                iterations, relative_errors, 
                marker=s.markers[plot_idx], markevery=2, 
                linestyle='-', linewidth=1.5, 
                color=s.colors[plot_idx], label=convergence_data[src_idx]["label"]
            )

    plt.xlabel('Iteration', fontsize=s.label_size)
    plt.ylabel('Global Relative Error', fontsize=s.label_size)
    plt.yscale('log')
    # ĐÃ SỬA: Thay đổi giới hạn xlim từ 30 về 22 để đồ thị ôm sát dữ liệu, phân bổ đối xứng hoàn hảo
    plt.xlim(0, 22)
    plt.gca().yaxis.set_major_formatter(mticker.LogFormatterMathtext())
    plt.grid(True, which="both", linestyle="-", linewidth=s.grid_linewidth)
    plt.legend(loc='upper right', fontsize=s.legend_size, frameon=True)
    plt.tight_layout()
    
    save_path_4 = os.path.join(figure_dir, "material_relax_4.png")
    plt.savefig(save_path_4, bbox_inches='tight', dpi=300)
    print(f"\033[92mGraph 4 saved to [{save_path_4}]\033[0m")
    plt.close()