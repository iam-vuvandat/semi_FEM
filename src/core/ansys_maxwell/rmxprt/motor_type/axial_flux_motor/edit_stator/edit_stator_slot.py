def edit_stator_slot(rmxprt, motor):
    """
    Ham thiet lap thong so hinh hoc ranh (Slot) cho Stator.
    Phai tat Auto Design truoc de cac thuoc tinh nhu Bs1, Hs2 xuat hien.
    """
    # Trich xuat du lieu tu object motor (m -> mm)
    bs0 = motor.geometry_data.stator.slot_opening * 1e3
    bs1 = motor.geometry_data.stator.slot_width * 1e3
    bs2 = motor.geometry_data.stator.slot_width * 1e3
    hs0 = motor.geometry_data.stator.tooth_tip_depth * 1e3
    hs1 = 0.5 
    hs2 = motor.geometry_data.stator.slot_depth * 1e3
    rs  = motor.geometry_data.stator.slot_corner_radius * 1e3

    oDesign = rmxprt.odesign
    oEditor = oDesign.SetActiveEditor("Machine")
    
    # Buoc 1: Bat buoc phai bo tich 'Auto Design' (trong hinh dang la True)
    oEditor.ChangeProperty(
        [
            "NAME:AllTabs",
            [
                "NAME:Slot",
                ["NAME:PropServers", "Stator:Core:Slot"],
                [
                    "NAME:ChangedProps",
                    ["NAME:Auto Design", "Value:=", False]
                ]
            ]
        ])

    # Buoc 2: Nap cac thong so theo hinh anh ban cung cap va cac thong so hinh hoc con lai
    oEditor.ChangeProperty(
        [
            "NAME:AllTabs",
            [
                "NAME:Slot",
                ["NAME:PropServers", "Stator:Core:Slot"],
                [
                    "NAME:ChangedProps",
                    ["NAME:Hs0", "Value:=", str(hs0) + "mm"],
                    ["NAME:Hs1", "Value:=", str(hs1) + "mm"],
                    ["NAME:Hs2", "Value:=", str(hs2) + "mm"],
                    ["NAME:Bs0", "Value:=", str(bs0) + "mm"],
                    ["NAME:Bs1", "Value:=", str(bs1) + "mm"],
                    ["NAME:Bs2", "Value:=", str(bs2) + "mm"],
                    ["NAME:Rs",  "Value:=", str(rs) + "mm"]
                ]
            ]
        ])
    return True