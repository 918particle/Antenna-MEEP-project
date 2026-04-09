from rf_horn import RF_horn
import constants

class RF_array:
	def __init__(self,geometry,sources):
		for j in range(0,constants.n_antenna):
			y = j*constants.d_y+constants.y0
			current_antenna = RF_horn(
				constants.box_size,
				constants.antenna_length,
				4.0*constants.box_size,
				constants.dx,
				constants.n_slices)
			current_antenna.create(constants.x0,y,geometry)
			current_antenna.add_source(constants.frequency,constants.phase+j*constants.d_phase,sources)