import matplotlib.pyplot as plt

def plot_radiation_patterns(results,theory_results,file_title,beam_loc=None):
	f = plt.figure(dpi=150)
	plt.polar(theory_results[0],theory_results[1],color='black')
	plt.polar(results[0][0],results[0][1],color='red')
	#plt.polar(results[1][0],results[1][1],color='green')
	#plt.polar(results[2][0],results[2][1],color='blue')
	if(beam_loc):
		for beam in beam_loc:
			plt.polar([beam,beam],[-31,3],color='black',linestyle='dashed')
	ax = plt.gca()
	ax.set_rlim(-31,3)
	ax.set_rticks([-15,0])
	ax.grid(True)
	ax.set_rlabel_position(180)
	ax.tick_params(labelsize=18)
	plt.savefig(file_title)