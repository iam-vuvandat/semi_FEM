import paths 
from storage.core import workspace 
from motor_type.models.AxialFluxMotorType1 import AxialFluxMotorType1


aft = AxialFluxMotorType1()
aft.create_geometry()
aft.create_adaptive_mesh(n_r_in                       =2,
                         n_r_1                        =2,
                         n_r_2                        =2,
                         n_r_3                        =2,
                         n_r_out                      =2,
                         n_theta                      =20,
                         n_z_in_air                   =2,
                         n_z_rotor_yoke               =2,
                         n_z_magnet                   =2,
                         n_z_airgap                   =2,
                         n_z_tooth_tip_1              =2,
                         n_z_tooth_tip_2              =2,
                         n_z_tooth_body               =2,
                         n_z_stator_yoke              =2,
                         n_z_out_air                  =2,
                         use_symmetry_factor=True,
                         periodic_boundary=True)

aft.create_reluctance_network(system_variable = "loop_flux")
aft.reluctance_network.update_reluctance_network(loop_flux= aft.reluctance_network.loop_flux)
