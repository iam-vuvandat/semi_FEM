import numpy as np
import matplotlib.pyplot as plt

class Record:
    def __init__(self, motor):
        self.mechanical = motor.mechanical
        self.flux_linkage = None
        self.back_emf = None
        self.mst_data = None

    @property
    def phase_number(self):
        if self.flux_linkage is not None:
            return self.flux_linkage.shape[0] - 1
        return 0
    
    def plot_maxwell_stress_tensor(self, plot=False):
        if self.mst_data is None or self.position is None:
            return None
        
        fig, axs = plt.subplots(2, 2, figsize=(12, 10))
        pos_deg = self.position * (180 / np.pi)
        
        # Fx - Index 0
        axs[0, 0].plot(pos_deg, self.mst_data[0, :], color='b')
        axs[0, 0].set_title("Force Fx")
        axs[0, 0].set_ylabel("Force [N]")
        axs[0, 0].grid(True)

        # Fy - Index 1
        axs[0, 1].plot(pos_deg, self.mst_data[1, :], color='g')
        axs[0, 1].set_title("Force Fy")
        axs[0, 1].set_ylabel("Force [N]")
        axs[0, 1].grid(True)

        # Fz - Index 2
        axs[1, 0].plot(pos_deg, self.mst_data[2, :], color='r')
        axs[1, 0].set_title("Force Fz (Axial Force)")
        axs[1, 0].set_ylabel("Force [N]")
        axs[1, 0].grid(True)

        # Tz - Index 3
        axs[1, 1].plot(pos_deg, self.mst_data[3, :], color='m')
        axs[1, 1].set_title("Torque Tz")
        axs[1, 1].set_ylabel("Torque [Nm]")
        axs[1, 1].grid(True)

        for ax in axs.flat:
            ax.set_xlabel("Position [deg]")

        fig.tight_layout()
        
        if plot:
            plt.show()
            
        return fig

    def plot_back_emf(self, plot=False):
        if self.back_emf is None or self.position is None:
            return None
        
        fig, ax = plt.subplots()
        n_phase = self.phase_number
        pos_deg = self.position * (180 / np.pi)
        for i in range(n_phase):
            ax.plot(pos_deg, self.back_emf[i, :], label=f"Phase {i+1}")
            
        ax.set_title("Back EMF vs Position")
        ax.set_xlabel("Position [deg]")
        ax.set_ylabel("Voltage [V]")
        ax.grid(True)
        ax.legend()
        
        if plot:
            plt.show()
            
        return fig

    def plot_flux_linkage(self, plot=False):
        if self.flux_linkage is None or self.position is None:
            return None
        
        fig, ax = plt.subplots()
        n_phase = self.phase_number
        pos_deg = self.position * (180 / np.pi)
        for i in range(n_phase):
            ax.plot(pos_deg, self.flux_linkage[i, :], label=f"Phase {i+1}")
        
        ax.set_title("Flux Linkage vs Position")
        ax.set_xlabel("Position [deg]")
        ax.set_ylabel("Flux [Wb]")
        ax.grid(True)
        ax.legend()
        
        if plot:
            plt.show()
            
        return fig

    def get_average_torque(self):
        if self.mst_data is not None:
            return np.mean(self.mst_data[3, :])
        return 0.0