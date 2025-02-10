import numpy as np
from config import *


def translation_matrix(position):
    m = np.eye(4, dtype=DTYPE)
    m[:3, 3] = position

    return m

def x_rotation_matrix(degrees):
    angle = np.radians(degrees)
    c = np.cos(angle)
    s = np.sin(angle)
    
    m = np.eye(4, dtype=DTYPE)
    m[1, 1] = c
    m[1, 2] = -s
    m[2, 1] = s
    m[2, 2] = c

    return m

def y_rotation_matrix(degrees):
    angle = np.radians(degrees)
    c = np.cos(angle)
    s = np.sin(angle)
    
    m = np.eye(4, dtype=DTYPE)
    m[0, 0] = c
    m[0, 2] = s
    m[2, 0] = -s
    m[2, 2] = c

    return m

def z_rotation_matrix(degrees):
    angle = np.radians(degrees)
    c = np.cos(angle)
    s = np.sin(angle)
    
    m = np.eye(4, dtype=DTYPE)
    m[0, 0] = c
    m[0, 1] = -s
    m[1, 0] = s
    m[1, 1] = c

    return m

def scaling_matrix(scale):
    m = np.eye(4, dtype=DTYPE)
    m[0, 0] = scale[0]
    m[1, 1] = scale[1]
    m[2, 2] = scale[2]

    return m
