from mayavi import mlab
from numpy import load
import h5py
import numpy as np

with h5py.File("horn_w_cable-eps-000000.00.h5", "r") as f:
    eps = np.array(f["eps"])

mlab.contour3d(
    eps,
    contours=[1.5],
    opacity=0.5
)

mlab.show()