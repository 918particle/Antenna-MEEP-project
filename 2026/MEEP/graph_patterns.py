import matplotlib.pyplot as plt
import constants

def plot_radiation_patterns(results,file_title,beam_loc=None):
	f = plt.figure(dpi=150)
	for result in results:
		if(result[2]=="data"):
			plt.polar(result[0],result[1],color='black')
		else:
			plt.polar(result[0],result[1],'--',color='gray')
	if(beam_loc):
		for beam in beam_loc:
			plt.polar(beam[0],beam[1],'o',color='black')
	ax = plt.gca()
	ax.set_rlim(-31,3)
	ax.set_rticks([-constants.beam_threshold,0])
	ax.grid(True)
	ax.set_rlabel_position(180)
	ax.tick_params(labelsize=18)
	plt.savefig(file_title)