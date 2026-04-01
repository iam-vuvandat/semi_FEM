import paths
import numpy as np
import matplotlib.pyplot as plt
import scienceplots



from src.core.core_class.utils.for_data_processor.apply_jounal_style import apply_journal_style
from src.core.core_class.utils.for_data_processor.plot_flux_linkage import plot_flux_linkage
from src.core.core_class.utils.for_data_processor.plot_back_emf import plot_back_emf
from src.core.core_class.utils.for_data_processor.plot_back_emf_line import plot_back_emf_line
from src.core.core_class.utils.for_data_processor.plot_current import plot_current
from src.core.core_class.utils.for_data_processor.plot_torque import plot_torque
from src.core.core_class.utils.for_data_processor.plot_axial_force import plot_axial_force
from src.core.core_class.utils.for_data_processor.plot_cogging_torque import plot_cogging_torque
from src.core.core_class.utils.for_data_processor.plot_mechanical_power import plot_mechanical_power
from src.core.core_class.utils.for_data_processor.plot_inductance_map import plot_inductance_map

from src.core.core_class.utils.for_data_processor.compare_flux_linkage import compare_flux_linkage
from src.core.core_class.utils.for_data_processor.compare_back_emf import compare_back_emf
from src.core.core_class.utils.for_data_processor.compare_back_emf_line import compare_back_emf_line
from src.core.core_class.utils.for_data_processor.compare_torque import compare_torque
from src.core.core_class.utils.for_data_processor.compare_mechanical_power import compare_mechanical_power

from src.core.solver.utils.synchronize_signals import synchronize_signals
from mpl_toolkits.mplot3d import Axes3D


class DataProcessor:
    def __init__(self, motor):
        self.motor = motor
        self.plot_style = apply_journal_style()
    


    def plot_flux_linkage(self,horizontal_axis = "mechanical_position"):
        plot_flux_linkage(data_processor= self, horizontal_axis= horizontal_axis)

    def plot_back_emf(self,horizontal_axis = "mechanical_position"):
        plot_back_emf(data_processor= self, horizontal_axis= horizontal_axis)
    
    def plot_back_emf_line(self,horizontal_axis = "mechanical_position"):
        plot_back_emf_line(data_processor= self, horizontal_axis= horizontal_axis)

    def plot_current(self,horizontal_axis = "mechanical_position"):
        plot_current(data_processor= self, horizontal_axis= horizontal_axis)

    def plot_torque(self,horizontal_axis = "mechanical_position"):
        plot_torque(data_processor= self, horizontal_axis= horizontal_axis)
    
    def plot_axial_force(self,horizontal_axis = "mechanical_position"):
        plot_axial_force(data_processor= self, horizontal_axis= horizontal_axis)
    
    def plot_cogging_torque(self,horizontal_axis = "mechanical_position"):
        plot_cogging_torque(data_processor= self, horizontal_axis= horizontal_axis)

    def plot_mechanical_power(self,horizontal_axis = "mechanical_position"):
        plot_mechanical_power(data_processor= self, horizontal_axis= horizontal_axis)

    def plot_inductance_map(self):
        plot_inductance_map(data_processor= self)




    def compare_flux_linkage(self,horizontal_axis = "mechanical_position", show_dq_axis = True, show_all_phases = True ):
        compare_flux_linkage(data_processor= self, horizontal_axis= horizontal_axis, show_dq_axis= show_dq_axis, show_all_phases= show_all_phases)

    def compare_back_emf(self,horizontal_axis = "mechanical_position", show_all_phases = True):
        compare_back_emf(data_processor= self, horizontal_axis= horizontal_axis, show_all_phases= show_all_phases)
    
    def compare_back_emf_line(self,horizontal_axis = "mechanical_position", show_all_phases = True):
        compare_back_emf_line(data_processor= self, horizontal_axis= horizontal_axis, show_all_phases= show_all_phases)
        
    def compare_torque(self,horizontal_axis = "mechanical_position"):
        compare_torque(data_processor= self, horizontal_axis= horizontal_axis)

    def compare_mechanical_power(self,horizontal_axis = "mechanical_position"):
        compare_mechanical_power(data_processor= self, horizontal_axis= horizontal_axis)


    def synchronize_signal(self, data_true, data_pred, is_periodic=True, half_open_interval=True):
        synchronize_signals(data_true = data_true, data_pred = data_pred, is_periodic= is_periodic, half_open_interval= half_open_interval)

    
    