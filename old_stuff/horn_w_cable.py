import numpy as np
from plan import Plan

def main():
    resolution = 20
    sigma = 0.5
    mu = 1
    cw_frequency = 0.1989
    rad_or_vswr = 1
    e_or_h_plane = 1
    Plan(resolution,cw_frequency,sigma,mu,rad_or_vswr,e_or_h_plane)

if __name__ == "__main__":
    main()