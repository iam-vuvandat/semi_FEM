def edit_stator_core(rmxprt, motor):
    # Chuyen doi tu m sang mm theo dung ten bien trong AxialFluxMotorType1
    d_outer = motor.geometry_data.stator.stator_lam_dia * 1e3
    d_inner = motor.geometry_data.stator.stator_bore_dia * 1e3
    length = motor.geometry_data.stator.stator_length * 1e3
    
    # Lay vat lieu tu material_data
    material = motor.material_data.iron_type
    stacking_factor = 1 # Gia tri mac dinh

    oDesign = rmxprt.odesign
    oEditor = oDesign.SetActiveEditor("Machine")
    
    oEditor.ChangeProperty(
        [
            "NAME:AllTabs",
            [
                "NAME:Machine",
                ["NAME:PropServers", "Stator:Core"],
                [
                    "NAME:ChangedProps",
                    ["NAME:Outer Diameter", "Value:=", str(d_outer) + "mm"],
                    ["NAME:Inner Diameter", "Value:=", str(d_inner) + "mm"],
                    ["NAME:Length", "Value:=", str(length) + "mm"],
                    ["NAME:Stacking Factor", "Value:=", str(stacking_factor)],
                    ["NAME:Steel Type", "Material:=", material]
                ]
            ]
        ])
    return True