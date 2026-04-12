def edit_motion_setting(m3d, motor):
    speed = motor.mechanical_data.shaft_speed
    oModule = m3d.odesign.GetModule("ModelSetup")
    
    oModule.Edit("MotionSetup1", 
        [
            "NAME:Data",
            "Move Type:="       , "Rotate",
            "Coordinate System:="   , "Global",
            "Axis:="            , "Z",
            "Is Positive:="     , True,
            "InitPos:="         , "0deg",
            "HasRotateLimit:="  , False,
            "NonCylindrical:="  , False,
            "Consider Mechanical Transient:=", False,
            "Angular Velocity:="    , str(speed) + "rpm"
        ])
    
    # In màu xanh lá cây (ANSI \033[92m)
    print(f"\033[92medit_motion_setting return: True (Speed: {speed}rpm)\033[0m")
    
    return True