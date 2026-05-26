import paths
import numpy as np
import matplotlib.pyplot as plt
import scienceplots

from src.core.core_class.utils.for_data_processor.apply_jounal_style import apply_journal_style
from src.core.core_class.utils.for_data_processor.plot_flux_linkage import plot_flux_linkage
from src.core.core_class.utils.for_data_processor.plot_back_emf import plot_back_emf
from src.core.core_class.utils.for_data_processor.plot_current import plot_current
from src.core.core_class.utils.for_data_processor.plot_torque import plot_torque
from src.core.core_class.utils.for_data_processor.plot_axial_force import plot_axial_force
from src.core.core_class.utils.for_data_processor.plot_cogging_torque import plot_cogging_torque
from src.core.core_class.utils.for_data_processor.plot_mechanical_power import plot_mechanical_power
from src.core.core_class.utils.for_data_processor.plot_inductance_map import plot_inductance_map
from src.core.core_class.utils.for_data_processor.plot_airgap_flux_density import plot_airgap_flux_density
from src.core.core_class.utils.for_data_processor.plot_airgap_flux_density_no_load import plot_airgap_flux_density_no_load


from mpl_toolkits.mplot3d import Axes3D

class DataProcessor:
    def __init__(self, motor):
        """
        Class for post-processing and analyzing simulation data.

        Properties (MBGRN - Stored in motor.record):
        - flux_linkage: (phase + 3, n_point) -> [Psi_d, Psi_q, Psi_0, Psi_A, Psi_B, ..., Position]
        - back_emf: (phase, n_point) -> Induced Back Electromotive Force (V)
        - currents: (3 + phase, n_point) -> [i_d, i_q, i_0, i_A, i_B, ..., Position]
        - cogging: (2, n_point) -> [Torque_cog, Position]
        - torque: (2, n_point) -> [Torque_total, Position]
        - axial_force: (2, n_point) -> [Force_z, Position]
        - mechanical_power: (2, n_point) -> [Power, Position]
        - average_mechanical_power: scalar (float)
        - id_grid, iq_grid: (resolution,) -> Current grid arrays for the inductance map
        - ld_map, lq_map: (resolution, resolution) -> Ld and Lq inductance maps

        Properties (FEM - Stored in motor.record):
        - flux_linkage_fem: (phase + 3, n_steps_fem) -> [Psi_d, Psi_q, ..., Position]
        - back_emf_fem: (phase, n_steps_fem) -> Back EMF from FEM solver (V)
        - torque_fem: (2, n_steps_fem) -> [Torque, Position]
        - mechanical_power_fem: (2, n_steps_fem) -> [Power, Position]
        - average_mechanical_power_fem: scalar (float)
        - axial_force_fem: (2, n_steps_fem) -> [Force_z, Position]
        - average_axial_force_fem: scalar (float)
        """
        self.motor = motor
        self.plot_style = apply_journal_style()

    def plot_airgap_flux_density(self, horizontal_axis="mechanical_position", show_fem=True, show_harmonic=True, plot=True):
        return plot_airgap_flux_density(data_processor=self, horizontal_axis=horizontal_axis, 
                                        show_fem=show_fem, show_harmonic=show_harmonic, plot=plot)

    def plot_airgap_flux_density_no_load(self, horizontal_axis="mechanical_position", show_fem=True, show_harmonic=True, plot=True):
        return plot_airgap_flux_density_no_load(data_processor=self, horizontal_axis=horizontal_axis, 
                                                show_fem=show_fem, show_harmonic=show_harmonic, plot=plot)
    
    def plot_flux_linkage(self, horizontal_axis="mechanical_position", show_fem=True, 
                          show_dq=False, show_all_phase=False, plot=True):
        return plot_flux_linkage(data_processor=self, horizontal_axis=horizontal_axis, 
                                 show_fem=show_fem, show_dq=show_dq, 
                                 show_all_phase=show_all_phase, plot=plot)

    def plot_back_emf(self, horizontal_axis="mechanical_position", show_fem=True, 
                      show_all_phases=False, plot=True):
        return plot_back_emf(data_processor=self, horizontal_axis=horizontal_axis, 
                             show_fem=show_fem, show_all_phases=show_all_phases, plot=plot)
    
    def plot_current(self, horizontal_axis="mechanical_position", show_fem=True, plot=True):
        return plot_current(data_processor=self, horizontal_axis=horizontal_axis, 
                            show_fem=show_fem, plot=plot)

    def plot_torque(self, horizontal_axis="mechanical_position", show_fem=True, plot=True, revert=False):
        return plot_torque(data_processor=self, horizontal_axis=horizontal_axis, 
                           show_fem=show_fem, plot=plot, revert=revert)
    
    def plot_axial_force(self, horizontal_axis="mechanical_position", show_fem=True, plot=True, revert=True):
        return plot_axial_force(data_processor=self, horizontal_axis=horizontal_axis, 
                                show_fem=show_fem, plot=plot, revert=revert)
    
    def plot_cogging_torque(self, horizontal_axis="mechanical_position", show_fem=True, plot=True, revert=True, num_periods=1):
        return plot_cogging_torque(data_processor=self, horizontal_axis=horizontal_axis, 
                                   show_fem=show_fem, plot=plot, revert=revert, num_periods=num_periods)

    def plot_mechanical_power(self, horizontal_axis="mechanical_position", show_fem=True, plot=True, revert=False):
        return plot_mechanical_power(data_processor=self, horizontal_axis=horizontal_axis, 
                                     show_fem=show_fem, plot=plot, revert=revert)

    def plot_inductance_map(self, plot=True):
        return plot_inductance_map(data_processor=self, plot=plot)