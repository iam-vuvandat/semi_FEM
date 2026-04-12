from ansys.aedt.core import Maxwell3d

def edit_solver(rmxprt, motor):
    speed = motor.mechanical_data.shaft_speed
    i_rms = motor.drive_data.i_rms
    
    oDesign = rmxprt.odesign
    
    # 1. Thiet lap Nguon dong (Power Source)
    oDesign.SetDesignSettings(
        [
            "NAME:Design Settings Data",
            "Table:=", "Power Source",
            [
                "NAME:Input",
                "Value:=", str(i_rms) + "A"
            ],
            "Control:=", "Current"
        ])

    # 2. Thiet lap Analysis Setup (Setup1)
    oModule = oDesign.GetModule("AnalysisSetup")
    oModule.InsertSetup("GRM", 
        [
            "NAME:Setup1",
            "Enabled:=", True,
            [
                "NAME:MeshLink",
                "ImportMesh:=", False
            ],
            "RatedOutputPower:=", "1500W",
            "RatedVoltage:=", "400V",
            "RatedSpeed:=", str(speed) + "rpm",
            "OperatingTemperature:=", "60cel",
            "OperationType:=", "Motor",
            "LoadType:=", "ConstSpeed",
            "RatedPowerFactor:=", "1.0",
            "Frequency:=", "60Hz",
            "CapacitivePowerFactor:=", False
        ])

    # 3. Giai (Analyze)
    oDesign.Analyze("Setup1")
    
    # 4. Xuat sang Maxwell 3D
    # Lenh nay se tao ra mot Design moi mac dinh ten la "Maxwell3DDesign1"
    oModule.CreateMaxwellDesign(1, "Setup1", "")
    
    # 5. Ket noi vao thiet ke Maxwell 3D vua tao va return
    # Sua loi: Dung 'project' va 'design' lam keyword argument
    m3d = Maxwell3d(project=rmxprt.project_name, design="Maxwell3DDesign1")
    
    print(f"\033[93medit_solver return: {m3d}\033[0m")
    
    return m3d