import numpy as np
import math
from scipy.interpolate import CubicSpline, PchipInterpolator

PI = math.pi

class Air:
    def __init__(self, name="default"):
        self.name = name
        self.relative_permeance = 1.


class Magnet:
    def __init__(self, name: str):
        self.name = name
        if name == "N30UH":
            self.relative_permeance = 1.05
            self.coercivity = 852000.0
        else:
            raise ValueError(f"Magnet '{name}' not found")


import numpy as np
from scipy.interpolate import PchipInterpolator

class Iron:
    def __init__(self, name: str):
        self.name = name
        if name == "M350-50A":
            self.B_H_curve = {
                "B_data": np.array([
                    0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,
                    1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9,
                    1.956, 2.1, 2.2, 2.2701, 2.4
                ]),
                "H_data": np.array([
                    0.0, 34.8, 46.0, 53.7, 60.6, 67.4, 74.6, 82.6, 91.8, 103.0,
                    119.0, 141.0, 178.0, 250.0, 455.0, 1180.0, 3020.0, 6100.0,
                    10700.0, 25000.0, 35000.0, 75000.0, 115000.0, 150000.0, 229580.0
                ])
            }
        else:
            raise ValueError(f"Iron '{name}' not found")
        
        self.smooth_BH_curve()

    def smooth_BH_curve(self, num_points=3000):
        B_orig = self.B_H_curve["B_data"]
        H_orig = self.B_H_curve["H_data"]
        
        B_smooth = np.linspace(B_orig.min(), B_orig.max(), num_points)
        interpolator = PchipInterpolator(B_orig, H_orig)
        H_smooth = interpolator(B_smooth)
        
        self.B_H_curve["B_data"] = B_smooth
        self.B_H_curve["H_data"] = H_smooth


class MaterialDataBase:
    def __init__(self, air="default", magnet_type="N30UH", iron_type="M350-50A"):
        self.air = Air(air)
        self.magnet = Magnet(magnet_type)
        self.iron = Iron(iron_type)
