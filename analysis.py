import math
import os
from abc import ABC, abstractmethod
from pathlib import Path

import meep as mp

from antenna import Antenna
from models import (
    AnalysisConfig,
    AnalysisType,
    AntennaType,
    Dimensionality,
    RadPatternResults,
    VSWRResults,
)
from rf_horn import RFHorn
from utilities import filter_kwargs, resolve_output_folder

ANTENNA_CLASSES = {AntennaType.RF_HORN: RFHorn}
CELL_PADDING = 20


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

        self.x_centering_adjustment: float | None = None
        self.y_centering_adjustment: float | None = None
        self.output_folder: Path | None = None
        self.antennas: list[Antenna] | None = None
        self.geometry: list[mp.GeometricObject] | None = None
        self.results: RadPatternResults | VSWRResults | None = None

        self._set_up_output_directory(output_folder=output_folder)

    def _set_up_output_directory(self, output_folder):
        output_folder_path = Path(__file__).parent / output_folder
        output_folder_path = resolve_output_folder(output_folder=output_folder)
        output_folder_path.mkdir(exist_ok=True)
        self.output_folder = output_folder_path

    def _get_centering_adjustment(self) -> None:
        vertices = [vertice for prism in self.geometry for vertice in prism.vertices]
        x = [vertice.x for vertice in vertices]
        center_x = (max(x) + min(x)) / 2
        y = [vertice.y for vertice in vertices]
        center_y = (max(y) + min(y)) / 2

        self.x_centering_adjustment = 0 - center_x
        self.y_centering_adjustment = 0 - center_y

    def _create_antennas(
        self,
        only_cable: bool = False,
    ) -> None:
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

        x_centering_adjustment = self.x_centering_adjustment
        y_centering_adjustment = self.y_centering_adjustment
        if x_centering_adjustment is None:
            x_centering_adjustment = 0.0
        if y_centering_adjustment is None:
            y_centering_adjustment = 0.0

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
                only_cable=only_cable,
                x_centering_adjustment=x_centering_adjustment,
                y_centering_adjustment=y_centering_adjustment,
            )
            self.geometry.extend(antenna.geometry)

    def _get_cell_dimensions(self) -> tuple[int, int, int]:
        temp_geometry = (
            self.geometry
        )  # need to do because _create_antennas() overwrites it

        if self.analysis_config.analysis_type == AnalysisType.VSWR:
            # only need to recreate antennas for VSWR because it changes across parts of the sim (RadPattern doesn't)
            self._create_antennas(only_cable=False)

        vertices = [vertice for prism in self.geometry for vertice in prism.vertices]
        x_dim = (
            math.ceil(max([abs(vertice.x) for vertice in vertices]) + CELL_PADDING) * 2
        )
        y_dim = (
            math.ceil(max([abs(vertice.y) for vertice in vertices]) + CELL_PADDING) * 2
        )
        if self.analysis_config.dimensionality == Dimensionality.THREE_DIMENSIONAL:
            z_dim = (
                math.ceil(max([abs(vertice.z) for vertice in vertices]) + CELL_PADDING)
                * 2
            )
        else:
            z_dim = 0

        self.geometry = temp_geometry  # reset to desired geometry
        return x_dim, y_dim, z_dim

    @abstractmethod
    def _get_sources(self, **kwargs) -> list[mp.Source]:
        pass

    def setup_sim(self, **kwargs) -> mp.Simulation:
        x_dim, y_dim, z_dim = self._get_cell_dimensions()
        cell_size = mp.Vector3(x_dim, y_dim, z_dim)

        sources = self._get_sources(**filter_kwargs(self._get_sources, kwargs))

        sim = mp.Simulation(
            resolution=self.analysis_config.resolution,
            cell_size=cell_size,
            boundary_layers=[mp.PML(self.analysis_config.dpml)],
            sources=sources,
            geometry=self.geometry,
        )
        return sim

    @abstractmethod
    def run_sim(self):
        pass

    @abstractmethod
    def plot_results(self, *args, **kwargs):
        pass
