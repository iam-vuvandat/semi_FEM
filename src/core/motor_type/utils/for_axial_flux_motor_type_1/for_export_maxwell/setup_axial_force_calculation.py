
def setup_axial_force_calculation(m3d,assignment):
    m3d.assign_force(
        assignment=assignment, 
        coordinate_system="Global", 
        is_virtual=True, 
        force_name="Axial_Force_Z"
    )