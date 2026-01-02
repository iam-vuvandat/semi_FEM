import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# 1. THIẾT LẬP PATH ĐỂ IMPORT MODULE
# =============================================================================
def setup_paths():
    current_file = os.path.abspath(__file__)
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
    if root_dir not in sys.path:
        sys.path.append(root_dir)

setup_paths()

from material.models.MaterialDataBase import MaterialDataBase
from material.core.lookup_BH_curve import lookup_BH_curve

# =============================================================================
# 2. CẤU HÌNH ĐỒ THỊ CHUẨN IEEE (TUYẾN TÍNH)
# =============================================================================
def set_ieee_style():
    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Times New Roman'],
        'font.size': 12,
        'axes.labelsize': 13,
        'axes.titlesize': 14,
        'xtick.labelsize': 11,
        'ytick.labelsize': 11,
        'legend.fontsize': 10,
        'axes.grid': True,
        'grid.alpha': 0.4,
        'grid.linestyle': '--',
        'mathtext.fontset': 'stix',
        'lines.linewidth': 1.8
    })

# =============================================================================
# 3. HÀM TEST VẬT LIỆU (LINEAR SCALE)
# =============================================================================
def test_material_load_stepping_linear():
    # Khởi tạo Database (Tự động smooth và tạo backup chuẩn)
    material_database = MaterialDataBase(iron_type="M350-50A")
    
    # Dải quét từ -2.6T đến 2.6T
    B_input = np.linspace(-2.6, 2.6, 2000)
    mu_0 = 4 * np.pi * 1e-7
    
    set_ieee_style()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), constrained_layout=True)

    # Các hệ số tải để quan sát sự tịnh tiến
    load_factors = [0.1, 0.3, 0.6, 1.0]
    colors = plt.cm.plasma(np.linspace(0, 0.8, len(load_factors)))

    print(f"{'Load Factor':<12} | {'Max Mu_r':<15} | {'Symmetry'}")
    print("-" * 50)

    for i, lf in enumerate(load_factors):
        # 1. Can thiệp vật liệu từ bản backup
        material_database.step_permeability(load_factor=lf)
        
        # 2. Tra cứu dữ liệu
        data_out = lookup_BH_curve(
            B_input=B_input, 
            material_database=material_database,
            return_du_dB=False
        )
        
        # 3. Tính toán H chuẩn (H = B / (mu_0 * mu_r))
        with np.errstate(divide='ignore', invalid='ignore'):
            H_calc = np.where(np.abs(B_input) > 1e-10, 
                              B_input / (mu_0 * data_out.mu_r), 
                              0.0)
        
        label = rf'Factor $\lambda_m = {lf:.1f}$'
        if lf == 1.0: label += " (Actual Curve)"
        
        # Đồ thị 1: mu_r vs B (THANG TUYẾN TÍNH)
        ax1.plot(B_input, data_out.mu_r, color=colors[i], label=label)
        
        # Đồ thị 2: B vs H
        ax2.plot(H_calc, B_input, color=colors[i], label=label)
        
        # Check đối xứng
        mu_pos = np.interp(2.0, B_input, data_out.mu_r)
        mu_neg = np.interp(-2.0, B_input, data_out.mu_r)
        status = "OK" if np.isclose(mu_pos, mu_neg, rtol=1e-3) else "Fail"
        print(f"{lf:<12.1f} | {np.max(data_out.mu_r):<15.2f} | {status}")

    # Cấu hình đồ thị mu_r (Linear)
    ax1.set_ylabel(r'Relative Permeability, $\mu_r$')
    ax1.set_xlabel(r'Flux Density, $B$ (T)')
    ax1.set_title(r'(a) Relative Permeability Symmetry (Linear Scale)', pad=10)
    ax1.axhline(y=1.0, color='red', linestyle=':', label='Air limit')
    ax1.legend(loc='upper right')
    # Giới hạn trục Y để thấy rõ đỉnh (tùy vật liệu, M350-50A thường max ~7000)
    ax1.set_ylim(bottom=0) 

    # Cấu hình đồ thị B-H
    ax2.set_xlabel(r'Magnetic Field Intensity, $H$ (A/m)')
    ax2.set_ylabel(r'Flux Density, $B$ (T)')
    ax2.set_title(r'(b) $B-H$ Curve Scaling (Full Range Symmetry)', pad=10)
    ax2.axhline(y=0, color='black', lw=0.8, alpha=0.5)
    ax2.axvline(x=0, color='black', lw=0.8, alpha=0.5)
    ax2.set_xlim([-50000, 50000]) 
    ax2.legend(loc='lower right')

    plt.show()

if __name__ == "__main__":
    test_material_load_stepping_linear()