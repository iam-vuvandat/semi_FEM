import numpy as np

def rotate_point_z(point, theta_deg):
    x, y, z = point
    theta_rad = np.radians(theta_deg)
    
    x_new = x * np.cos(theta_rad) - y * np.sin(theta_rad)
    y_new = x * np.sin(theta_rad) + y * np.cos(theta_rad)
    z_new = z
    
    return [x_new, y_new, z_new]