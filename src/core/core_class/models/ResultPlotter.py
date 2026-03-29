import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class ResultPlotter:
    def __init__(self, motor):
        self.motor = motor
        self.colors = ['#d62728', '#2ca02c', '#1f77b4', '#ff7f0e', '#9467bd', '#8c564b']

    def plot(self, *arg, plot_all = False):
        record = self.motor.record
        n_phase = self.motor.winding_data.phase

        # 1. Từ thông liên kết (Flux Linkage)
        if "flux_linkage" in arg or plot_all is True:
            if hasattr(record, "flux_linkage"):
                data = record.flux_linkage
                theta = data[-1, :]
                plt.figure(figsize=(10, 5))
                plt.plot(theta, data[0, :], 'k--', label='$\Psi_d$', linewidth=1.5)
                plt.plot(theta, data[1, :], 'k-', label='$\Psi_q$', linewidth=1.5)
                for i in range(n_phase):
                    plt.plot(theta, data[2 + i, :], color=self.colors[i % 6], 
                             label=f'Pha {chr(65+i)}', alpha=0.7)
                plt.title("Từ thông liên kết (Flux Linkage)", fontweight='bold')
                plt.xlabel("Vị trí Rotor (rad)")
                plt.ylabel("Flux (Wb)")
                plt.legend(loc='upper right', ncol=2, fontsize='small')
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

        # 2. Sức điện động pha (Back-EMF)
        if "back_emf" in arg or plot_all is True:
            if hasattr(record, "back_emf"):
                data = record.back_emf
                theta = data[-1, :] if data.shape[0] > n_phase else record.flux_linkage[-1, :]
                plt.figure(figsize=(10, 5))
                for i in range(n_phase):
                    plt.plot(theta, data[i, :], color=self.colors[i % 6], label=f'Pha {chr(65+i)}')
                plt.title("Sức điện động (Back-EMF)", fontweight='bold')
                plt.xlabel("Vị trí Rotor (rad)")
                plt.ylabel("Voltage (V)")
                plt.legend(loc='upper right', ncol=2, fontsize='small')
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

        # 3. Sức điện động dây (Back-EMF Line-to-Line)
        if "back_emf_line" in arg or plot_all is True:
            if hasattr(record, "back_emf"):
                data = record.back_emf
                theta = record.flux_linkage[-1, :]
                plt.figure(figsize=(10, 5))
                for i in range(n_phase):
                    v_line = data[i, :] - data[(i + 1) % n_phase, :]
                    plt.plot(theta, v_line, color=self.colors[i % 6], 
                             label=f'Line {chr(65+i)}{chr(65+(i+1)%n_phase)}')
                plt.title("Sức điện động dây (Line-to-Line Back-EMF)", fontweight='bold')
                plt.xlabel("Vị trí Rotor (rad)")
                plt.ylabel("Voltage (V)")
                plt.legend(loc='upper right', ncol=2, fontsize='small')
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

        # 4. Mô-men điện từ (Torque)
        if "torque" in arg or plot_all is True:
            if hasattr(record, "mst_data"):
                data = record.mst_data
                theta = data[-1, :]
                torque_z = data[3, :]
                plt.figure(figsize=(10, 4))
                plt.plot(theta, torque_z, color='purple', label='Electromagnetic Torque')
                avg_torque = np.mean(torque_z)
                plt.axhline(y=avg_torque, color='black', linestyle='--', label=f'Avg: {avg_torque:.2f} Nm')
                plt.title("Mô-men điện từ (Maxwell Stress)", fontweight='bold')
                plt.xlabel("Vị trí Rotor (rad)")
                plt.ylabel("Torque (Nm)")
                plt.ylim(bottom=0)
                plt.legend(loc='upper right')
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

        # 5. Lực dọc trục (Axial Force)
        if "axial_force" in arg or plot_all is True:
            if hasattr(record, "mst_data"):
                data = record.mst_data
                theta = data[-1, :]
                force_z = data[2, :]
                plt.figure(figsize=(10, 4))
                plt.plot(theta, force_z, color='darkcyan', label='Axial Force')
                avg_force = np.mean(force_z)
                plt.axhline(y=avg_force, color='black', linestyle='--', label=f'Avg: {avg_force:.2f} N')
                plt.title("Lực dọc trục (Axial Force)", fontweight='bold')
                plt.xlabel("Vị trí Rotor (rad)")
                plt.ylabel("Force (N)")
                plt.ylim(bottom=0)
                plt.legend(loc='upper right')
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

        # 6. Mô-men răng (Cogging Torque)
        if "cogging_torque" in arg or plot_all is True:
            if hasattr(record, "cogging"):
                data = record.cogging
                theta = data[-1, :]
                plt.figure(figsize=(10, 4))
                plt.plot(theta, data[0, :], color='brown')
                plt.title("Mô-men răng (Cogging Torque)", fontweight='bold')
                plt.xlabel("Vị trí Rotor (rad)")
                plt.ylabel("Torque (Nm)")
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

        # 7. Dòng điện (Currents)
        if "currents" in arg or plot_all is True:
            if hasattr(record, "currents"):
                data = record.currents
                theta = data[-1, :]
                plt.figure(figsize=(10, 5))
                plt.plot(theta, data[0, :], 'r--', label='$I_d$', linewidth=1.5)
                plt.plot(theta, data[1, :], 'b-', label='$I_q$', linewidth=1.5)
                for i in range(n_phase):
                    plt.plot(theta, data[2 + i, :], color=self.colors[i % 6], 
                             label=f'Phase {chr(65+i)}', alpha=0.7)
                plt.title("Dòng điện (Currents)", fontweight='bold')
                plt.xlabel("Vị trí Rotor (rad)")
                plt.ylabel("Current (A)")
                plt.legend(loc='upper right', ncol=2, fontsize='small')
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

        # 8. Công suất cơ học (Mechanical Power)
        if "mechanical_power" in arg or plot_all is True:
            if hasattr(record, "mechanical_power"):
                data = record.mechanical_power
                p_values = data[0, :]
                theta = data[1, :]
                plt.figure(figsize=(10, 4))
                plt.plot(theta, p_values, color='forestgreen', linewidth=1.5, label='P_mech')
                if hasattr(record, "average_mechanical_power"):
                    avg_p = record.average_mechanical_power
                    plt.axhline(y=avg_p, color='red', linestyle='--', label=f'Avg: {avg_p:.2f} W')
                plt.title("Công suất cơ học (Mechanical Power)", fontweight='bold')
                plt.xlabel("Vị trí Rotor (rad)")
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

        # Lenh show duy nhat de hien thi tat ca cac figure da khoi tao
        plt.show()