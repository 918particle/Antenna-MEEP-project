import matplotlib.pyplot as plt
import numpy as np
import constants

def plot_radiation_patterns(results,file_title,beam_loc=None):
	f = plt.figure(dpi=150)
	i=0
	factor=180.0/np.pi
	shifted_angles=((results[0][0]+np.pi)%(2*np.pi)-np.pi)*factor
	for result in results:
		if(result[2]=="data"):
			match i:
				case 0:
					plt.plot(shifted_angles,result[1],color=(1.0,0.0,1.0))
				case 1:
					plt.plot(shifted_angles,result[1],color=(0.0,0.0,1.0))
				case 2:
					plt.plot(shifted_angles,result[1],color=(0.0,1.0,0.0))
				case 3:
					plt.plot(shifted_angles,result[1],color=(1.0,0.0,0.0))
				case 4:
					plt.plot(shifted_angles,result[1],color=(0.0,0.0,0.0))
		else:
			plt.plot(shifted_angles,result[1],'--',color='gray')
		i+=1
	#if(beam_loc):
	#	for beam in beam_loc:
	#		plt.plot(beam[0]*factor,beam[1],'o',color='black')
	ax = plt.gca()
	ax.set_ylim(-31,3)
	ax.set_xlim(-45,45)
	ax.set_xticks([-45,-30,-15,0,15,30,45])
	ax.set_yticks([-constants.beam_threshold,0])
	ax.grid(True)
	ax.tick_params(labelsize=18)
	plt.savefig(file_title)