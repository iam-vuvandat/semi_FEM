def update_record(data_processor):
    """
    Executes post-processing calculations on simulation data using the provided
    data_processor instance and updates the motor record object with mechanical 
    power relative errors.
    """
    motor = data_processor.motor
    record = motor.record

    has_pow_mbgrn = hasattr(record, "average_mechanical_power") and record.average_mechanical_power is not None
    has_pow_fem = hasattr(record, "average_mechanical_power_fem") and record.average_mechanical_power_fem is not None

    if has_pow_mbgrn and has_pow_fem:
        val_pow_mbgrn = record.average_mechanical_power
        val_pow_fem = record.average_mechanical_power_fem
        
        if val_pow_fem != 0:
            record.mechanical_power_average_error = (abs(val_pow_mbgrn - val_pow_fem) / val_pow_fem) * 100
        else:
            record.mechanical_power_average_error = 0.0
    else:
        record.mechanical_power_average_error = None

    return True