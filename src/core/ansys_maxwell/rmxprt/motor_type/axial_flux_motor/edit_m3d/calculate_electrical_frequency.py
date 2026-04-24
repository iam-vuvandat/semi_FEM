def calculate_electrical_frequency(rated_speed_rpm, poles, return_string=False):
    frequency = (rated_speed_rpm * poles) / 120
    
    result = f"{frequency}Hz" if return_string else frequency
    
    print(f"\033[92mcalculate_electrical_frequency return: {result}\033[0m")
    return result