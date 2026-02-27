import numpy as np

def get_volume(element = None):
    if element is None:
        return 0.0
    
    else:
        section_area = element.section_area[0,2]
        height = element.length[0,2]
        return float(section_area * height)