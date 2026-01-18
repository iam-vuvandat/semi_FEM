import numpy as np

class ElementLite:
    __slots__ = [ 
        'position', 
        'material', 
        'magnetization_direction', 
        'flux_density_average', 
        'symmetry_factor'
    ]

    def __init__(self, element):
        self.position = element.position
        self.material = str(element.material)
        self.symmetry_factor = getattr(element, 'symmetry_factor', 1)
        
        if element.magnetization_direction is not None:
            self.magnetization_direction = np.copy(element.magnetization_direction)
        else:
            self.magnetization_direction = None
            
        if element.flux_density_average is not None:
            self.flux_density_average = np.copy(element.flux_density_average)
        else:
            self.flux_density_average = None

    def to_dict(self):
        return {slot: getattr(self, slot) for slot in self.__slots__}