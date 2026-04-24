def winding_direction_setup(motor, m3d, point_out=True):
    oModule = m3d.odesign.GetModule("BoundarySetup")
    
    # Lấy toàn bộ danh sách các excitations trong design
    all_excitations = list(oModule.GetExcitations())
    
    # Lọc các terminal dựa trên quy tắc đặt tên bắt đầu bằng "Ph" (e.g., PhA_0, PhB_1,...)
    terminal_list = [name for name in all_excitations if name.startswith("Ph")]
    
    # Lấy số vòng dây từ dữ liệu motor
    conductor_num = str(motor.winding_data.conductor_number)
    
    for terminal_name in terminal_list:
        # Tự động xác định tên Winding dựa trên ký tự pha (e.g., PhA_0 -> PhaseA)
        phase_char = terminal_name[2]
        winding_name = f"Phase{phase_char}"
        
        oModule.Edit(terminal_name, 
            [
                f"NAME:{terminal_name}",
                "ParentBndID:="     , winding_name,
                "Conductor number:="    , conductor_num,
                "Winding:="     , winding_name,
                "Point out of terminal:=", point_out
            ])
            
    print(f"\033[94mSuccessfully updated direction for {len(terminal_list)} terminals.\033[0m")