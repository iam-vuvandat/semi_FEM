def edit_rotor(rmxprt, motor):
    poles = motor.geometry_data.rotor.pole_number
    d_outer = motor.geometry_data.rotor.rotor_lam_dia * 1e3
    d_inner = motor.geometry_data.rotor.shaft_hole_diameter * 1e3
    length = motor.geometry_data.rotor.rotor_length * 1e3
    iron_material = motor.material_data.iron_type

    oDesign = rmxprt.odesign
    oEditor = oDesign.SetActiveEditor("Machine")

    # 1. Chinh so cuc (dat len dau theo Recorded Script)
    oEditor.ChangeProperty(
        [
            "NAME:AllTabs",
            [
                "NAME:Machine",
                [
                    "NAME:PropServers", 
                    "Rotor"
                ],
                [
                    "NAME:ChangedProps",
                    [
                        "NAME:Number of Poles",
                        "Value:=", str(poles)
                    ]
                ]
            ]
        ])

    # 2. Chinh thong so hinh hoc va vat lieu loi Rotor
    oEditor.ChangeProperty(
        [
            "NAME:AllTabs",
            [
                "NAME:Machine",
                [
                    "NAME:PropServers", 
                    "Rotor:Core"
                ],
                [
                    "NAME:ChangedProps",
                    [
                        "NAME:Outer Diameter",
                        "Value:=", str(d_outer) + "mm"
                    ],
                    [
                        "NAME:Inner Diameter",
                        "Value:=", str(d_inner) + "mm"
                    ],
                    [
                        "NAME:Length",
                        "Value:=", str(length) + "mm"
                    ],
                    [
                        "NAME:Stacking Factor",
                        "Value:=", "1"
                    ],
                    [
                        "NAME:Steel Type",
                        "Material:=", iron_material
                    ]
                ]
            ]
        ])
    return True