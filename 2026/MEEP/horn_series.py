import meep as mp
import numpy as np
import matplotlib.pyplot as plt
from rf_horn import RF_horn
from rf_array import RF_array
from near2far_region import Near2Far_Region
import radiation_pattern
import graph_patterns
import constants

#Create the simulation
pml_layers = [mp.PML(1.0)]
geometry = []
sources = []
RF_array(geometry,sources)
sim = mp.Simulation(
	cell_size=mp.Vector3(constants.x_size,constants.y_size),
	boundary_layers=pml_layers,
	geometry=geometry,
	sources=sources,
	resolution=constants.resolution)

#Add Near 2 Far projection regions
frequencies = np.array([3])*constants.frequency
region = Near2Far_Region(constants.n2f_x_size,constants.n2f_y_size,frequencies)
region_objs = region.create(sim)

#Plot surfaces
f = plt.figure(dpi=150)
sim.plot2D(ax=f.gca(),eps_parameters={'cmap': 'gray'})
plt.savefig("surfaces.png")

#Run statement
sim.run(until=100)

#Compute radiation patterns
results = radiation_pattern.calculate_radiation_pattern(sim,region_objs)
theory_results = radiation_pattern.calculate_theoretical_radiation_pattern(0.0,3*constants.frequency)

#Beamwidth analysis
beams = radiation_pattern.locate_beams(results)
print(beams)

#Graph radiation patterns
graph_patterns.plot_radiation_patterns(theory_results+results,"rad_pattern.png",beam_loc=beams)