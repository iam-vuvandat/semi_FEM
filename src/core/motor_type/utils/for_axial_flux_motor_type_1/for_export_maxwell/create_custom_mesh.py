def create_custom_mesh(m3d, motor, region):
    mesh_setting = motor.maxwell_export_option.custom_option.mesh_setting
    maximum_element_length = mesh_setting.maximum_element_length * 1e3 
    airgap_element_layer = mesh_setting.airgap_element_layer

    if maximum_element_length != -1:
        all_objects = m3d.modeler.object_names
        mesh_targets = [
            obj for obj in all_objects 
            if obj != region         
            and "Line" not in obj         
            and "Sheet" not in obj      
        ]

        m3d.mesh.assign_length_mesh(
            assignment=mesh_targets,
            maximum_length=f"{maximum_element_length}mm",
            maximum_elements=None,
            name="Global_Core_Mesh"
        )
    
    if airgap_element_layer != -1: 
        rotor = motor.geometry_data.rotor

        rotor_lam_dia        = rotor.rotor_lam_dia  * 1e3
        shaft_hole_diameter  = rotor.shaft_hole_diameter * 1e3 
        
        rotor_outer_radius = rotor_lam_dia / 2 
        rotor_inner_radius = shaft_hole_diameter / 2

        airgap = rotor.airgap * 1e3 
        rotor_length = rotor.rotor_length * 1e3
        magnet_length = rotor.magnet_length * 1e3
        maximum_airgap_element_length = airgap / airgap_element_layer 

        # SỬA ĐỔI: Sử dụng 0.49 để tạo khe hở an toàn 2% ở giữa (0.02 * airgap)
        # Điều này thỏa mãn điều kiện "must be a layer of band in between"
        half_height_safe = airgap * 0.49
        z_rotor_top = rotor_length + magnet_length
        # Vùng stator bắt đầu từ 51% chiều cao khe hở
        z_stator_start = z_rotor_top + (airgap * 0.51)

        # 1. Vùng Mesh phía Rotor (Sát mặt nam châm)
        rotor_mesh_out = m3d.modeler.create_cylinder(
            orientation="Z", 
            origin=[0, 0, z_rotor_top], 
            radius=rotor_outer_radius, 
            height=half_height_safe, 
            name="mesh_rotor_side"
        )
        rotor_mesh_in = m3d.modeler.create_cylinder(
            orientation="Z", 
            origin=[0, 0, z_rotor_top], 
            radius=rotor_inner_radius, 
            height=half_height_safe
        )
        m3d.modeler.subtract(blank_list=[rotor_mesh_out], tool_list=[rotor_mesh_in], keep_originals=False)
        m3d.modeler[rotor_mesh_out].material_name = "vacuum"
        m3d.modeler[rotor_mesh_out].model = True

        # 2. Vùng Mesh phía Stator (Sát mặt răng Stator)
        stator_mesh_out = m3d.modeler.create_cylinder(
            orientation="Z", 
            origin=[0, 0, z_stator_start], 
            radius=rotor_outer_radius, 
            height=half_height_safe, 
            name="mesh_stator_side"
        )
        stator_mesh_in = m3d.modeler.create_cylinder(
            orientation="Z", 
            origin=[0, 0, z_stator_start], 
            radius=rotor_inner_radius, 
            height=half_height_safe
        )
        m3d.modeler.subtract(blank_list=[stator_mesh_out], tool_list=[stator_mesh_in], keep_originals=False)
        m3d.modeler[stator_mesh_out].material_name = "vacuum"
        m3d.modeler[stator_mesh_out].model = True

        # Gán Mesh Operation cho cả 2 vùng
        m3d.mesh.assign_length_mesh(
            assignment=[rotor_mesh_out, stator_mesh_out],
            maximum_length=f"{maximum_airgap_element_length}mm",
            maximum_elements=None,
            name="Air_gap_Refinement"
        )
    
    return None