from re import A
from sympy import rad
import paths
import math 
pi = math.pi
import numpy as np 
from motor_type.utils.for_create_geometry.create_arc import create_arc
from motor_type.utils.for_create_geometry.create_smart_surface import create_smart_surface
from motor_type.utils.for_create_geometry.create_loft_mesh import create_loft_mesh
from core_class.models.Geometry import Geometry
from core_class.models.Segment import Segment

arc1 = create_arc(radius= 5,
                  start_rad=np.radians(-15),
                  end_rad= np.radians(15))

arc2 = create_arc(radius= 10,
                  start_rad=np.radians(-15),
                  end_rad= np.radians(15))

surface1 = create_smart_surface(arc1=arc1,
                                arc2=arc2,
                                z1=2,
                                z2=2)

surface2 = create_smart_surface(arc1=arc1,
                                arc2=arc2,
                                z1=4,
                                z2=4)

mesh1 = create_loft_mesh(surface1,
                         surface2)

segment1 = Segment(mesh=mesh1,
                   material= "iron")
geometry = []
geometry.append(segment1)
geometry1 = Geometry(geometry=geometry)
geometry1.show()