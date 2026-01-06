from dataclasses import dataclass
import numpy as np


@dataclass
class Output:
    flat_position :int

def find_flat_position(element):
    nr,nt,nz = element.elements.shape()
    i,j,k = element.position
    flat_position = i + (j * nr) + (k * nr * nt)
    
    return Output(flat_position= flat_position)
    