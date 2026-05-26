import numpy as np 
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def plot_inductance_map(data_processor, plot = False):
    record = data_processor.motor.record
    
    # Chủ động đọc các thông số từ SimpleNamespace
    s = data_processor.plot_style
    
    fig = None
    if hasattr(record, "ld_map") and hasattr(record, "lq_map"):
        id_grid = record.id_grid
        iq_grid = record.iq_grid
        
        # Chuyển đổi sang mH để dễ quan sát
        ld_map = record.ld_map * 1000 
        lq_map = record.lq_map * 1000 
        
        # Xử lý các điểm không tính toán để tránh lỗi vẽ mặt
        ld_map[ld_map == 0] = np.nan
        lq_map[lq_map == 0] = np.nan
        
        # Tạo lưới tọa độ
        ID, IQ = np.meshgrid(id_grid, iq_grid, indexing='ij')
        
        fig = plt.figure(figsize=(20, 10))
        
        # --- Vẽ bản đồ Ld ---
        ax1 = fig.add_subplot(121, projection='3d')
        surf1 = ax1.plot_surface(ID, IQ, ld_map, cmap='viridis', 
                                 edgecolor='none', alpha=0.9, antialiased=True)
        
        # Chủ động thiết lập tiêu đề và nhãn trục
        ax1.set_title(r'Inductance Map $L_d$ ($mH$)', fontsize=s.title_size, family=s.font_family)
        ax1.set_xlabel(r'$I_d$ (A)', fontsize=s.label_size, family=s.font_family)
        ax1.set_ylabel(r'$I_q$ (A)', fontsize=s.label_size, family=s.font_family)
        ax1.set_zlabel(r'$L_d$ ($mH$)', fontsize=s.label_size, family=s.font_family)
        
        # Thiết lập cỡ chữ cho các con số trên trục (ticks)
        ax1.tick_params(axis='both', which='major', labelsize=s.tick_size)
        
        # Colorbar
        cbar1 = fig.colorbar(surf1, ax=ax1, shrink=0.5, aspect=10, pad=0.1)
        cbar1.ax.tick_params(labelsize=s.tick_size)

        # --- Vẽ bản đồ Lq ---
        ax2 = fig.add_subplot(122, projection='3d')
        surf2 = ax2.plot_surface(ID, IQ, lq_map, cmap='plasma', 
                                 edgecolor='none', alpha=0.9, antialiased=True)
        
        ax2.set_title(r'Inductance Map $L_q$ ($mH$)', fontsize=s.title_size, family=s.font_family)
        ax2.set_xlabel(r'$I_d$ (A)', fontsize=s.label_size, family=s.font_family)
        ax2.set_ylabel(r'$I_q$ (A)', fontsize=s.label_size, family=s.font_family)
        ax2.set_zlabel(r'$L_q$ ($mH$)', fontsize=s.label_size, family=s.font_family)
        
        # Thiết lập cỡ chữ cho các con số trên trục
        ax2.tick_params(axis='both', which='major', labelsize=s.tick_size)
        
        # Colorbar
        cbar2 = fig.colorbar(surf2, ax=ax2, shrink=0.5, aspect=10, pad=0.1)
        cbar2.ax.tick_params(labelsize=s.tick_size)

        # Điều chỉnh góc nhìn mặc định
        ax1.view_init(elev=30, azim=-135)
        ax2.view_init(elev=30, azim=-135)
        
        plt.tight_layout()
        
        if plot:
            plt.show()
            
    return fig