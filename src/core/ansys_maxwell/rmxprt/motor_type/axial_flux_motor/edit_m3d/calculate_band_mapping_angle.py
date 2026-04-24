import math

def calculate_band_mapping_angle(delta_angle, return_string, minimum_angle=math.radians(1), maximum_angle=math.radians(3)):
    k = math.ceil(minimum_angle / delta_angle)
    band_mapping_angle = k * delta_angle
    
    if band_mapping_angle > maximum_angle:
        band_mapping_angle = maximum_angle
        
    print(f"\033[94mdelta_angle: {math.degrees(delta_angle)} deg, calculate_band_mapping_angle return: {math.degrees(band_mapping_angle)} deg\033[0m")
    
    if return_string:
        return f"{math.degrees(band_mapping_angle)}deg"
    return band_mapping_angle