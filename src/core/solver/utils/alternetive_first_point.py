import numpy as np 

def alternetive_first_point(data, remove_last_point = True, last_row_is_position = True):
    if last_row_is_position:
        data[:-1, 0] = data[:-1, -1]
        
        if remove_last_point:
            data = data[:, :-1]
            
        return data
    else:
        data[:, 0] = data[:, -1]
        
        if remove_last_point:
            data = data[:, :-1]
            
        return data