def change_motor_type(rmxprt, motor = None, motor_type="Axial-Flux Rotor"):
    
    airgap_length = motor.geometry_data.rotor.airgap * 1e3 # unit:mm 

    oDesign = rmxprt.odesign
    oEditor = oDesign.SetActiveEditor("Machine")
    
    # Buoc 1: Thay doi Structure truoc de Ansys kich hoat menu Axial
    oEditor.ChangeProperty(
        [
            "NAME:AllTabs",
            [
                "NAME:Machine",
                [
                    "NAME:PropServers", 
                    "Machine"
                ],
                [
                    "NAME:ChangedProps",
                    [
                        "NAME:Structure",
                        "Value:=", motor_type
                    ]
                ]
            ]
        ])

    # Buoc 2: Sau khi Structure da duoc xac nhan, moi thay doi cac thong so dac thu
    oEditor.ChangeProperty(
        [
            "NAME:AllTabs",
            [
                "NAME:Machine",
                [
                    "NAME:PropServers", 
                    "Machine"
                ],
                [
                    "NAME:ChangedProps",
                    [
                        "NAME:Stator Type",
                        "Value:=", "AXIAL_AC"
                    ],
                    [
                        "NAME:Rotor Type",
                        "Value:=", "AXIAL_PM"
                    ],
                    [
                        "NAME:Air Gap Length",
                        "Value:=", str(airgap_length) + "mm"
                    ]
                ]
            ]
        ])
    return True