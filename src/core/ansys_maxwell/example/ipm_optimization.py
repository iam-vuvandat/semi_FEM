from pyaedt import Maxwell3d

mx = Maxwell3d(
    project="demo",
    design="magnetostatic_test",
    solution_type="Magnetostatic",
    new_desktop=True
)

# Geometry
core = mx.modeler.create_box(
    origin=[-20, -20, -20],
    sizes=[40, 40, 40],
    name="Core",
    material="vacuum"
)

coil = mx.modeler.create_cylinder(
    orientation="Z",
    origin=[0, 0, -10],
    radius=5,
    height=20,
    name="Coil",
    material="copper"
)

# Region (bắt buộc, KHÔNG assign boundary)
mx.modeler.create_region(pad_value=50)

# Excitation (API có thật)
mx.assign_current(
    assignment="Coil",
    amplitude=10,
    name="Icoil"
)

# Setup & solve
mx.create_setup("Setup1")
mx.analyze()

mx.release_desktop()
