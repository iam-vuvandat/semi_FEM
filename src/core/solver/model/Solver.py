import numpy as np
from src.core.solver.core.solve import solve
from src.core.solver.utils.find_relaxation_decay import find_relaxation_decay

class Solver:
    def __init__ (self,reluctance_network):
        self.reluctance_network = reluctance_network
        self.convergence_settings = self.reluctance_network.calculation_data.convergence_settings
        self.convergence_settings.relaxation_history = np.array([np.linspace(0.1, 1.0, 10), np.zeros(10)])
        
    def solve(self):
        solve(solver = self)

    def find_relaxation_decay(self):
        find_relaxation_decay(solver = self)
