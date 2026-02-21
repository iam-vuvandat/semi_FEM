
def create_balloon(pad_value=30,m3d = None):
    region = m3d.modeler.create_region(pad_value= pad_value, pad_type="Percentage Offset",name = "region")
    m3d.assign_insulating(assignment=[region])