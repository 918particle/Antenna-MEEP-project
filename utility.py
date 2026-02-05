import numpy as np
import meep as mp
import matplotlib.pyplot as plt
def cw_f(frequency,phase):
    return lambda t: np.sin(2.0*3.14159*frequency*t+phase*np.pi/180.0)
def pulse_f(sigma,mu):
    return lambda t: np.exp(-0.5*(t-mu)*(t-mu)/sigma/sigma)
def make_near_to_far_field_box(sx,sy,xoffset,yoffset,frequency,sim):
    top = mp.Near2FarRegion(center=mp.Vector3(xoffset,0.5*sy+yoffset,0),size=mp.Vector3(sx,0,sy),weight=+1)
    bottom = mp.Near2FarRegion(center=mp.Vector3(xoffset,-0.5*sy+yoffset,0),size=mp.Vector3(sx,0,sy),weight=-1)
    right = mp.Near2FarRegion(center=mp.Vector3(0.5*sx+xoffset,yoffset,0),size=mp.Vector3(0,sy,sy),weight=+1)
    left = mp.Near2FarRegion(center=mp.Vector3(-0.5*sx+xoffset,yoffset,0),size=mp.Vector3(0,sy,sy),weight=-1)
    #upper = mp.Near2FarRegion(center=mp.Vector3(xoffset,yoffset,0.5*sy),size=mp.Vector3(sx,sy,0),weight=+1)
    #lower = mp.Near2FarRegion(center=mp.Vector3(xoffset,yoffset,-0.5*sy),size=mp.Vector3(sx,sy,0),weight=-1)
    #return sim.add_near2far(frequency,0,1,top,bottom,left,right,upper,lower)
    return sim.add_near2far(frequency,0,1,top,bottom,left,right)
def make_flux_region(x,y,lx,ly,sim):
    f_start = 0.0
    f_stop = 0.32
    number_of_frequencies = 1024
    f_center = (f_stop+f_start)/2.0;
    df = f_stop-f_start
    flux_monitor_volume = mp.FluxRegion(center=mp.Vector3(x,y,0),size=mp.Vector3(lx,0,0),direction=-mp.Y)
    return sim.add_flux(f_center,df,number_of_frequencies,flux_monitor_volume)
def calculate_radiation_pattern(sim,projection_box,E_or_H_Plane):
    r = 1000
    if(E_or_H_Plane):
        npts = 360
        E = np.zeros((npts,3),dtype=np.complex128)
        H = np.zeros((npts,3),dtype=np.complex128)
        angles = 2*np.pi/npts*np.arange(npts)
        for n in range(npts):
            ff = sim.get_farfield(projection_box,mp.Vector3(r*np.cos(angles[n]),r*np.sin(angles[n]),0))
            E[n,:] = [ff[j] for j in range(3)]
            H[n,:] = [ff[j+3] for j in range(3)]
        Px = np.real(np.conj(E[:,1])*H[:,2]-np.conj(E[:,2])*H[:,1])
        Py = np.real(np.conj(E[:,2])*H[:,0]-np.conj(E[:,0])*H[:,2])
        Pr = np.sqrt(np.square(Px) + np.square(Py))
        directivity = 10.0*np.log10(Pr/max(Pr))
        return (angles,directivity)
    else:
        npts = 180
        angles = np.pi/npts*np.arange(npts)
        E = np.zeros((npts,3),dtype=np.complex128)
        H = np.zeros((npts,3),dtype=np.complex128)
        for n in range(npts):
            ff = sim.get_farfield(projection_box,mp.Vector3(r*np.sin(angles[n]),0,r*np.cos(angles[n])))
            E[n,:] = [ff[j] for j in range(3)]
            H[n,:] = [ff[j+3] for j in range(3)]
        Px = np.real(np.conj(E[:,1])*H[:,2]-np.conj(E[:,2])*H[:,1])
        Py = np.real(np.conj(E[:,2])*H[:,0]-np.conj(E[:,0])*H[:,2])
        Pr = np.sqrt(np.square(Px) + np.square(Py))
        directivity = 10.0*np.log10(Pr/max(Pr))
        return (angles,directivity)
def plot_radiation_pattern(angles,directivity,plot_title,E_or_H_Plane):
    x,y = np.loadtxt('RadPattern_Result_Nov14th.dat',unpack=True)
    x2,y2 = np.loadtxt('RadPattern_Result_Dec1st.dat',unpack=True)
    x *= np.pi/180.0
    x2 += 90.0
    x2 *= np.pi/180.0
    g = plt.figure(dpi=300)
    plt.polar(angles,directivity,color='black')
    if(E_or_H_Plane):
        plt.polar(x,y,'o',color='black')
    else:
        plt.polar(x2,y2,'+',color='black')
    ax = g.gca()
    ax.set_rlim(-26,1)
    ax.set_rticks([-15,-3])
    ax.grid(True)
    ax.set_rlabel_position(180)
    ax.tick_params(labelsize=18)
    plt.savefig(plot_title)
    plt.close()
def plot_surfaces(sim):
    f = plt.figure(dpi=300)
    sim.plot2D(ax=f.gca())
    plt.savefig("surfaces.png")
    plt.close()