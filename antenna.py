from abc import ABC, abstractmethod
from collections.abc import Callable

import meep as mp
import numpy as np

from models import AnalysisConfig, AnalysisType, Dimensionality


class Antenna(ABC):
    def __init__(self, analysis_config: AnalysisConfig):
        self.antenna_config = analysis_config.antenna_config
        self.analysis_type_config = analysis_config.analysis_type_config
        self._file_config = self.antenna_config.gdsii_file_config
        self.dimensionality: Dimensionality = analysis_config.dimensionality

        self.geometry: list[mp.GeometricObject] | None = None
        self.conductors: list[mp.GeometricObject] | None = None
        self.dielectric: list[mp.GeometricObject] | None = None
        self.base_source: mp.Source | None = None
        self.sweep_source: mp.Source | None = None
        self.pulse_source: mp.Source | None = None
        self.sources: list[mp.Source] | None = None

    def _shift_antenna(self, x_offset: float = 0.0, y_offset: float = 0.0) -> None:
        for obj in self.geometry:
            obj.center += mp.Vector3(x_offset, y_offset, 0)
            obj.vertices = [v + mp.Vector3(x_offset, y_offset, 0) for v in obj.vertices]

    def _continuous_wave_source(
        self, frequency: float, amplitude: float, phase: float
    ) -> Callable[[float], float]:
        omega = 2.0 * np.pi * frequency
        return lambda t: amplitude * np.sin(omega * t + phase * np.pi / 180.0)

    def _pulse_source(self, sigma: float, mu: float) -> Callable[[float], float]:
        return lambda t: np.exp(-0.5 * (t - mu) * (t - mu) / sigma / sigma)

    @abstractmethod
    def _set_geometry_rad_pattern(self) -> None:
        pass

    @abstractmethod
    def _set_geometry_vswr(self) -> None:
        pass

    def set_geometry(
        self,
        x_offset: float = 0.0,
        y_offset: float = 0.0,
    ) -> None:
        self.geometry = []

        if self.analysis_type_config.analysis_type == AnalysisType.RAD_PATTERN:
            self._set_geometry_rad_pattern()
        elif self.analysis_type_config.analysis_type == AnalysisType.VSWR:
            self._set_geometry_vswr()

        self._shift_antenna(x_offset=x_offset, y_offset=y_offset)

    @abstractmethod
    def _set_source_rad_pattern(
        self,
        frequency: float,
        base_phase_offset: float,
        x_offset: float = 0.0,
        y_offset: float = 0.0,
    ):
        pass

    @abstractmethod
    def _set_source_vswr(self):
        pass

    def set_source(
        self,
        x_offset: float = 0.0,
        y_offset: float = 0.0,
        frequency: float | None = None,
        base_phase_offset: float | None = None,
    ):
        if self.analysis_type_config.analysis_type == AnalysisType.RAD_PATTERN:
            self._set_source_rad_pattern(
                x_offset=x_offset,
                y_offset=y_offset,
                frequency=frequency,
                base_phase_offset=base_phase_offset,
            )
        elif self.analysis_type_config.analysis_type == AnalysisType.VSWR:
            self._set_source_vswr()
