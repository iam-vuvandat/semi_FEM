def edit_magnet(rmxprt, motor):
    """
    Ham thiet lap thong so Nam cham (Magnet) dua tren AxialFluxMotorType1.
    """
    # Tinh toan thong so tu class motor
    embrace = motor.geometry_data.rotor.magnet_arc / 180.0
    m_length = motor.geometry_data.rotor.magnet_depth * 1e3    # radial width
    m_thickness = motor.geometry_data.rotor.magnet_length * 1e3 # axial thickness
    magnet_material = motor.material_data.magnet_type

    oDesign = rmxprt.odesign
    oEditor = oDesign.SetActiveEditor("Machine")
    
    oEditor.ChangeProperty(
        [
            "NAME:AllTabs",
            [
                "NAME:Pole",
                [
                    "NAME:PropServers", 
                    "Rotor:Core:Pole"
                ],
                [
                    "NAME:ChangedProps",
                    [
                        "NAME:Embrace",
                        "Value:=", str(embrace)
                    ],
                    [
                        "NAME:Magnet Type",
                        "Material:=", magnet_material
                    ],
                    [
                        "NAME:Magnet Length",
                        "Value:=", str(m_length) + "mm"
                    ],
                    [
                        "NAME:Magnet Thickness",
                        "Value:=", str(m_thickness) + "mm"
                    ]
                ]
            ]
        ])
    return True