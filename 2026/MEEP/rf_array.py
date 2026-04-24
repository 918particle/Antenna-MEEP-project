from rf_horn import RF_horn
import constants as c

class RF_array:
	def __init__(self,geometry,sources):
		for j in range(0,c.n_antenna):
			y = j*c.d_y+c.y0
			current_antenna = RF_horn(c.box_size,c.antenna_length,4.0*c.box_size,c.dx,c.n_slices)
			current_antenna.create(c.x0,y,geometry)
			current_antenna.add_source(c.frequency_1,c.phase+j*c.d_phase_1,sources)
			current_antenna.add_source(c.frequency_2,c.phase+j*c.d_phase_2,sources)
			current_antenna.add_source(c.frequency_3,c.phase+j*c.d_phase_3,sources)
			current_antenna.add_source(c.frequency_4,c.phase+j*c.d_phase_4,sources)
			current_antenna.add_source(c.frequency_5,c.phase+j*c.d_phase_5,sources)