from mayavi import mlab
from numpy import load
import h5py
import numpy as np

with h5py.File("meep_structure.h5","r") as f:
    eps = np.array(f["epsilon"])

mlab.contour3d(
    eps,
    contours=[1.5],
    opacity=0.85,
    color=(0.25,0.25,0.25)
)

mlab.show()