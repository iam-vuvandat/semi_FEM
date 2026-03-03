import numpy as np

def update_reluctance(vectorized_elements):
    vectorized_elements.reluctance = vectorized_elements.vacuum_reluctance / vectorized_elements.relative_permeability