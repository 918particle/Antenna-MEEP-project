import meep as mp
import numpy as np
import matplotlib.pyplot as plt
import utility

example = utility.rf_horn(1,1,1,1,1,1)

#Important variables
x_size = 40.0
y_size = 150.0
z_size = 50
geometry = [mp.Block(mp.Vector3(x_size,y_size),center=mp.Vector3(),material=mp.Medium(epsilon=1))]
pml_layers = [mp.PML(1.0)]
sources = []
resolution = 10
antennaFreq = 0.04
phase = 0
d_phase = 10

#Horn parameters
a = 0.9375
c = 15.0
d = 4.0*a
dx = 0.1
k_1 = a/2
k_2 = (1/c)*np.log(2*d/a)
n_slices = int(c/dx)
thickness = 0.6667
box_thickness = 0.6667
antenna_size = mp.Vector3(box_thickness/10.0,0.5)
backplate_size = mp.Vector3(box_thickness,1.1*a)
side_plate_size = mp.Vector3(a,box_thickness)

#Array parameters
d_y = 2*d
n_antenna = 16

#Offsets
x0 = -0.5*c
y0 = -y_size/2.0+d*5

def source_function(phase):
	N = 10
	a = np.zeros((N,1))
	b = np.zeros((N,1))
	a[0] = 1
	a[3] = 1
	a[7] = 1
	omega = 2.0*np.pi*antennaFreq
	return lambda t: np.sum([a[n]*np.sin((n+1)*omega*t+phase)+b[n]*np.cos((n+1)*omega*t+phase) for n in range(N)],axis=0)

for j in range(0,n_antenna):
	y = j*d_y+y0
	#Describe the box
	antenna_location = mp.Vector3(0.375+x0,y)
	backplate_location = mp.Vector3(x0,y)
	side_plate_location_pos = mp.Vector3(a/2.0+x0,a/2.0+y)
	side_plate_location_neg = mp.Vector3(a/2.0+x0,-a/2.0+y)
	backplate = mp.Block(backplate_size,center=backplate_location,material=mp.metal)
	side_plate_xz_upper = mp.Block(side_plate_size,center=side_plate_location_pos,material=mp.metal)
	side_plate_xz_lower = mp.Block(side_plate_size,center=side_plate_location_neg,material=mp.metal)
	#Add it to the geometry
	geometry.append(side_plate_xz_upper)
	geometry.append(side_plate_xz_lower)
	geometry.append(backplate)
	#geometry loop for horn portion
	size_xz_upper = mp.Vector3(dx,thickness)
	size_xz_lower = mp.Vector3(dx,thickness)
	for i in range(0,n_slices):
		center_xz_upper = mp.Vector3(i*dx+a+x0,k_1*np.exp(k_2*(i*dx))+y)
		center_xz_lower = mp.Vector3(i*dx+a+x0,-k_1*np.exp(k_2*(i*dx))+y)
		geometry.append(mp.Block(size_xz_upper,center=center_xz_upper,material=mp.metal)) #xz_upper
		geometry.append(mp.Block(size_xz_lower,center=center_xz_lower,material=mp.metal)) #xz_lower
	#Add it as a source
	sources.append(
		mp.Source(
			mp.CustomSource(src_func=source_function(phase),start_time=1),
			component=mp.Ey,
			center=antenna_location,
			size=antenna_size,
			amplitude=1
		)
    )
	phase+=d_phase

#Create the simulation and near to far field box
sim = mp.Simulation(
	cell_size=mp.Vector3(x_size,y_size),
	boundary_layers=pml_layers,
	geometry=geometry,
	sources=sources,
	resolution=resolution)
sx = 22.0
sy = 125
nearfield_box_low = sim.add_near2far(antennaFreq,0,1,
	mp.Near2FarRegion(center=mp.Vector3(0,0.5*sy,0),size=mp.Vector3(sx,0,0),weight=+1),
	mp.Near2FarRegion(center=mp.Vector3(0,-0.5*sy,0),size=mp.Vector3(sx,0,0),weight=-1),
	mp.Near2FarRegion(center=mp.Vector3(0.5*sx,0.0,0),size=mp.Vector3(0,sy,0),weight=+1),
	mp.Near2FarRegion(center=mp.Vector3(-0.5*sx,0.0,0),size=mp.Vector3(0,sy,0),weight=-1)
	)
nearfield_box_mid = sim.add_near2far(4*antennaFreq,0,1,
	mp.Near2FarRegion(center=mp.Vector3(0,0.5*sy,0),size=mp.Vector3(sx,0,0),weight=+1),
	mp.Near2FarRegion(center=mp.Vector3(0,-0.5*sy,0),size=mp.Vector3(sx,0,0),weight=-1),
	mp.Near2FarRegion(center=mp.Vector3(0.5*sx,0.0,0),size=mp.Vector3(0,sy,0),weight=+1),
	mp.Near2FarRegion(center=mp.Vector3(-0.5*sx,0.0,0),size=mp.Vector3(0,sy,0),weight=-1)
	)
nearfield_box_high = sim.add_near2far(8*antennaFreq,0,1,
	mp.Near2FarRegion(center=mp.Vector3(0,0.5*sy,0),size=mp.Vector3(sx,0,0),weight=+1),
	mp.Near2FarRegion(center=mp.Vector3(0,-0.5*sy,0),size=mp.Vector3(sx,0,0),weight=-1),
	mp.Near2FarRegion(center=mp.Vector3(0.5*sx,0.0,0),size=mp.Vector3(0,sy,0),weight=+1),
	mp.Near2FarRegion(center=mp.Vector3(-0.5*sx,0.0,0),size=mp.Vector3(0,sy,0),weight=-1)
	)

#Plot surfaces
f = plt.figure(dpi=150)
sim.plot2D(ax=f.gca(),eps_parameters={'cmap': 'gray'})
plt.savefig("surfaces.png")

#Run statement
sim.run(until=200)

#Calculate radiation pattern: directivity versus azimuthal angle
npts = 360
angles = 2*np.pi/npts*np.arange(npts)
r = 1000
E_low = np.zeros((npts,3),dtype=np.complex128)
H_low = np.zeros((npts,3),dtype=np.complex128)
E_mid = np.zeros((npts,3),dtype=np.complex128)
H_mid = np.zeros((npts,3),dtype=np.complex128)
E_high = np.zeros((npts,3),dtype=np.complex128)
H_high = np.zeros((npts,3),dtype=np.complex128)
for n in range(npts):
	ff_low = sim.get_farfield(nearfield_box_low,mp.Vector3(r*np.cos(angles[n]),r*np.sin(angles[n]),0.0))
	ff_mid = sim.get_farfield(nearfield_box_mid,mp.Vector3(r*np.cos(angles[n]),r*np.sin(angles[n]),0.0))
	ff_high = sim.get_farfield(nearfield_box_high,mp.Vector3(r*np.cos(angles[n]),r*np.sin(angles[n]),0.0))
	E_low[n,:] = [np.conj(ff_low[j]) for j in range(3)]
	H_low[n,:] = [ff_low[j+3] for j in range(3)]
	E_mid[n,:] = [np.conj(ff_mid[j]) for j in range(3)]
	H_mid[n,:] = [ff_mid[j+3] for j in range(3)]
	E_high[n,:] = [np.conj(ff_high[j]) for j in range(3)]
	H_high[n,:] = [ff_high[j+3] for j in range(3)]
Px = np.real(E_low[:,1]*H_low[:,2]-E_low[:,2]*H_low[:,1])
Py = np.real(E_low[:,2]*H_low[:,0]-E_low[:,0]*H_low[:,2])
Pz = np.real(E_low[:,0]*H_low[:,1]-E_low[:,1]*H_low[:,0])
Pr_low = np.sqrt(np.square(Px)+np.square(Py)+np.square(Pz))
Px = np.real(E_mid[:,1]*H_mid[:,2]-E_mid[:,2]*H_mid[:,1])
Py = np.real(E_mid[:,2]*H_mid[:,0]-E_mid[:,0]*H_mid[:,2])
Pz = np.real(E_mid[:,0]*H_mid[:,1]-E_mid[:,1]*H_mid[:,0])
Pr_mid = np.sqrt(np.square(Px)+np.square(Py)+np.square(Pz))
Px = np.real(E_high[:,1]*H_high[:,2]-E_high[:,2]*H_high[:,1])
Py = np.real(E_high[:,2]*H_high[:,0]-E_high[:,0]*H_high[:,2])
Pz = np.real(E_high[:,0]*H_high[:,1]-E_high[:,1]*H_high[:,0])
Pr_high = np.sqrt(np.square(Px)+np.square(Py)+np.square(Pz))
normalization_high = max(Pr_high)
directivity_low = 10.0*np.log10(Pr_low/normalization_high)
directivity_mid = 10.0*np.log10(Pr_mid/normalization_high)
directivity_high = 10.0*np.log10(Pr_high/normalization_high)
directivity_theory = []
for theta in angles:
	if(theta!=0.0):
		pr_th_num = np.sin(n_antenna*np.pi*d_y*antennaFreq*(np.sin(theta)-np.sin(0*np.pi/180)))
		pr_th_den = np.sin(1.0*np.pi*d_y*antennaFreq*(np.sin(theta)-np.sin(0*np.pi/180)))
		directivity_theory.append(pr_th_num*pr_th_num/pr_th_den/pr_th_den/n_antenna/n_antenna)
	else:
		directivity_theory.append(1.0/n_antenna/n_antenna)
directivity_theory = 10.0*np.log10(directivity_theory)
directivity_theory[0] = 0
angles_theory = angles
f = plt.figure(dpi=150)
#plt.polar(angles_theory,directivity_theory,color='black')
plt.polar(angles,directivity_low+10,color='black')
#plt.polar(angles,directivity_mid,color='red')
#plt.polar(angles,directivity_high,color='blue')
ax = plt.gca()
ax.set_rlim(-40,3)
ax.set_rticks([-30,-15,0])
ax.grid(True)
ax.set_rlabel_position(180)
ax.tick_params(labelsize=18)
plt.savefig("rad_pattern.png")