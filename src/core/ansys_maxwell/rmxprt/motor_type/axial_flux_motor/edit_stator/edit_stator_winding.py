def edit_stator_winding(rmxprt, motor):
    layers = motor.winding_data.winding_layer
    parallel_branches = motor.winding_data.parallel_path
    conductors_per_slot = motor.winding_data.turns * layers
    coil_pitch = motor.winding_data.throw
    
    oDesign = rmxprt.odesign
    oEditor = oDesign.SetActiveEditor("Machine")
    
    oEditor.ChangeProperty(
        [
            "NAME:AllTabs",
            [
                "NAME:Winding",
                [
                    "NAME:PropServers", 
                    "Stator:Winding"
                ],
                [
                    "NAME:ChangedProps",
                    [
                        "NAME:Winding Layers",
                        "Value:=", str(layers)
                    ],
                    [
                        "NAME:Winding Type",
                        "WindingType:=", "Whole-Coiled"
                    ],
                    [
                        "NAME:Parallel Branches",
                        "Value:=", str(parallel_branches)
                    ],
                    [
                        "NAME:Conductors per Slot",
                        "Value:=", str(conductors_per_slot)
                    ],
                    [
                        "NAME:Coil Pitch",
                        "Value:=", str(coil_pitch)
                    ],
                    [
                        "NAME:Wire Wrap",
                        "Value:=", "2mm"
                    ],
                    [
                        "NAME:Conductor Type",
                        "Material:=", "copper"
                    ],
                    [
                        "NAME:Wire Size",
                        "WireSizeWireDiameter:=", "3.459mm",
                        "WireSizeGauge:="   , "7",
                        "WireSizeWireWidth:="   , "0mm",
                        "WireSizeWireThickness:=", "0mm",
                        "WireSizeMixedWireRectType:=", False,
                        ["NAME:WireSizeMixedDiameter"],
                        ["NAME:WireSizeMixedWidth"],
                        ["NAME:WireSizeMixedThickness"],
                        ["NAME:WireSizeMixedThicknessMixedFillet"],
                        ["NAME:WireSizeMixedThicknessMixedNumber"]
                    ]
                ]
            ]
        ])
    return True