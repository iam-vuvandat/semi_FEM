from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_m3d.winding_direction_setup import winding_direction_setup

def edit_excitation(m3d, motor, disable_excitation=False):
    
    motor.update_maxwell_setting()
    current_functions = motor.maxwell_export_option.current_function_for_rmxprt_export
    oModule = m3d.odesign.GetModule("BoundarySetup")
    
    n_phases = int(motor.winding_data.phase)
    turns_val = str(motor.winding_data.turns)

    for i in range(n_phases):
        phase_char = chr(65 + i) 
        winding_name = f"Phase{phase_char}"
        terminal_name = f"Ph{phase_char}_{i}"
        
        # Logic kiem tra disable_excitation
        if disable_excitation:
            current_eq = "0A"
        else:
            current_eq = current_functions[i]

        oModule.Edit(winding_name, 
            [
                f"NAME:{winding_name}",
                "Type:="                , "Current",
                "IsSolid:="             , False,
                "Current:="             , current_eq,
                "Resistance:="          , "0ohm",
                "Inductance:="          , "0",
                "Voltage:="             , "0",
                "ParallelBranchesNum:=" , "1"
            ])

        oModule.Edit(terminal_name, 
            [
                f"NAME:{terminal_name}",
                "ParentBndID:="         , winding_name,
                "Conductor number:="    , turns_val,
                "Winding:="             , winding_name,
                "Point out of terminal:=", True
            ])

    status_msg = "DISABLED (0A)" if disable_excitation else "ENABLED"
    print(f"\033[92medit_excitation return: True ({n_phases} phases {status_msg}, turns={turns_val})\033[0m")
    return True