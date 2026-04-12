def setup_axial_force_calculation(m3d):
    oModule = m3d.odesign.GetModule("MaxwellParameterSetup")
    oModule.AssignForce(
        [
            "NAME:Axial_Force",
            "Reference CS:="     , "Global",
            "Is Virtual:="       , True,
            "Objects:="          , ["Band"]
        ])
    
    print(f"\033[92msetup_axial_force_calculation return: True\033[0m")
    return True