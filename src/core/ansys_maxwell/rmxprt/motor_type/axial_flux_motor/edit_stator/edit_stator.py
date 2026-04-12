def edit_stator(rmxprt, motor = None,poles=4, slots=16, circuit_type="Y3", slot_type="4", pos_control=True):
    
    poles = motor.geometry_data.rotor.pole_number
    slots = motor.geometry_data.stator.slot_number
    slot_type = "4"

    oDesign = rmxprt.odesign
    oEditor = oDesign.SetActiveEditor("Machine")
    
    oEditor.ChangeProperty(
        [
            "NAME:AllTabs",
            [
                "NAME:Machine",
                [
                    "NAME:PropServers", 
                    "Stator"
                ],
                [
                    "NAME:ChangedProps",
                    [
                        "NAME:Number of Poles",
                        "Value:=", str(poles)
                    ],
                    [
                        "NAME:Number of Slots",
                        "Value:=", str(slots)
                    ],
                    [
                        "NAME:Circuit Type",
                        "CircuitType:=", circuit_type
                    ],
                    [
                        "NAME:Slot Type",
                        "SlotType:=", slot_type
                    ],
                    [
                        "NAME:Position Control",
                        "Value:=", pos_control
                    ]
                ]
            ]
        ])
    return True