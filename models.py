from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum, auto
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import NDArray


class Plane(StrEnum):
    E_PLANE = auto()
    H_PLANE = auto()


class Dimensionality(StrEnum):
    TWO_DIMENSIONAL = auto()
    THREE_DIMENSIONAL = auto()


class AnalysisType(StrEnum):
    RAD_PATTERN = auto()
    VSWR = auto()


class AntennaType(StrEnum):
    RF_HORN = auto()


@dataclass
class GDSIIFileConfigHorn:
    """Configuration for a GDSII file for an RF horn.

    Attributes:
        file_path (str): Relative path to the GDSII file of the RF horn.
        horn_sides_layer (int): Layer number containing the side walls of the RF horn.
        conductive_layer (int): Layer number containing the conductive layer of the RF horn.
        dielectric_layer (int): Layer number containing the dielectric layer of the RF horn.
        source_layer (int): Layer number containing the source for the RF horn.
        horn_top_layer (int): Layer number containing the top layer of the RF horn.
        back_plug_layer (int): Layer number containing the back plug of the RF horn.

    Raises:
        FileNotFoundError: Raised when path of file_path is not found
    """

    file_path: Path | str
    horn_sides_layer: int
    conductive_layer: int
    dielectric_layer: int
    source_layer: int
    horn_top_layer: int
    back_plug_layer: int

    def __post_init__(self):
        self.file_path = Path(self.file_path)

        if not self.file_path.exists():
            raise FileNotFoundError(
                f"The provided path for GDSII file does not exist: {self.file_path}"
            )


@dataclass
class AntennaConfig:
    """Configuration for an antenna. Units are in Meep units.

    Attributes:
        antenna_type (AntennaType): Type of antenna. Currently just RF Horn but options will be added at a later time.
        gdsii_file_config (GDSIIFileConfigHorn): Config for GDSII file of antenna.
        xy_thickness (float): Thickness in direction of xy plane. Defaults to 1.0.
        z_thickness (float): Thickness in direction of z plane. Defaults to 0.0.
    """

    antenna_type: AntennaType
    # TODO: when new antenna types are added, add other GDSII file config types to typehint
    gdsii_file_config: GDSIIFileConfigHorn
    xy_thickness: float = 1.0
    z_thickness: float = 0.0

    def __post_init__(self):
        if self.antenna_type == AntennaType.RF_HORN:
            if not isinstance(self.gdsii_file_config, GDSIIFileConfigHorn):
                raise TypeError(
                    "RF Horn antenna type must have type GDSIIFileConfigHorn for gdsii_file_config"
                )
        # TODO: when new antenna types are added, add file config agreement checks
        else:
            pass


@dataclass
class RadPatternAnalysisConfig:
    """Configuration for radiation pattern analysis. Units are in Meep units.

    Attributes:
        source_frequency (float):
        steering_beam_base_frequency (float):
        sweep_start (float): Frequency to start the sweep.
        sweep_end (float): Frequency to end the sweep.
        phase (float): The phase of the sweep frequency and first antenna's base frequency.
        df (float): Frequency steps to take during sweep between sweep_start and sweep_end.
        plane (Plane): Plane for analysis.
        d_phase(float): The scalar difference in phase between each antenna's base frequency. Defaults to 1.5.
    """

    source_frequency: float
    steering_beam_base_frequency: float
    sweep_start: float
    sweep_end: float
    phase: float = 0.0
    d_f: float
    plane: Plane
    d_phase: float = 1.5

    analysis_type: AnalysisType = field(init=False)

    def __post_init__(self):
        self.analysis_type = AnalysisType.RAD_PATTERN


@dataclass
class VSWRAnalysisConfig:
    """Configuration for VSWR analysis. Units are in Meep units.

    Attributes:
        source_sigma: Sigma for the pulse source function.
        source_mu: Mu for the source pulse function.
    """

    source_sigma: float
    source_mu: float
    analysis_type: AnalysisType = field(init=False)

    def __post_init__(self):
        self.analysis_type = AnalysisType.VSWR


@dataclass
class AnalysisConfig:
    """Configuration for analysis. Units are in Meep units.

    Attributes:
        antenna_config (AntennaConfig): Config of antenna to analyze.
        num_antenna (int): Number of antennas in array.
        resolution (int): Number of pixels per distance unit.
        dimensionality (Dimensionality): Number of dimensions to analyze.
        x_offset (float): The offset in the x direction between antenna. Defaults to 0.0.
        y_offset (float): The offset in the y direction between antenna. Defaults to 0.0.
        dpml (float): Thickness of perfectly matched layer (PML). Defaults to 1.0.
        analysis_type_config (RadPatternAnalysisConfig | VSWRAnalysisConfig): Config for type of analysis to perform.
    """

    antenna_config: AntennaConfig
    num_antenna: int
    resolution: int
    dimensionality: Dimensionality
    analysis_type_config: RadPatternAnalysisConfig | VSWRAnalysisConfig
    x_offset: float = 0.0
    y_offset: float = 0.0
    dpml: float = 1.0
    analysis_type: AnalysisType = field(init=False)

    def __post_init__(self):
        self.analysis_type = self.analysis_type_config.analysis_type


@dataclass
class Near2FarDimensions:
    x_size: float
    y_size: float
    x_center: float
    y_center: float
    z_size: float | None = None
    z_center: float | None = None


@dataclass
class RadPatternResult:
    """Result of a run of radiation pattern analysis for a singular frequency.

    Attributes:
        frequency (float): Frequency of the run that produced this result. Units: Meep units.
        angles (NDArray[np.float32]): Angles analyzed. 1D array. Units: Radians.
        directivity (NDArray[np.float64]): Directivity expressed in decibles. 1D array. Units: dBi.
    """

    frequency: float
    angles: NDArray[np.float32]
    directivity: NDArray[np.float64]


@dataclass
class RadPatternAllResults:
    """_summary_

    Attributes:
        frequencies (NDArray[np.float32]): Frequencies analyzed. 1D array. Units: Radians.
        angles (NDArray[np.float32]): Angles analyzed. 1D array. Units: Radians.
        directivity (NDArray[np.float64]): Directivity expressed in decibles. 2D array.
                                    directivity[i, j] corresponds to the directivity at
                                    frequencies[i] and angles[j]. Units: dBi.
    """

    frequencies: NDArray[np.float32]
    angles: NDArray[np.float32]
    directivity: NDArray[np.float64]
    df: pd.DataFrame
