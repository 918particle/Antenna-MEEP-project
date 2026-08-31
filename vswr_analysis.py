from dataclasses import dataclass
from pathlib import Path

import meep as mp
import numpy as np
import pandas as pd

from analysis import Analysis
from models import (
    AnalysisConfig,
    Dimensionality,
    VSWRResults,
)
from utilities import plot_surfaces, plot_vswr

SIM_TIMESTEPS = 115


@dataclass
class FluxMonitorDimensions:
    x_size: float
    y_size: float
    x_center: float
    y_center: float
    z_size: float = 0
    z_center: float = 0


class VSWRAnalysis(Analysis):
    def __init__(self, analysis_config: AnalysisConfig, output_folder: str):
        super().__init__(analysis_config=analysis_config, output_folder=output_folder)

    def _get_flux_monitor_dimensions(self) -> FluxMonitorDimensions:
        x_coords = [
            vertex.x
            for prism in self.antennas[0].dielectric
            for vertex in prism.vertices
        ]
        y_coords = [
            vertex.y
            for prism in self.antennas[0].dielectric
            for vertex in prism.vertices
        ]
        z_coords = [
            vertex.z
            for prism in self.antennas[0].dielectric
            for vertex in prism.vertices
        ]

        x_min = min(x_coords)
        x_max = max(x_coords)
        y_min = min(y_coords)
        y_max = max(y_coords)

        x_size = x_max - x_min
        y_size = y_max - y_min

        # If the cable is oriented in the x-direction, the monitor should be the y-width
        if x_size > y_size:
            x_size = 0
        # If the cable is oriented in the y-direction, the monitor should be the x-width
        else:
            y_size = 0

        dims = FluxMonitorDimensions(
            x_size=x_size,
            y_size=y_size,
            x_center=(x_min + x_max) / 2,
            y_center=(y_min + y_max) / 2,
        )
        if self.analysis_config.dimensionality == Dimensionality.THREE_DIMENSIONAL:
            z_min = min(z_coords)
            z_max = max(z_coords)
            dims.z_size = (z_max - z_min) + 2
            dims.z_center = (z_min + z_max) / 2

        return dims

    def _get_flux_region(self, sim: mp.Simulation) -> mp.DftFlux:
        f_start = 0.0
        f_stop = 0.6
        number_of_frequencies = 1024
        f_center = (f_stop + f_start) / 2.0
        df = f_stop - f_start
        dims = self._get_flux_monitor_dimensions()
        flux_monitor_volume = mp.FluxRegion(
            center=mp.Vector3(x=dims.x_center, y=dims.y_center, z=dims.z_center),
            size=mp.Vector3(x=dims.x_size, y=dims.y_size, z=dims.z_size),
            direction=-mp.Y,
        )
        return sim.add_flux(
            f_center,
            df,
            number_of_frequencies,
            flux_monitor_volume,
        )

    def _get_sources(self) -> list[mp.Source]:
        sources = []
        for antenna in self.antennas:
            antenna.set_source()
            sources.extend(antenna.sources)
        return sources

    def run_sim(self):
        self._create_antennas()
        sim = self.setup_sim()
        flux_monitor = self._get_flux_region(sim=sim)
        if self.analysis_config.dimensionality == Dimensionality.TWO_DIMENSIONAL:
            plot_surfaces(sim=sim, output_folder=self.output_folder, file_name="vswr_surfaces")
        sim.run(until=SIM_TIMESTEPS)
        normalization_run = sim.get_flux_data(flux_monitor)
        normalization_flux = mp.get_fluxes(flux_monitor)
        sim.reset_meep()

        sim = self.setup_sim()
        flux_monitor = self._get_flux_region(sim=sim)
        sim.load_minus_flux_data(flux_monitor, normalization_run)
        sim.run(until=2 * SIM_TIMESTEPS)
        reflection_flux = mp.get_fluxes(flux_monitor)
        flux_frequencies = mp.get_flux_freqs(flux_monitor)

        frequencies = np.array(flux_frequencies) * 30
        gamma = np.abs(np.divide(reflection_flux,normalization_flux))
        vswr = (1 + gamma) / (1 - gamma)
        df = pd.DataFrame(
            {
                "frequencies": frequencies,
                "gamma": gamma,
                "vswr": vswr,
            }
        )
        self.results = VSWRResults(
            frequencies=frequencies, gamma=gamma, vswr=vswr, df=df
        )
        self.results.df.to_csv(f"{self.output_folder}/vswr_results.csv")

    def plot_results(self, lab_data_file: Path | str | None = None):
        plot_vswr(
            sim_results=self.results,
            output_folder=self.output_folder,
            lab_data_file=lab_data_file,
        )