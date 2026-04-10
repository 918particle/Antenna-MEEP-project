import meep as mp
import numpy as np
import constants

def calculate_radiation_pattern(simulation,n2f_objs):
	N = len(n2f_objs)
	results = []
	angles = 2*np.pi/constants.npts*np.arange(constants.npts)
	for i in range(N):
		E = np.zeros((constants.npts,3),dtype=np.complex128)
		H = np.zeros((constants.npts,3),dtype=np.complex128)
		for n in range(constants.npts):
			ff = simulation.get_farfield(n2f_objs[i],mp.Vector3(constants.r*np.cos(angles[n]),constants.r*np.sin(angles[n])))
			E[n,:] = [np.conj(ff[j]) for j in range(3)]
			H[n,:] = [ff[j+3] for j in range(3)]
		Px = np.real(E[:,1]*H[:,2]-E[:,2]*H[:,1])
		Py = np.real(E[:,2]*H[:,0]-E[:,0]*H[:,2])
		Pz = np.real(E[:,0]*H[:,1]-E[:,1]*H[:,0])
		Pr = np.sqrt(np.square(Px)+np.square(Py)+np.square(Pz))
		directivity = 10.0*np.log10(Pr/constants.normalization)
		results.append((angles,directivity,"data"))
	return results
def calculate_theoretical_radiation_pattern(phi_0,frequency):
	directivity = []
	angles = 2*np.pi/constants.npts*np.arange(constants.npts)
	for theta in angles:
		if(theta==0.0 and phi_0==0.0):
			directivity.append(1.0)
		else:
			pr_th_num = np.sin(constants.n_antenna*np.pi*constants.d_y*frequency*(np.sin(theta)-np.sin(phi_0)))
			pr_th_den = np.sin(1.0*np.pi*constants.d_y*frequency*(np.sin(theta)-np.sin(phi_0)))
			directivity.append(pr_th_num*pr_th_num/pr_th_den/pr_th_den/constants.n_antenna/constants.n_antenna)
	directivity = 10.0*np.log10(directivity)-10.0*np.log10(constants.theory_normalization)
	return [(angles,directivity,"theory")]
def locate_beams(rad_patterns):
	results = []
	current_lobe = []
	current_power = []
	In = False
	for pattern in rad_patterns:
		angles = pattern[0]
		p = pattern[1]
		m = np.max(p)
		for i in range(1,constants.npts):
			if(not In and (m-p[i])<=constants.beam_threshold and (m-p[i-1])>=constants.beam_threshold):
				In = True
				current_lobe.append(angles[i]) if angles[i]<=np.pi else current_lobe.append(angles[i]-2*np.pi)
				current_power.append(p[i])
			elif(In and (m-p[i])<=constants.beam_threshold):
				current_lobe.append(angles[i]) if angles[i]<=np.pi else current_lobe.append(angles[i]-2*np.pi)
				current_power.append(p[i])
			else:
				In=False
				results.append((np.mean(current_lobe),np.max(current_power))) if current_lobe else None
				current_lobe = []
				current_power = []
	return results