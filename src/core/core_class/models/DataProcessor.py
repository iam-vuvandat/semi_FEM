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
from mpl_toolkits.mplot3d import Axes3D

class DataProcessor:
    def __init__(self, motor):
        self.motor = motor
        self.plot_style = apply_journal_style()

    def update_record(self):
        return update_record(data_processor= self)

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
    def plot_flux_linkage_no_load(self, horizontal_axis="mechanical_position", show_fem=True, 
                          show_dq=False, show_all_phase=False, plot=True):
        return plot_flux_linkage_no_load(data_processor=self, horizontal_axis=horizontal_axis, 
                                 show_fem=show_fem, show_dq=show_dq, 
                                 show_all_phase=show_all_phase, plot=plot)

    def plot_back_emf(self, horizontal_axis="mechanical_position", show_fem=True, 
                      show_all_phases=False, plot=True):
        return plot_back_emf(data_processor=self, horizontal_axis=horizontal_axis, 
                             show_fem=show_fem, show_all_phases=show_all_phases, plot=plot)
    
    def plot_back_emf_no_load(self, horizontal_axis="mechanical_position", show_fem=True, 
                      show_all_phases=False, plot=True):
        return plot_back_emf_no_load(data_processor=self, horizontal_axis=horizontal_axis, 
                             show_fem=show_fem, show_all_phases=show_all_phases, plot=plot)
    
    def plot_current(self, horizontal_axis="mechanical_position", show_fem=False, plot=True):
        return plot_current(data_processor=self, horizontal_axis=horizontal_axis, 
                            show_fem=show_fem, plot=plot)

    def plot_torque(self, horizontal_axis="mechanical_position", show_fem=True, plot=True, revert=False):
        return plot_torque(data_processor=self, horizontal_axis=horizontal_axis, 
                           show_fem=show_fem, plot=plot, revert=revert)
    
    def plot_axial_force(self, horizontal_axis="mechanical_position", show_fem=True, plot=True, revert=True):
        return plot_axial_force(data_processor=self, horizontal_axis=horizontal_axis, 
                                show_fem=show_fem, plot=plot, revert=revert)
    
    def plot_axial_force_no_load(self, horizontal_axis="mechanical_position", show_fem=True, plot=True, revert=True):
        return plot_axial_force_no_load(data_processor=self, horizontal_axis=horizontal_axis, 
                                show_fem=show_fem, plot=plot, revert=revert)
    
    def plot_cogging_torque(self, horizontal_axis="mechanical_position", show_fem=True, plot=True, revert=False, num_periods=1):
        return plot_cogging_torque(data_processor=self, horizontal_axis=horizontal_axis, 
                                   show_fem=show_fem, plot=plot, revert=revert, num_periods=num_periods)

    def plot_mechanical_power(self, horizontal_axis="mechanical_position", show_fem=True, plot=True, revert=False):
        return plot_mechanical_power(data_processor=self, horizontal_axis=horizontal_axis, 
                                     show_fem=show_fem, plot=plot, revert=revert)

    def plot_inductance_map(self, plot=True):
        return plot_inductance_map(data_processor=self, plot=plot)
    
    def plot_power_at_varying_current(self, plot= True):
        return plot_power_at_varying_current(data_processor=self, plot=plot)

    def create_report(self):
        return create_report(data_processor= self)