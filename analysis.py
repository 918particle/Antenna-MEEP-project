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
    Dimensions,
    RadPatternResults,
    VSWRResults,
)
from rf_horn import RFHorn
from utilities import filter_kwargs, get_cell_dimensions, resolve_output_folder

ANTENNA_CLASSES = {AntennaType.RF_HORN: RFHorn}
CELL_PADDING = 10


class Analysis(ABC):
    def __init__(
        self,
        analysis_config: AnalysisConfig,
        output_folder: Path | str,
        max_parallelization: int = os.cpu_count() - 1,
    ):
        """_summary_

        Args:
            analysis_config (AnalysisConfig): AnalysisConfig for analysis.
            output_folder (Path | str): Relative path of folder to output results to.
            max_parallelization (int, optional): Maximum parallel tasks. Defaults to os.cpu_count()-1.
        """
        self.analysis_config = analysis_config
        self.analysis_type_config = analysis_config.analysis_type_config
        self.antenna_config = analysis_config.antenna_config
        self.max_parallelization = max_parallelization

        self.x_centering_adjustment: float | None = None
        self.y_centering_adjustment: float | None = None
        self.output_folder: Path | None = None
        self.antennas: list[Antenna] | None = None
        self.geometry: list[mp.GeometricObject] | None = None
        self.antenna_only_geometry: list[mp.GeometricObject] | None = None
        self.cable_only_geometry: list[mp.GeometricObject] | None = None
        self.results: RadPatternResults | VSWRResults | None = None

        self._set_up_output_directory(output_folder=output_folder)

    def _set_up_output_directory(self, output_folder: Path | str):
        output_folder_path = Path(__file__).parent / output_folder
        output_folder_path = resolve_output_folder(output_folder=output_folder)
        output_folder_path.mkdir(exist_ok=True)
        self.output_folder = output_folder_path

    def _get_centering_adjustment(self) -> None:
        # only center on antenna, cable should extend out past PML
        if len(self.antenna_only_geometry) > 0:
            vertices = [
                vertice
                for prism in self.antenna_only_geometry
                for vertice in prism.vertices
            ]
            x = [vertice.x for vertice in vertices]
            center_x = (max(x) + min(x)) / 2
            y = [vertice.y for vertice in vertices]
            center_y = (max(y) + min(y)) / 2
        else:
            center_x = 0
            center_y = 0

        self.x_centering_adjustment = 0 - center_x
        self.y_centering_adjustment = 0 - center_y

    def _create_antennas(
        self,
        only_cable: bool = False,
        cell_dims: Dimensions | None = None,
    ) -> None:
        self.antennas = []
        self.geometry = []
        self.antenna_only_geometry = []
        self.cable_only_geometry = []

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
            antenna.set_geometry(
                x_offset=x_offset * i,
                y_offset=y_offset * i,
                only_cable=only_cable,
                x_centering_adjustment=x_centering_adjustment,
                y_centering_adjustment=y_centering_adjustment,
                cell_dims=cell_dims,
            )
            self.antennas.append(antenna)

            self.geometry.extend(antenna.geometry)
            self.antenna_only_geometry.extend(antenna.antenna_only_geometry)
            self.cable_only_geometry.extend(antenna.cable_only_geometry)

    @abstractmethod
    def _get_sources(self, **kwargs) -> list[mp.Source]:
        pass

    def setup_sim(self, **kwargs) -> mp.Simulation:
        if not kwargs.get("cell_dims", None):
            kwargs["cell_dims"] = get_cell_dimensions(
                geometry=self.antenna_only_geometry,
                analysis_config=self.analysis_config,
                cell_padding=CELL_PADDING,
                x_shift=self.x_centering_adjustment,
                y_shift=self.y_centering_adjustment,
            )
        cell_size = mp.Vector3(
            x=kwargs["cell_dims"].x_dim,
            y=kwargs["cell_dims"].y_dim,
            z=kwargs["cell_dims"].z_dim,
        )

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
