from dataclasses import dataclass
from typing import Any
import numpy as np

@dataclass
class Output:
    flux_direct : Any

def find_flux_direct(element):
    """
    [     r_in    t_left     z_bot
          r_out   t_right    z_top    ]
    """

    magnetic_potential = element.magnetic_potential
    loop_flux = element.loop_flux
    flux_direct = np.zeros((2,3))
    r_i,t_j,z_k = element.position

    if magnetic_potential is not None:
        neighbor_elements = element.neighbor_elements()
        neighbor_elements_position = element.neighbor_elements_position
        

        for i in [0,1,2]:
            if neighbor_elements[0,i] is not None:
                flux_direct[0,i] = find_flux(begin_potential=magnetic_potential.retrieve(position = neighbor_elements_position[0,i]).value,
                                            end_potential= magnetic_potential.retrieve(position = element.position ).value,
                                            r1 = neighbor_elements[0,i].reluctance[1,i],
                                            r2 = element.reluctance[0,i],
                                            f1 = neighbor_elements[0,i].magnetic_source[1,i],
                                            f2 = element.magnetic_source[0,i])
        
        for i in [0,1,2]:
            if neighbor_elements[1,i] is not None:
                flux_direct[1,i] = find_flux(end_potential=magnetic_potential.retrieve(position = neighbor_elements_position[1,i]).value,
                                            begin_potential= magnetic_potential.retrieve(position = element.position ).value,
                                            r1 = neighbor_elements[1,i].reluctance[0,i],
                                            r2 = element.reluctance[1,i],
                                            f1 = neighbor_elements[1,i].magnetic_source[0,i],
                                            f2 = element.magnetic_source[1,i])

        return Output(flux_direct= flux_direct)
    
    else:
        loop_flux = element.loop_flux

        flux_direct[0,0] = (
                            +loop_flux.access_Ort_plane(z_layer = z_k, position = (r_i -1 ,t_j)).value 
                            -loop_flux.access_Ort_plane(z_layer = z_k, position = (r_i -1 ,t_j -1)).value
                            +loop_flux.access_Orz_plane(t_layer = t_j, position = (r_i -1 ,z_k -1)).value
                            -loop_flux.access_Orz_plane(t_layer = t_j, position = (r_i -1 ,z_k)).value
                            )
        
        flux_direct[1,0] = (
                            +loop_flux.access_Ort_plane(z_layer = z_k, position = (r_i ,t_j)).value 
                            -loop_flux.access_Ort_plane(z_layer = z_k, position = (r_i ,t_j -1)).value
                            +loop_flux.access_Orz_plane(t_layer = t_j, position = (r_i ,z_k -1)).value
                            -loop_flux.access_Orz_plane(t_layer = t_j, position = (r_i ,z_k)).value
                            )

        flux_direct[0,1] = (
                            +loop_flux.access_Ort_plane(z_layer = z_k, position = (r_i -1 ,t_j-1)).value
                            -loop_flux.access_Ort_plane(z_layer = z_k, position = (r_i ,t_j-1)).value
                            +loop_flux.access_Otz_plane(r_layer = r_i, position = (t_j -1 ,z_k-1)).value 
                            -loop_flux.access_Otz_plane(r_layer = r_i, position = (t_j -1 ,z_k)).value   
                            )
        
        flux_direct[1,1] = (
                            +loop_flux.access_Ort_plane(z_layer = z_k, position = (r_i -1 ,t_j)).value
                            -loop_flux.access_Ort_plane(z_layer = z_k, position = (r_i ,t_j)).value
                            +loop_flux.access_Otz_plane(r_layer = r_i, position = (t_j,z_k-1)).value 
                            -loop_flux.access_Otz_plane(r_layer = r_i, position = (t_j ,z_k)).value   
                            )
        
        flux_direct[0,2] = (
                            +loop_flux.access_Orz_plane(t_layer = t_j, position = (r_i ,z_k -1)).value
                            -loop_flux.access_Orz_plane(t_layer = t_j, position = (r_i-1 ,z_k -1)).value
                            +loop_flux.access_Otz_plane(r_layer = r_i, position = (t_j,z_k-1)).value 
                            -loop_flux.access_Otz_plane(r_layer = r_i, position = (t_j-1 ,z_k-1)).value   
                            )
        
        flux_direct[1,2] = (
                            +loop_flux.access_Orz_plane(t_layer = t_j, position = (r_i ,z_k)).value
                            -loop_flux.access_Orz_plane(t_layer = t_j, position = (r_i-1 ,z_k)).value
                            +loop_flux.access_Otz_plane(r_layer = r_i, position = (t_j,z_k)).value 
                            -loop_flux.access_Otz_plane(r_layer = r_i, position = (t_j-1 ,z_k)).value   
                            )

    return Output(flux_direct= flux_direct)

def find_flux(begin_potential,
              end_potential ,
              r1,
              r2,
              f1,
              f2):
    flux = 0.0
    flux = ((begin_potential - end_potential ) + (f1 + f2)) / (r1+r2)
    
    return flux