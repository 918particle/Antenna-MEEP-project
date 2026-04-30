import os
import meep as mp
import numpy as np
import matplotlib.pyplot as plt
from rf_horn import RF_horn
from rf_array import RF_array
from near2far_region import Near2Far_Region
import radiation_pattern
import graph_patterns
import constants as c
mp.verbosity(0)
frequencies = np.arange(c.sweep_start,c.sweep_stop,c.d_f)

#Frequency sweep
for f in frequencies:
	#Create the simulation
	pml_layers = [mp.PML(1.0)]
	geometry = []
	sources = []
	RF_array(geometry,sources,f)
	sim = mp.Simulation(
		cell_size=mp.Vector3(c.x_size,c.y_size),
		boundary_layers=pml_layers,
		geometry=geometry,
		sources=sources,
		resolution=c.resolution)
	#Add Near 2 Far projection regions
	region = Near2Far_Region(c.n2f_x_size,c.n2f_y_size,np.array([c.base_frequency,f]))
	region_objs = region.create(sim)
	#Run statement
	sim.run(until=100)
	#Compute radiation patterns
	theory_results = radiation_pattern.calculate_theoretical_radiation_pattern(0.0,f)
	results = radiation_pattern.calculate_radiation_pattern(sim,region_objs)
	#angles=((results[0][0]+np.pi)%(2*np.pi)-np.pi)*180.0/np.pi
	#for i in range(c.npts):
	#	print(angles[i],end=' ')
	#	for result in results:
	#		directivity = result[1]
	#		print(directivity[i],end=' ')
	#	print()
	#Beamwidth analysis
	#beams = radiation_pattern.locate_beams(results)
	#print(beams)
	#Graph radiation patterns
	graph_patterns.plot_radiation_patterns(results,"rad_pattern"+"_"+format(f,".2f")+".png")
	#Plot surfaces
	if(f==frequencies[0]):
		fg = plt.figure(dpi=150)
		sim.plot2D(ax=fg.gca(),eps_parameters={'cmap': 'gray'})
		plt.savefig("surfaces.png")
	sim.reset_meep()