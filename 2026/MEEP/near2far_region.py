import meep as mp

class Near2Far_Region:
	def __init__(self,x_size,y_size,frequencies):
		self.x_size = x_size
		self.y_size = y_size
		self.frequencies = frequencies
	def create(self,simulation):
		results = []
		for f in self.frequencies:
			results.append(
				simulation.add_near2far(
					f,0,1,
					mp.Near2FarRegion(center=mp.Vector3(0,0.5*self.y_size,0),size=mp.Vector3(self.x_size,0,0),weight=+1),
					mp.Near2FarRegion(center=mp.Vector3(0,-0.5*self.y_size,0),size=mp.Vector3(self.x_size,0,0),weight=-1),
					mp.Near2FarRegion(center=mp.Vector3(0.5*self.x_size,0.0,0),size=mp.Vector3(0,self.y_size,0),weight=+1),
					mp.Near2FarRegion(center=mp.Vector3(-0.5*self.x_size,0.0,0),size=mp.Vector3(0,self.y_size,0),weight=-1)
				)
			)
		return results