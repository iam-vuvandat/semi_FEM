
def create_custom_mesh(m3d, motor, region):
    mesh_setting = motor.maxwell_export_option.custom_option.mesh_setting
    maximum_element_length = mesh_setting.maximum_element_length * 1e3 # unit: mm
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
        rotor_outer_radius = motor.geometry_data.rotor.rotor_lam_dia / 2 * 1e3 #unit: mm
        airgap_element_layer = mesh_setting.airgap_element_layer
        airgap = motor.geometry_data.rotor.airgap * 1e3 # unit: mm
        rotor_length = motor.geometry_data.rotor.rotor_length * 1e3
        maximum_airgap_element_length = airgap / airgap_element_layer # unit: mm
        magnet_length = motor.geometry_data.rotor.magnet_length * 1e3 # unit: mm

        airgap_obj = m3d.modeler.create_cylinder(
        orientation="Z", 
        origin=[0, 0, rotor_length + magnet_length], 
        radius= rotor_outer_radius * 1.1, 
        height= airgap)

        m3d.mesh.assign_length_mesh(
            assignment=airgap_obj,
            maximum_length=f"{maximum_airgap_element_length}mm",
            maximum_elements=None,
            name="Air_gap"
        )
            

        
