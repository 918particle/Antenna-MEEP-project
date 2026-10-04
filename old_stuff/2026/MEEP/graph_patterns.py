import matplotlib.pyplot as plt
import numpy as np
import constants

def plot_radiation_patterns(results,file_title,beam_loc=None):
	f = plt.figure(dpi=150)
	factor=180.0/np.pi
	shifted_angles=((results[0][0]+np.pi)%(2*np.pi)-np.pi)*factor
	for result in results:
		if(result[2]=="data"):
			plt.plot(shifted_angles,result[1],'-',color='black')
	if(beam_loc):
		for beam in beam_loc:
			plt.plot(beam[0]*factor,beam[1],'o',color='black')
	ax = plt.gca()
	ax.set_ylim(-31,3)
	ax.set_xlim(-90,90)
	ax.set_xticks([-90,-45,0,45,90])
	ax.set_yticks([-constants.beam_threshold,0])
	ax.grid(True)
	ax.tick_params(labelsize=18)
	plt.savefig(file_title)
	plt.close()