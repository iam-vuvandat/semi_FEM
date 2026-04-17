import paths
import numpy as np 
import matplotlib.pyplot as plt
from src.core.solver.utils.get_waveform_nrmse import get_waveform_nrmse
from src.core.solver.utils.update_dq_axis import update_dq_axis

from types import SimpleNamespace

def compare_flux_linkage(data_processor, horizontal_axis = "mechanical_position", 
                         show_dq_axis = False, show_all_phases = True):
    poles = data_processor.motor.geometry_data.rotor.pole_number
    
    
    record = data_processor.motor.record
    n_phase = data_processor.motor.winding_data.phase
    s = data_processor.plot_style
    shaft_speed = (data_processor.motor.mechanical_data.shaft_speed * np.pi * 2) / 60 

    def get_x_axis(theta_data):
        if horizontal_axis == "time":
            return theta_data / shaft_speed, r'Time ($s$)'
        else:
            return theta_data, r'Rotor Position ($rad$)'

    if hasattr(record, "flux_linkage") and hasattr(record, "flux_linkage_fem"):
        # 1. Lấy dữ liệu thô
        data_sf = record.flux_linkage
        
        # TẠO BẢN SAO để synchronize_signal chỉnh sửa trực tiếp trên bản sao này
        data_fem = record.flux_linkage_fem.copy()

        


        # 2. Đồng bộ hóa dữ liệu (In-place modification)
        data_processor.synchronize_signal(data_true = data_sf, 
                                          data_pred = data_fem)
        
        update_dq_axis(data_full=data_fem, pole_pairs=  poles /2)
        
        # Sau khi gọi hàm trên, data_fem đã được cập nhật dữ liệu mới
        x_sf, x_label = get_x_axis(data_sf[-1, :])
        x_fem, _ = get_x_axis(data_fem[-1, :])

        # 3. Tính toán sai số dựa trên Pha A (index 2)
        wave_mrn = data_sf[2, :]
        wave_fem = data_fem[2, :]

        nrmse_val = get_waveform_nrmse(data_true = wave_fem, data_pred = wave_mrn)
        
        peak_mrn = np.max(np.abs(wave_mrn))
        peak_fem = np.max(np.abs(wave_fem))
        error_peak = np.abs(peak_mrn - peak_fem) / peak_fem * 100

        average_mrn = np.mean(np.abs(wave_mrn))
        average_fem = np.mean(np.abs(wave_fem))
        error_average = np.abs(average_mrn - average_fem) / average_fem * 100

        rms_mrn = np.sqrt(np.mean(wave_mrn**2))
        rms_fem = np.sqrt(np.mean(wave_fem**2))
        error_rms = np.abs(rms_mrn - rms_fem) / rms_fem * 100

        # ==============================================================================
        # 4. Vẽ đồ thị (Đã sửa đổi cách hiển thị đường và marker)
        # ==============================================================================
        fig, ax = plt.subplots(figsize=(16, 10))

        # --- ĐỊNH NGHĨA CÁC ĐỊNH DẠNG MỚI ---
        # 1. FEM dùng nét liền, độ dày vừa phải để làm chuẩn
        fem_linestyle = '-' 
        fem_linewidth = 2.5
        
        # 2. MRN dùng marker, không dùng đường nối
        mrn_linestyle = 'None' 
        # Danh sách các loại marker để xoay vòng: Tròn, Vuông, Tam giác lên, Kim cương, Tam giác xuống
        mrn_markers = ['o', 's', '^', 'D', 'v'] 
        mrn_markersize = 7 # Kích thước dấu chấm

        if show_dq_axis:
            # --- Trục d ---
            # FEM d: Nét liền
            ax.plot(x_fem, data_fem[0, :], color='#4477AA', 
                    linestyle=fem_linestyle, linewidth=fem_linewidth,
                    label=r'$\Psi_d$ (Maxwell)')
            
            # MRN d: Marker Tròn ('o' - index 0)
            ax.plot(x_sf, data_sf[0, :], color='#4477AA', 
                    linestyle=mrn_linestyle, marker=mrn_markers[0], markersize=mrn_markersize,
                    label=r'$\Psi_d$ (semi-FEM)')

            # --- Trục q ---
            # FEM q: Nét liền
            ax.plot(x_fem, data_fem[1, :], color='#EE6677', 
                    linestyle=fem_linestyle, linewidth=fem_linewidth,
                    label=r'$\Psi_q$ (Maxwell)')
            
            # MRN q: Marker Vuông ('s' - index 1)
            ax.plot(x_sf, data_sf[1, :], color='#EE6677', 
                    linestyle=mrn_linestyle, marker=mrn_markers[1], markersize=mrn_markersize,
                    label=r'$\Psi_q$ (semi-FEM)')

        if show_all_phases:
            for i in range(n_phase):
                # Thiết lập màu sắc
                color = s.phase_colors[i % 3] if n_phase == 3 else s.colors[i % len(s.colors)]
                label_p = f'Phase {chr(65+i)}'
                
                # --- Vẽ FEM trước (Nét liền) ---
                ax.plot(x_fem, data_fem[2 + i, :], color=color, 
                        linestyle=fem_linestyle, linewidth=fem_linewidth - 0.5, # Hơi mảnh hơn dq chút
                        label=f'{label_p} (Maxwell)')
                
                # --- Vẽ MRN sau (Marker) ---
                # Chọn marker dựa trên index của pha để thay đổi loại dấu (tròn, vuông, tam giác...)
                # Ta dùng (i + 2) nếu show_dq_axis để tránh trùng marker với d/q, hoặc cứ để i % len nếu muốn đơn giản.
                marker_idx = i % len(mrn_markers) 
                
                ax.plot(x_sf, data_sf[2 + i, :], color=color, 
                        linestyle=mrn_linestyle, marker=mrn_markers[marker_idx], markersize=mrn_markersize - 1,
                        label=f'{label_p} (semi-FEM)')

        # --- Các thiết lập khác giữ nguyên ---
        ax.set_xlabel(x_label, fontsize=s.label_size, family=s.font_family)
        ax.set_ylabel(r'Flux Linkage ($Wb$)', fontsize=s.label_size, family=s.font_family)
        ax.tick_params(axis='both', which='major', labelsize=s.tick_size)
        
        # Tăng ncol trong legend lên 2 để hiển thị gọn gàng khi có nhiều marker
        ax.legend(frameon=True, loc='best', ncol=2, fontsize=s.legend_size)
        
        ax.grid(True, which='both', linestyle='-', linewidth=s.grid_linewidth)
        
        plt.tight_layout()
        plt.show()

        # 5. Đóng gói kết quả
        result = SimpleNamespace(
            nrmse = nrmse_val, 
            peak_mrn = peak_mrn, 
            peak_fem = peak_fem,
            error_peak = error_peak,
            average_mrn = average_mrn,
            average_fem = average_fem,
            error_average = error_average,
            rms_mrn = rms_mrn,
            rms_fem = rms_fem,
            error_rms = error_rms
        )
        
        data_processor.motor.record.flux_linkage_compared = result
        print(result)
        return result

    return None