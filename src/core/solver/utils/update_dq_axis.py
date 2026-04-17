from src.core.solver.utils.convert_to_dq import convert_to_dq

def update_dq_axis(data_full, pole_pairs):
    current_position = data_full[-1,:]
    data = data_full[2:-1,:]
    dq_updated = convert_to_dq(value = data, poles = pole_pairs, current_position = current_position)

    data_full[0:2,:] = dq_updated[:-1,:]

    return data_full