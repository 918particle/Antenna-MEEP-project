import numpy as np
import meep as mp

class RF_horn:
	def __init__(self,box_size,length,width,dx,n_slices):
		self.box_size = box_size
		self.length = length
		self.width = width
		self.dx = dx
		self.n_slices = n_slices
		self.thickness = 0.6667
		self.box_thickness = 0.6667
		self.antenna_size = mp.Vector3(0.1,0.5)
		self.backplate_size = mp.Vector3(self.box_thickness,1.1*self.box_size)
		self.sideplate_size = mp.Vector3(self.box_size,self.box_thickness)
		self.x_loc = 0
		self.y_loc = 0
		self.antenna_position = 0
		self.backplate_position = 0
		self.sideplate_position_upper = 0
		self.sideplate_position_lower = 0
		self.antenna_offset = 0.375
	def create(self,x,y,geometry):
		self.x_loc = x
		self.y_loc = y
		self.antenna_position = mp.Vector3(self.antenna_offset+self.x_loc,self.y_loc)
		self.backplate_position = mp.Vector3(self.x_loc,self.y_loc)
		self.sideplate_position_upper = mp.Vector3(self.box_size/2.0+self.x_loc,self.box_size/2.0+self.y_loc)
		self.sideplate_position_lower = mp.Vector3(self.box_size/2.0+self.x_loc,-self.box_size/2.0+self.y_loc)
		backplate = mp.Block(self.backplate_size,center=self.backplate_position,material=mp.metal)
		sideplate_upper = mp.Block(self.sideplate_size,center=self.sideplate_position_upper,material=mp.metal)
		sideplate_lower = mp.Block(self.sideplate_size,center=self.sideplate_position_lower,material=mp.metal)
		geometry.append(backplate)
		geometry.append(sideplate_lower)
		geometry.append(sideplate_upper)
		edge_size = mp.Vector3(self.dx,self.thickness)
		k_1 = self.box_size/2
		k_2 = (1/self.length)*np.log(2*self.width/self.box_size)
		for i in range(0,self.n_slices):
			edge_upper = mp.Vector3(i*self.dx+self.box_size+x,k_1*np.exp(k_2*(i*self.dx))+y)
			edge_lower = mp.Vector3(i*self.dx+self.box_size+x,-k_1*np.exp(k_2*(i*self.dx))+y)
			geometry.append(mp.Block(edge_size,center=edge_upper,material=mp.metal))
			geometry.append(mp.Block(edge_size,center=edge_lower,material=mp.metal))
	def source_function(self,frequency,phase):
		N = 10
		a = np.zeros((N,1))
		b = np.zeros((N,1))
		a[0] = 1
		a[2] = 1
		a[5] = 1
		a[8] = 1
		omega = 2.0*np.pi*frequency
		return lambda t: np.sum([a[n]*np.sin((n+1)*omega*t-phase)+b[n]*np.cos((n+1)*omega*t-phase) for n in range(N)],axis=0)
	def add_source(self,frequency,phase,sources):
		sources.append(
			mp.Source(
				mp.CustomSource(src_func=self.source_function(frequency,phase),start_time=1),
				component=mp.Ey,
				center=self.antenna_position,
				size=self.antenna_size,
				amplitude=1
			)
		)