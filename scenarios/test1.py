import paths
from motor_type.models.AxialFluxMotorType1 import AxialFluxMotorType1
from storage.core import workspace 
from tqdm import tqdm
import numpy as np

re_create_motor = True
re_solve = True

if re_create_motor == False:
    aft = workspace.load("aft1")
    if re_solve == True:
        aft.reluctance_network.list_elements_lite = None
else:
    aft = AxialFluxMotorType1(magnet_length=4.0 * 1e-3,
                              airgap=0.5 * 1e-3)
    aft.create_geometry()
    aft.create_adaptive_mesh()
    aft.create_reluctance_network()
    print(aft.reluctance_network.system_variable)
    print(aft.reluctance_network.loop_flux)
    aft.reluctance_network.update_reluctance_network(loop_flux=aft.reluctance_network.loop_flux)
    workspace.save(aft1=aft)



if re_solve == True:
    equation_component = aft.reluctance_network.create_loop_flux_equation()
    F = equation_component.F
    R = equation_component.R

    # Kích thước hệ
    system_size = F.size

    # Tính rank (chú ý tolerance)
    rank_R = np.linalg.matrix_rank(R.toarray(), tol=1e-10)

    if rank_R < system_size:
        print("⚠️ HỆ THIẾU RANK")
        print(f"   rank(R) = {rank_R}")
        print(f"   size(F) = {system_size}")
        print("→ Có khả năng thiếu vòng toàn cục hoặc vòng topo sai.")
    else:
        print("✅ Hệ đủ rank (topo đầy đủ)")

    workspace.save(aft1=aft)

aft.reluctance_network.show()
