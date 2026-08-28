import meep as mp
import numpy as np
import utility

gdsII_file = 'test.gds'
gdsII_file_no_horn = 'no_horn.gds'
HORN_LAYER = 2
COND_LAYER = 5
DIEL_LAYER = 6
SOURCE_LAYER = 7
BACK_PLUG = 8
SOURCE_LAYER_2 = 9
TOP_LAYER = 10

def Plan(resolution,frequency,sigma,mu,radPattern_or_vswr,E_or_H_Plane):
    t_all = 1.0 #normally 1.0
    thickness = 0.5 #normally 0.5
    if(radPattern_or_vswr):
        dpml = 1
        back = mp.get_GDSII_prisms(mp.metal,gdsII_file,BACK_PLUG,-t_all,t_all)
        sides = mp.get_GDSII_prisms(mp.metal,gdsII_file,HORN_LAYER,-t_all,t_all)
        bottom = mp.get_GDSII_prisms(mp.metal,gdsII_file,TOP_LAYER,-t_all,-t_all+thickness)
        top = mp.get_GDSII_prisms(mp.metal,gdsII_file,TOP_LAYER,t_all-thickness,t_all)
        geometry = back+sides+top+bottom
        #geometry = sides+back
        sources = []
        src_vol = mp.GDSII_vol(gdsII_file,SOURCE_LAYER,-thickness/2,thickness/2)
        sources.append(mp.Source(mp.CustomSource(src_func=utility.cw_f(frequency,0.0),start_time=0.0),component=mp.Ey,volume=src_vol,amplitude=1))
        sim = mp.Simulation(resolution=resolution,cell_size=mp.Vector3(60,60,60),boundary_layers=[mp.PML(dpml)],sources=sources,geometry=geometry)
        projection_box = utility.make_near_to_far_field_box(30,15,-10,0,frequency,sim)
        #utility.plot_surfaces(sim)
        #sim.run(mp.to_appended("ey",mp.at_every(0.5, mp.output_efield_y)),until=100)
        sim.run(until=100)
        (angles,directivity) = utility.calculate_radiation_pattern(sim,projection_box,E_or_H_Plane)
        utility.plot_radiation_pattern(angles,directivity,"rad_pattern.png",E_or_H_Plane)
    else:
        dpml = 5
        time_steps = 115
        conductors = mp.get_GDSII_prisms(mp.metal,gdsII_file_no_horn,COND_LAYER,-t_all,t_all)
        dielectric = mp.get_GDSII_prisms(mp.Medium(epsilon=2),gdsII_file_no_horn,DIEL_LAYER,-t_all,t_all)
        geometry = conductors+dielectric
        sources = []
        src_vol = mp.GDSII_vol(gdsII_file,SOURCE_LAYER_2,-t_all,t_all)
        sources.append(mp.Source(mp.CustomSource(src_func=utility.pulse_f(sigma,mu),start_time=0.0),component=mp.Ex,volume=src_vol,amplitude=1))
        sim = mp.Simulation(resolution=resolution,cell_size=mp.Vector3(68,68),boundary_layers=[mp.PML(dpml)],sources=sources,geometry=geometry)
        flux_monitor = utility.make_flux_region(0,11.0,1.0,0.055,sim)
        sim.run(until=time_steps)
        normalization_run = sim.get_flux_data(flux_monitor)
        normalization_flux = mp.get_fluxes(flux_monitor)
        sim.reset_meep()
        conductors = mp.get_GDSII_prisms(mp.metal,gdsII_file,COND_LAYER,-t_all,t_all)
        dielectric = mp.get_GDSII_prisms(mp.Medium(epsilon=2),gdsII_file,DIEL_LAYER,-t_all,t_all)
        sides = mp.get_GDSII_prisms(mp.metal,gdsII_file,HORN_LAYER,-t_all,t_all)
        geometry = []
        geometry = conductors+dielectric+sides
        sim = mp.Simulation(resolution=resolution,cell_size=mp.Vector3(68,68),boundary_layers=[mp.PML(dpml)],sources=sources,geometry=geometry)
        flux_monitor = utility.make_flux_region(0,11.0,1.0,0.055,sim)
        sim.load_minus_flux_data(flux_monitor,normalization_run)
        sim.run(mp.to_appended("ex",mp.at_every(1, mp.output_efield_x)),until=time_steps)
        #sim.run(until=time_steps)
        reflection_flux = mp.get_fluxes(flux_monitor)
        flux_frequencies = mp.get_flux_freqs(flux_monitor)
        n = len(flux_frequencies)
        results = np.zeros((n,3),dtype=float)
        for i in range(n):
            gamma = np.abs(reflection_flux[i])/np.abs(normalization_flux[i])
            vswr = (1+np.sqrt(gamma))/(1-np.sqrt(gamma))
            results[i][0] = flux_frequencies[i]*30
            results[i][1] = gamma
            results[i][2] = vswr
        np.savetxt("vswr.dat",results)
        utility.plot_surfaces(sim)