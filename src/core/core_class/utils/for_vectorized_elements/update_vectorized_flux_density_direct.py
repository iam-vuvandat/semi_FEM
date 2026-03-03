import numpy as np

def update_vectorized_flux_density(vectorized_elements):
    # Thuc hien phep chia truc tiep de toi uu hieu nang
    vectorized_elements.flux_density_direct = vectorized_elements.flux_direct / vectorized_elements.section_area