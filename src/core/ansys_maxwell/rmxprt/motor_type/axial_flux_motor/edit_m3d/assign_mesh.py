import numpy as np
import math
from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_m3d.calculate_band_mapping_angle import calculate_band_mapping_angle



def assign_mesh(m3d, motor):
    oModule = m3d.odesign.GetModule("MeshSetup")
    
    motor.require("mechanical")
    mesh_setting = motor.maxwell_export_option.custom_option.mesh_setting

    # Trich xuat va tinh toan
    cogging_period_mech = motor.mechanical.cogging_period_mech 
    point_number_simulation = motor.calculation_data.general_options.n_point

    # Kiem tra tranh chia cho -1 hoac gia tri -1 tu n_point
    if point_number_simulation != -1 and point_number_simulation != 0:
        minimum_step_rotate = cogging_period_mech / point_number_simulation
    else:
        minimum_step_rotate = -1

    clone_mesh = mesh_setting.cylindrical_gap_1.clone_mesh

    moving_side_layers = mesh_setting.cylindrical_gap_1.moving_side
    static_side_layers = mesh_setting.cylindrical_gap_1.static_side

    length_band_element_length = mesh_setting.length_band_element_length
    length_coil_element_length = mesh_setting.length_coil_element_length
    length_mag_element_length = mesh_setting.length_mag_element_length
    length_main_element_length = mesh_setting.length_main_element_length
    length_region_element_length = mesh_setting.length_region_element_length

    if clone_mesh:
        # 1. Cap nhat Cylindrical Gap Mesh Operation
        if minimum_step_rotate != -1 and moving_side_layers != -1 and static_side_layers != -1:
            minimum_step_rotate = calculate_band_mapping_angle(delta_angle=minimum_step_rotate,
                                                               minimum_angle= math.radians(1),
                                                               maximum_angle= math.radians(3),
                                                               return_string= True)
            oModule.EditCylindricalGapOp("CylindricalGap1", 
                [
                    "NAME:CylindricalGap1",
                    "CloneMesh:="       , True,
                    "BandMappingAngle:="    , minimum_step_rotate,
                    "MovingSideLayers:="    , str(moving_side_layers),
                    "StaticSideLayers:="    , str(static_side_layers)
                ])
    
    # 2. Cap nhat cac Length Operations (chi gan khi gia tri khac -1)
    if length_band_element_length != -1:
        oModule.EditLengthOp("Length_Band", 
            [
                "NAME:Length_Band",
                "RefineInside:="    , True,
                "Enabled:="         , True,
                "RestrictElem:="    , False,
                "NumMaxElem:="      , "1000",
                "RestrictLength:="  , True,
                "MaxLength:="       , f"{length_band_element_length}mm"
            ])

    if length_coil_element_length != -1:
        oModule.EditLengthOp("Length_Coil", 
            [
                "NAME:Length_Coil",
                "RefineInside:="    , True,
                "Enabled:="         , True,
                "RestrictElem:="    , False,
                "NumMaxElem:="      , "1000",
                "RestrictLength:="  , True,
                "MaxLength:="       , f"{length_coil_element_length}mm"
            ])

    if length_mag_element_length != -1:
        oModule.EditLengthOp("Length_Mag", 
            [
                "NAME:Length_Mag",
                "RefineInside:="    , True,
                "Enabled:="         , True,
                "RestrictElem:="    , False,
                "NumMaxElem:="      , "1000",
                "RestrictLength:="  , True,
                "MaxLength:="       , f"{length_mag_element_length}mm"
            ])

    if length_main_element_length != -1:
        oModule.EditLengthOp("Length_Main", 
            [
                "NAME:Length_Main",
                "RefineInside:="    , True,
                "Enabled:="         , True,
                "RestrictElem:="    , False,
                "NumMaxElem:="      , "1000",
                "RestrictLength:="  , True,
                "MaxLength:="       , f"{length_main_element_length}mm"
            ])

    if length_region_element_length != -1:
        oModule.EditLengthOp("Length_Region", 
            [
                "NAME:Length_Region",
                "RefineInside:="    , True,
                "Enabled:="         , True,
                "RestrictElem:="    , False,
                "NumMaxElem:="      , "1000",
                "RestrictLength:="  , True,
                "MaxLength:="       , f"{length_region_element_length}mm"
            ])

    print(f"\033[92massign_mesh return: True\033[0m")
    return True