import paths
import numpy as np
import matplotlib.pyplot as plt
from src.core.solver.utils.synchronize_signals import synchronize_signals
from mpl_toolkits.mplot3d import Axes3D

class DataProcessor:
    def __init__(self, motor):
        self.motor = motor
        self.colors = ['#d62728', '#2ca02c', '#1f77b4', '#ff7f0e', '#9467bd', '#8c564b']

    def plot(self, *arg, horizontal_axis = "mechanical_position", plot_all = False):
        record = self.motor.record
        n_phase = self.motor.winding_data.phase
       
        shaft_speed = (self.motor.mechanical_data.shaft_speed * np.pi * 2) / 60 # rad/s

        def get_x_axis(theta_data):
            if horizontal_axis == "time":
                return theta_data / shaft_speed, "Thời gian (s)"
            else:
                return theta_data, "Vị trí Rotor (rad)"

        # 1. Từ thông liên kết (Flux Linkage)
        if "flux_linkage" in arg or plot_all is True:
            if hasattr(record, "flux_linkage"):
                data = record.flux_linkage
                x_data, x_label = get_x_axis(data[-1, :])
                plt.figure(figsize=(10, 5))
                plt.plot(x_data, data[0, :], 'k--', label='$\Psi_d$', linewidth=1.5)
                plt.plot(x_data, data[1, :], 'k-', label='$\Psi_q$', linewidth=1.5)
                for i in range(n_phase):
                    plt.plot(x_data, data[2 + i, :], color=self.colors[i % 6], 
                             label=f'Pha {chr(65+i)}', alpha=0.7)
                plt.title("Từ thông liên kết (Flux Linkage)", fontweight='bold')
                plt.xlabel(x_label)
                plt.ylabel("Flux (Wb)")
                plt.legend(loc='upper right', ncol=2, fontsize='small')
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

        # 2. Sức điện động pha (Back-EMF)
        if "back_emf" in arg or plot_all is True:
            if hasattr(record, "back_emf"):
                data = record.back_emf
                theta_orig = data[-1, :] if data.shape[0] > n_phase else record.flux_linkage[-1, :]
                x_data, x_label = get_x_axis(theta_orig)
                plt.figure(figsize=(10, 5))
                for i in range(n_phase):
                    plt.plot(x_data, data[i, :], color=self.colors[i % 6], label=f'Pha {chr(65+i)}')
                plt.title("Sức điện động (Back-EMF)", fontweight='bold')
                plt.xlabel(x_label)
                plt.ylabel("Voltage (V)")
                plt.legend(loc='upper right', ncol=2, fontsize='small')
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

        # 3. Sức điện động dây (Back-EMF Line-to-Line)
        if "back_emf_line" in arg or plot_all is True:
            if hasattr(record, "back_emf"):
                data = record.back_emf
                x_data, x_label = get_x_axis(record.flux_linkage[-1, :])
                plt.figure(figsize=(10, 5))
                for i in range(n_phase):
                    v_line = data[i, :] - data[(i + 1) % n_phase, :]
                    plt.plot(x_data, v_line, color=self.colors[i % 6], 
                             label=f'Line {chr(65+i)}{chr(65+(i+1)%n_phase)}')
                plt.title("Sức điện động dây (Line-to-Line Back-EMF)", fontweight='bold')
                plt.xlabel(x_label)
                plt.ylabel("Voltage (V)")
                plt.legend(loc='upper right', ncol=2, fontsize='small')
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

        # 4. Mô-men điện từ (Torque)
        if "torque" in arg or plot_all is True:
            if hasattr(record, "mst_data"):
                data = record.mst_data
                x_data, x_label = get_x_axis(data[-1, :])
                torque_z = data[3, :]
                plt.figure(figsize=(10, 4))
                plt.plot(x_data, torque_z, color='purple', label='Electromagnetic Torque')
                avg_torque = np.mean(torque_z)
                plt.axhline(y=avg_torque, color='black', linestyle='--', label=f'Avg: {avg_torque:.2f} Nm')
                plt.title("Mô-men điện từ (Maxwell Stress)", fontweight='bold')
                plt.xlabel(x_label)
                plt.ylabel("Torque (Nm)")
                plt.ylim(bottom=0)
                plt.legend(loc='upper right')
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

        # 5. Lực dọc trục (Axial Force)
        if "axial_force" in arg or plot_all is True:
            if hasattr(record, "mst_data"):
                data = record.mst_data
                x_data, x_label = get_x_axis(data[-1, :])
                force_z = data[2, :]
                plt.figure(figsize=(10, 4))
                plt.plot(x_data, force_z, color='darkcyan', label='Axial Force')
                avg_force = np.mean(force_z)
                plt.axhline(y=avg_force, color='black', linestyle='--', label=f'Avg: {avg_force:.2f} N')
                plt.title("Lực dọc trục (Axial Force)", fontweight='bold')
                plt.xlabel(x_label)
                plt.ylabel("Force (N)")
                plt.ylim(bottom=0)
                plt.legend(loc='upper right')
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

        # 6. Mô-men răng (Cogging Torque)
        if "cogging_torque" in arg or plot_all is True:
            if hasattr(record, "cogging"):
                data = record.cogging
                x_data, x_label = get_x_axis(data[-1, :])
                plt.figure(figsize=(10, 4))
                plt.plot(x_data, data[0, :], color='brown')
                plt.title("Mô-men răng (Cogging Torque)", fontweight='bold')
                plt.xlabel(x_label)
                plt.ylabel("Torque (Nm)")
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

        # 7. Dòng điện (Currents)
        if "currents" in arg or plot_all is True:
            if hasattr(record, "currents"):
                data = record.currents
                x_data, x_label = get_x_axis(data[-1, :])
                plt.figure(figsize=(10, 5))
                plt.plot(x_data, data[0, :], 'r--', label='$I_d$', linewidth=1.5)
                plt.plot(x_data, data[1, :], 'b-', label='$I_q$', linewidth=1.5)
                for i in range(n_phase):
                    plt.plot(x_data, data[2 + i, :], color=self.colors[i % 6], 
                             label=f'Phase {chr(65+i)}', alpha=0.7)
                plt.title("Dòng điện (Currents)", fontweight='bold')
                plt.xlabel(x_label)
                plt.ylabel("Current (A)")
                plt.legend(loc='upper right', ncol=2, fontsize='small')
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

        # 8. Công suất cơ học (Mechanical Power)
        if "mechanical_power" in arg or plot_all is True:
            if hasattr(record, "mechanical_power"):
                data = record.mechanical_power
                p_values = data[0, :]
                x_data, x_label = get_x_axis(data[1, :])
                plt.figure(figsize=(10, 4))
                plt.plot(x_data, p_values, color='forestgreen', linewidth=1.5, label='P_mech')
                if hasattr(record, "average_mechanical_power"):
                    avg_p = record.average_mechanical_power
                    plt.axhline(y=avg_p, color='red', linestyle='--', label=f'Avg: {avg_p:.2f} W')
                plt.title("Công suất cơ học (Mechanical Power)", fontweight='bold')
                plt.xlabel(x_label)
                plt.ylabel("Power (W)")
                plt.ylim(bottom=0)
                plt.legend(loc='upper right')
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

        # 9. Bản đồ điện cảm 3D (Inductance Map)
        if "inductance_map" in arg or plot_all is True:
            if hasattr(record, "ld_map") and hasattr(record, "lq_map"):
                id_grid = record.id_grid
                iq_grid = record.iq_grid
                ld_map = record.ld_map * 1000 
                lq_map = record.lq_map * 1000 
                ld_map[ld_map == 0] = np.nan
                lq_map[lq_map == 0] = np.nan
                ID, IQ = np.meshgrid(id_grid, iq_grid, indexing='ij')
                fig3d = plt.figure(figsize=(14, 6))
                ax1 = fig3d.add_subplot(121, projection='3d')
                ax1.plot_surface(ID, IQ, ld_map, cmap='viridis', edgecolor='none', alpha=0.9)
                ax1.set_title("Bản đồ điện cảm $L_d$ (mH)", fontweight='bold')
                ax1.set_xlabel("Id (A)")
                ax1.set_ylabel("Iq (A)")
                ax2 = fig3d.add_subplot(122, projection='3d')
                ax2.plot_surface(ID, IQ, lq_map, cmap='plasma', edgecolor='none', alpha=0.9)
                ax2.set_title("Bản đồ điện cảm $L_q$ (mH)", fontweight='bold')
                ax2.set_xlabel("Id (A)")
                ax2.set_ylabel("Iq (A)")
                plt.tight_layout()

        plt.show()
    
    def compare_flux_linkage(self, horizontal_axis = "mechanical_position"):
        self.synchronize_signal(data_true = self.motor.record.flux_linkage, data_pred = self.motor.record.flux_linkage_fem)
        record = self.motor.record
        n_phase = self.motor.winding_data.phase
        shaft_speed = (self.motor.mechanical_data.shaft_speed * np.pi * 2) / 60 

        def get_x_axis(theta_data):
            if horizontal_axis == "time":
                return theta_data / shaft_speed, "Thời gian (s)"
            else:
                return theta_data, "Vị trí Rotor (rad)"

        if hasattr(record, "flux_linkage") and hasattr(record, "flux_linkage_fem"):
            data_sf = record.flux_linkage
            data_fem = record.flux_linkage_fem
            
            x_sf, x_label = get_x_axis(data_sf[-1, :])
            x_fem, _ = get_x_axis(data_fem[-1, :])
            
            plt.figure(figsize=(12, 6))
            for i in range(n_phase):
                color = self.colors[i % 6]
                plt.plot(x_sf, data_sf[2 + i, :], color=color, label=f'semiFEM Pha {chr(65+i)}', linewidth=2)
                plt.plot(x_fem, data_fem[2 + i, :], color=color, linestyle='--', label=f'FEM Pha {chr(65+i)}', alpha=0.6)
            
            plt.title("So sánh Từ thông liên kết: semiFEM vs FEM", fontweight='bold')
            plt.xlabel(x_label)
            plt.ylabel("Flux (Wb)")
            plt.legend(loc='upper right', ncol=2, fontsize='x-small')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()

    def compare_back_emf(self, horizontal_axis = "mechanical_position"):
        self.synchronize_signal(data_true = self.motor.record.back_emf, data_pred = self.motor.record.back_emf_fem)

        record = self.motor.record
        n_phase = self.motor.winding_data.phase
        shaft_speed = (self.motor.mechanical_data.shaft_speed * np.pi * 2) / 60 # rad/s

        def get_x_axis(theta_data):
            if horizontal_axis == "time":
                return theta_data / shaft_speed, "Thời gian (s)"
            else:
                return theta_data, "Vị trí Rotor (rad)"

        # Kiểm tra sự tồn tại của cả hai nguồn dữ liệu
        if hasattr(record, "back_emf") and hasattr(record, "back_emf_fem"):
            data_sf = record.back_emf
            data_fem = record.back_emf_fem
            
            # Trục hoành lấy từ hàng cuối của flux_linkage tương ứng
            x_sf, x_label = get_x_axis(record.flux_linkage[-1, :])
            x_fem, _ = get_x_axis(record.flux_linkage_fem[-1, :])
            
            plt.figure(figsize=(12, 6))
            for i in range(n_phase):
                color = self.colors[i % 6]
                # Vẽ semiFEM (nét liền, dày) và FEM (nét đứt, mờ hơn)
                plt.plot(x_sf, data_sf[i, :], color=color, 
                         label=f'semiFEM Pha {chr(65+i)}', linewidth=2)
                plt.plot(x_fem, data_fem[i, :], color=color, linestyle='--', 
                         label=f'FEM Pha {chr(65+i)}', alpha=0.6)
            
            plt.title("So sánh Sức điện động pha: semiFEM vs FEM", fontweight='bold')
            plt.xlabel(x_label)
            plt.ylabel("Voltage (V)")
            plt.legend(loc='upper right', ncol=2, fontsize='x-small')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()

    def compare_back_emf_line(self, horizontal_axis = "mechanical_position"):
        self.synchronize_signal(data_true = self.motor.record.back_emf_line, data_pred = self.motor.record.back_emf_line_fem)

        record = self.motor.record
        n_phase = self.motor.winding_data.phase
        shaft_speed = (self.motor.mechanical_data.shaft_speed * np.pi * 2) / 60 

        def get_x_axis(theta_data):
            if horizontal_axis == "time":
                return theta_data / shaft_speed, "Thời gian (s)"
            else:
                return theta_data, "Vị trí Rotor (rad)"

        if hasattr(record, "back_emf") and hasattr(record, "back_emf_line_fem"):
            # Xử lý dữ liệu semiFEM: Lấy sẵn hoặc tính toán on-the-fly
            if hasattr(record, "back_emf_line"):
                data_sf = record.back_emf_line
            else:
                # Tính dây-dây: V_ab = V_a - V_b
                data_sf = np.array([record.back_emf[i, :] - record.back_emf[(i + 1) % n_phase, :] 
                                   for i in range(n_phase)])
            
            data_fem = record.back_emf_line_fem
            
            x_sf, x_label = get_x_axis(record.flux_linkage[-1, :])
            x_fem, _ = get_x_axis(record.flux_linkage_fem[-1, :])
            
            plt.figure(figsize=(12, 6))
            for i in range(n_phase):
                color = self.colors[i % 6]
                label_name = f'{chr(65+i)}{chr(65+(i+1)%n_phase)}'
                plt.plot(x_sf, data_sf[i, :], color=color, 
                         label=f'semiFEM Dây {label_name}', linewidth=2)
                plt.plot(x_fem, data_fem[i, :], color=color, linestyle='--', 
                         label=f'FEM Dây {label_name}', alpha=0.6)
            
            plt.title("So sánh Sức điện động dây: semiFEM vs FEM", fontweight='bold')
            plt.xlabel(x_label)
            plt.ylabel("Voltage (V)")
            plt.legend(loc='upper right', ncol=2, fontsize='x-small')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
    
    def synchronize_signal(self,data_true, data_pred, is_periodic=True, half_open_interval=True):
        synchronize_signals(data_true = data_true, data_pred = data_pred, is_periodic= is_periodic, half_open_interval= half_open_interval)

