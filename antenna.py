from collections.abc import Callable

import meep as mp
import numpy as np

from models import AnalysisType, AntennaConfig, Dimensionality, SourceConfig


class Antenna:
    def __init__(self, antenna_config: AntennaConfig, source_config: SourceConfig):
        self.antenna_config = antenna_config
        self.source_config = source_config
        self._file_config = self.antenna_config.gdsii_file_config

        self.dimensionality: Dimensionality | None = None
        self.geometry: list[mp.GeometricObject] | None = None
        self.base_source: mp.Source | None = None

    def _shift_antenna(self, x_offset: float = 0.0, y_offset: float = 0.0) -> None:
        for obj in self.geometry:
            obj = obj.shift(mp.Vector3(x_offset, y_offset, 0))

    def _rad_pattern_source_function(
        self, frequency, phase
    ) -> Callable[[float], float]:
        omega = 2.0 * np.pi * frequency
        return lambda t: np.sin(omega * t + phase * np.pi / 180.0)

    def _set_geometry_rad_pattern(self) -> None:
        raise NotImplementedError(
            "Child function did not implement _set_geometry_rad_pattern"
        )

    def _set_geometry_vswr(self) -> None:
        raise NotImplementedError("Child function did not implement _set_geometry_vswr")

    def set_geometry(
        self,
        dimensionality: Dimensionality,
        analysis_type: AnalysisType,
        x_offset: float = 0.0,
        y_offset: float = 0.0,
    ) -> None:
        self.dimensionality = dimensionality
        self.geometry = []

        if analysis_type == AnalysisType.RAD_PATTERN:
            self._set_geometry_rad_pattern()
        else:
            self._set_geometry_vswr()

        self._shift_antenna(x_offset=x_offset, y_offset=y_offset)
