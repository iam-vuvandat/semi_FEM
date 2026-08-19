import os
import paths
import numpy as np
import matplotlib.pyplot as plt
import scienceplots

from src.core.core_class.utils.for_data_processor.update_record import update_record
from src.core.core_class.utils.for_data_processor.apply_jounal_style import apply_journal_style
from src.core.core_class.utils.for_data_processor.plot_flux_linkage import plot_flux_linkage
from src.core.core_class.utils.for_data_processor.plot_flux_linkage_no_load import plot_flux_linkage_no_load
from src.core.core_class.utils.for_data_processor.plot_back_emf import plot_back_emf
from src.core.core_class.utils.for_data_processor.plot_back_emf_no_load import plot_back_emf_no_load
from src.core.core_class.utils.for_data_processor.plot_current import plot_current
from src.core.core_class.utils.for_data_processor.plot_torque import plot_torque
from src.core.core_class.utils.for_data_processor.plot_axial_force import plot_axial_force
from src.core.core_class.utils.for_data_processor.plot_axial_force_no_load import plot_axial_force_no_load
from src.core.core_class.utils.for_data_processor.plot_cogging_torque import plot_cogging_torque
from src.core.core_class.utils.for_data_processor.plot_mechanical_power import plot_mechanical_power
from src.core.core_class.utils.for_data_processor.plot_inductance_map import plot_inductance_map
from src.core.core_class.utils.for_data_processor.plot_airgap_flux_density import plot_airgap_flux_density
from src.core.core_class.utils.for_data_processor.plot_airgap_flux_density_no_load import plot_airgap_flux_density_no_load
from src.core.core_class.utils.for_data_processor.create_report import create_report
from src.core.core_class.utils.for_data_processor.plot_power_at_varying_current import plot_power_at_varying_current
from src.core.core_class.utils.for_data_processor.plot_solver_history import plot_solver_history


class DataProcessor:
    def __init__(self, motor):
        self.motor = motor
        self.plot_style = apply_journal_style()

    def update_record(self):
        return update_record(data_processor=self)

    def plot_airgap_flux_density(self, horizontal_axis="mechanical_position", show_fem=True, show_harmonic=True, plot=True, figsize=None):
        return plot_airgap_flux_density(data_processor=self, horizontal_axis=horizontal_axis, 
                                        show_fem=show_fem, show_harmonic=show_harmonic, plot=plot, figsize=figsize)

    def plot_airgap_flux_density_no_load(self, horizontal_axis="mechanical_position", show_fem=True, show_harmonic=True, plot=True, figsize=None):
        return plot_airgap_flux_density_no_load(data_processor=self, horizontal_axis=horizontal_axis, 
                                                show_fem=show_fem, show_harmonic=show_harmonic, plot=plot, figsize=figsize)
    
    def plot_flux_linkage(self, horizontal_axis="mechanical_position", show_fem=True, 
                          show_dq=False, show_all_phase=False, show_harmonic=True, plot=True, figsize=None):
        return plot_flux_linkage(data_processor=self, horizontal_axis=horizontal_axis, 
                                 show_fem=show_fem, show_dq=show_dq, 
                                 show_all_phase=show_all_phase, show_harmonic=show_harmonic, plot=plot, figsize=figsize)

    def plot_flux_linkage_no_load(self, horizontal_axis="mechanical_position", show_fem=True, 
                                  show_dq=False, show_all_phase=False, show_harmonic=True, plot=True, figsize=None):
        return plot_flux_linkage_no_load(data_processor=self, horizontal_axis=horizontal_axis, 
                                         show_fem=show_fem, show_dq=show_dq, 
                                         show_all_phase=show_all_phase, show_harmonic=show_harmonic, plot=plot, figsize=figsize)

    def plot_back_emf(self, horizontal_axis="mechanical_position", show_fem=True, 
                      show_all_phases=False, show_harmonic=True, plot=True, figsize=None):
        return plot_back_emf(data_processor=self, horizontal_axis=horizontal_axis, 
                             show_fem=show_fem, show_all_phases=show_all_phases, show_harmonic=show_harmonic, plot=plot, figsize=figsize)
    
    def plot_back_emf_no_load(self, horizontal_axis="mechanical_position", show_fem=True, 
                              show_all_phases=False, show_harmonic=True, plot=True, figsize=None):
        return plot_back_emf_no_load(data_processor=self, horizontal_axis=horizontal_axis, 
                                     show_fem=show_fem, show_all_phases=show_all_phases, show_harmonic=show_harmonic, plot=plot, figsize=figsize)
    
    def plot_current(self, horizontal_axis="mechanical_position", show_fem=True, plot=True, figsize=None):
        return plot_current(data_processor=self, horizontal_axis=horizontal_axis, 
                            show_fem=show_fem, plot=plot, figsize=figsize)

    def plot_torque(self, horizontal_axis="mechanical_position", show_fem=True, plot=True, revert=True, figsize=None):
        return plot_torque(data_processor=self, horizontal_axis=horizontal_axis, 
                           show_fem=show_fem, plot=plot, revert=revert, figsize=figsize)
    
    def plot_axial_force(self, horizontal_axis="mechanical_position", show_fem=True, plot=True, revert=True, figsize=None):
        return plot_axial_force(data_processor=self, horizontal_axis=horizontal_axis, 
                                show_fem=show_fem, plot=plot, revert=revert, figsize=figsize)
    
    def plot_axial_force_no_load(self, horizontal_axis="mechanical_position", show_fem=True, plot=True, revert=True, figsize=None):
        return plot_axial_force_no_load(data_processor=self, horizontal_axis=horizontal_axis, 
                                        show_fem=show_fem, plot=plot, revert=revert, figsize=figsize)
    
    def plot_cogging_torque(self, horizontal_axis="mechanical_position", show_fem=True, plot=True, revert=True, num_periods=1, figsize=None):
        return plot_cogging_torque(data_processor=self, horizontal_axis=horizontal_axis, 
                                   show_fem=show_fem, plot=plot, revert=revert, num_periods=num_periods, figsize=figsize)

    def plot_mechanical_power(self, horizontal_axis="mechanical_position", show_fem=True, plot=True, revert=True, figsize=None):
        return plot_mechanical_power(data_processor=self, horizontal_axis=horizontal_axis, 
                                     show_fem=show_fem, plot=plot, revert=revert, figsize=figsize)

    def plot_inductance_map(self, plot=True):
        return plot_inductance_map(data_processor=self, plot=plot)
    
    def plot_power_at_varying_current(self, plot=True, figsize=None):
        return plot_power_at_varying_current(data_processor=self, plot=plot, figsize=figsize)

    def create_report(self, path=None):
        return create_report(data_processor=self, path=path)

    def plot_solver_history(self, step_index=0, plot_residual=True, plot_relaxation_factor=True, plot_relaxation_decay=False, plot=False, plot_convergence_threshold=True):
        return plot_solver_history(
            data_processor=self, 
            step_index=step_index, 
            plot_residual=plot_residual, 
            plot_relaxation_factor=plot_relaxation_factor, 
            plot_relaxation_decay=plot_relaxation_decay,
            plot=plot,
            plot_convergence_threshold=plot_convergence_threshold
        )