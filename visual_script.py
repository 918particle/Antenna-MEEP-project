from mayavi import mlab
from numpy import load

data = load('horn_data.npy')

s = mlab.contour3d(data, colormap = "YlGnBu")
mlab.show()