
def create_custom_mesh(m3d, motor, exclude):
    maximum_element_length = motor.maxwell_export_option.custom_option.mesh_setting.maximum_element_length * 1e3 # unit: mm

    all_objects = m3d.modeler.object_names
    mesh_targets = [
        obj for obj in all_objects 
        if obj != exclude              
        and "Line" not in obj        
        and "Sheet" not in obj      
    ]

    m3d.mesh.assign_length_mesh(
        assignment=mesh_targets,
        maximum_length=f"{maximum_element_length}mm",
        maximum_elements=None,
        name="Global_Core_Mesh"
    )