import re

import numpy as np
from src.core.core_class.utils.for_vectorized_elements.create_vectorized_elements import create_vectorized_elements

class VectorizedElements:
    def __init__(self,reluctance_network):
        self.init_vectorized_elements(reluctance_network = reluctance_network)
        


    def init_vectorized_elements(self,reluctance_network):
        create_vectorized_elements(vectorized_elements= self, reluctance_network= reluctance_network)
    

