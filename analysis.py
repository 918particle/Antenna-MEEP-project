import os
from abc import ABC, abstractmethod
from pathlib import Path

import meep as mp

from antenna import Antenna
from models import AnalysisConfig, AnalysisType, AntennaType, Dimensionality
from rf_horn import RFHorn
from utilities import plot_surfaces, resolve_output_folder

ANTENNA_CLASSES = {AntennaType.RF_HORN: RFHorn}


class Analysis(ABC):
    def __init__(
        self,
        analysis_config: AnalysisConfig,
        output_folder: Path | str,
        max_parallelization: int = os.cpu_count() - 1,
    ):
        self.analysis_config = analysis_config
        self.analysis_type_config = analysis_config.analysis_type_config
        self.antenna_config = analysis_config.antenna_config
        self.max_parallelization = max_parallelization

        self.output_folder: Path | None = None
        self.antennas: list[Antenna] | None = None
        self.geometry: list[mp.GeometricObject] | None = None

        self._set_up_output_directory(output_folder=output_folder)

    def _set_up_output_directory(self, output_folder):
        output_folder_path = Path(__file__).parent / output_folder
        output_folder_path = resolve_output_folder(output_folder=output_folder)
        output_folder_path.mkdir(exist_ok=True)
        self.output_folder = output_folder_path

    def _create_antennas(self):
        self.antennas = []
        self.geometry = []
        if self.analysis_config.analysis_type == AnalysisType.RAD_PATTERN:
            num_antenna = self.analysis_type_config.num_antenna
            x_offset = self.analysis_type_config.x_offset
            y_offset = self.analysis_type_config.y_offset
        else:  # VSWR
            num_antenna = 1
            x_offset = 0
            y_offset = 0

        # TODO: make it so it can create copies of the antenna and shift over
        # instead of creating whole new antenna every time?
        for i in range(num_antenna):
            antenna: Antenna = ANTENNA_CLASSES[self.antenna_config.antenna_type](
                analysis_config=self.analysis_config
            )
            self.antennas.append(antenna)

            antenna.set_geometry(
                x_offset=x_offset * i,
                y_offset=y_offset * i,
            )
            self.geometry.extend(antenna.geometry)

    @abstractmethod
    def _get_sources(self, **kwargs) -> list[mp.Source]:
        pass

    def setup_sim(self, **kwargs) -> mp.Simulation:
        sources = self._get_sources(**kwargs)

        if self.analysis_config.dimensionality == Dimensionality.TWO_DIMENSIONAL:
            cell_size = mp.Vector3(60, 60, 0)
        elif self.analysis_config.dimensionality == Dimensionality.THREE_DIMENSIONAL:
            cell_size = mp.Vector3(60, 60, 60)

        sim = mp.Simulation(
            resolution=self.analysis_config.resolution,
            cell_size=cell_size,
            boundary_layers=[mp.PML(self.analysis_config.dpml)],
            sources=sources,
            geometry=self.geometry,
        )
        if self.analysis_config.dimensionality == Dimensionality.TWO_DIMENSIONAL:
            plot_surfaces(sim=sim, output_folder=self.output_folder)
        return sim

    @abstractmethod
    def run_sim(self):
        pass

    @abstractmethod
    def plot_results(self, *args, **kwargs):
        pass
