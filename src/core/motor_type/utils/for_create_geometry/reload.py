from src.core.motor_type.models.Container import Container
from src.core.motor_type.utils.for_create_geometry.find_symmetry_factor import find_symmetry_factor
from src.core.motor_type.utils.for_create_geometry.find_cogging_period import find_cogging_period

def reload(motor):

    motor.mechanical.symmetry_factor = find_symmetry_factor(motor = motor).symmetry_factor
    motor.mechanical.cogging_period_mech = find_cogging_period(motor = motor).period_mech

    motor.init_winding()
    motor.record = Container()
    motor.create_geometry()
    motor.create_adaptive_mesh()
    motor.reluctance_network = None

