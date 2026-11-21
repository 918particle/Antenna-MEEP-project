from dataclasses import dataclass
from pathlib import Path

import meep as mp
import numpy as np
import pandas as pd

from analysis import Analysis
from models import (
    AnalysisConfig,
    Dimensionality,
    Direction,
    VSWRResults,
)
from utilities import (
    get_cell_dimensions,
    get_geometry_dimensions,
    get_geometry_orientation,
    plot_surfaces,
    plot_vswr,
)

SIM_TIMESTEPS = 115
FLUX_MONITOR_PADDING = 0


@dataclass
class FluxMonitorDimensions:
    """Dataclass storing dimensions for a flux monitor.

    Attributes:
        x_size (float): Size in x dimension.
        y_size (float): Size in y dimension.
        z_size (float): Size in z dimension. Defaults to 0.
        x_center (float): Center point in x.
        y_center (float): Center point in y.
        z_center (float): Center point in z. Defaults to 0.
    """

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
        cable_dir = get_geometry_orientation(self.cable_only_geometry)
        cable_dims = get_geometry_dimensions(self.antennas[0].cable_only_geometry)
        x_size = cable_dims.x_dim
        y_size = cable_dims.y_dim
        if cable_dir == Direction.Y_DIR:
            # antenna is automatically centered at 0,0
            # want midpoint between source and end of cable at antenna
            # so that point is half of source center point
            y_center = self.antennas[0].sources[0].center.y / 2
            x_center = self.antennas[0].sources[0].center.x
            y_size = 0
        else:
            # antenna is automatically centered at 0,0
            # want midpoint between source and end of cable at antenna
            # so that point is half of source center point
            x_center = self.antennas[0].sources[0].center.x / 2
            y_center = self.antennas[0].sources[0].center.y
            x_size = 0

        dims = FluxMonitorDimensions(
            x_size=x_size,
            y_size=y_size,
            x_center=x_center,
            y_center=y_center,
        )
        if self.analysis_config.dimensionality == Dimensionality.THREE_DIMENSIONAL:
            dims.z_size = cable_dims.z_dim
            dims.z_center = cable_dims.z_dim / 2

        return dims

    def _get_flux_region(self, sim: mp.Simulation, direction: Direction) -> mp.DftFlux:
        f_start = 0.0
        f_stop = 0.6
        number_of_frequencies = 1024
        f_center = (f_stop + f_start) / 2.0
        df = f_stop - f_start
        dims = self._get_flux_monitor_dimensions()
        if direction == Direction.X_DIR:
            meep_dir = mp.X
        else:
            meep_dir = mp.Y
        flux_monitor_volume = mp.FluxRegion(
            center=mp.Vector3(x=dims.x_center, y=dims.y_center, z=dims.z_center),
            size=mp.Vector3(x=dims.x_size, y=dims.y_size, z=dims.z_size),
            direction=meep_dir,
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
            antenna.set_source(
                x_offset=self.x_centering_adjustment,
                y_offset=self.y_centering_adjustment,
            )
            sources.extend(antenna.sources)
        return sources

    def run_sim(self):
        self._create_antennas()
        self._get_centering_adjustment()
        cell_dims = get_cell_dimensions(
            geometry=self.antenna_only_geometry,
            analysis_config=self.analysis_config,
            cell_padding=10,
            x_shift=self.x_centering_adjustment,
            y_shift=self.y_centering_adjustment,
            cable_geometry=self.cable_only_geometry,
        )
        cable_orientation = get_geometry_orientation(self.cable_only_geometry)

        self._create_antennas(
            only_cable=True,
            cell_dims=cell_dims,
        )  # first pass was to get centering adjustment, which included creating the antenna in addition to cable

        sim1 = self.setup_sim(only_cable=True, cell_dims=cell_dims)
        flux_monitor1 = self._get_flux_region(sim=sim1, direction=cable_orientation)
        if self.analysis_config.dimensionality == Dimensionality.TWO_DIMENSIONAL:
            plot_surfaces(
                sim=sim1,
                output_folder=self.output_folder,
                file_name="vswr_surfaces_only_cable",
            )
        sim1.run(until=SIM_TIMESTEPS)
        normalization_run = sim1.get_flux_data(flux_monitor1)
        normalization_flux = mp.get_fluxes(flux_monitor1)

        self._create_antennas()
        sim2 = self.setup_sim(cell_dims=cell_dims)
        flux_monitor2 = self._get_flux_region(sim=sim2, direction=cable_orientation)
        if self.analysis_config.dimensionality == Dimensionality.TWO_DIMENSIONAL:
            plot_surfaces(
                sim=sim2, output_folder=self.output_folder, file_name="vswr_surfaces"
            )
        sim2.load_minus_flux_data(flux_monitor2, normalization_run)
        sim2.run(until=SIM_TIMESTEPS)
        reflection_flux = mp.get_fluxes(flux_monitor2)
        flux_frequencies = mp.get_flux_freqs(flux_monitor2)

        frequencies = np.array(flux_frequencies)
        gamma = np.abs(np.divide(reflection_flux, normalization_flux))
        vswr = (1 + np.sqrt(gamma)) / (1 - np.sqrt(gamma))
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
