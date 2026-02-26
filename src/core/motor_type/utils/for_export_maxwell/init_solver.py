
def init_solver(m3d,motor):

    setup_name = "Setup1"
    if setup_name in m3d.setup_names:
        m3d.delete_setup(setup_name)

    setup = m3d.create_setup(name=setup_name, setup_type="Transient")
    setup.props["StopTime"] = "10ms"
    setup.props["TimeStep"] = "2ms"
    setup.props["SaveFieldsType"] = "Every N Steps"
    setup.props["N Steps"] = "1"
    setup.props["Steps From"] = "0s"
    setup.props["Steps To"] = "10ms"
    setup.props["NonlinearSolverResidual"] = "0.005"
    setup.props["ScalarPotential"] = "Second Order"
    setup.props["SmoothBHCurve"] = False
    setup.update()

    for setup_name in m3d.setup_names:
        m3d.analyze_setup(setup_name)