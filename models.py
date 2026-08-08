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
        gdsii_file_config (GDSIIFileConfigHorn): Config for GDSII file of antenna.
        xy_thickness (float): Thickness in direction of xy plane. Defaults to 1.0.
        z_thickness (float): Thickness in direction of z plane. Defaults to 0.0.
        dpml (float): Thickness of perfectly matched layer (PML). Defaults to 1.0.
    """
    # TODO: when new antenna types are added, add other GDSII file config types to typehint
    gdsii_file_config: GDSIIFileConfigHorn
    xy_thickness: float = 1.0
    z_thickness: float = 0.0
    dpml: float = 1


@dataclass
class SourceConfig:
    """Configuration for a source. Broken up into a base and sweep frequency to mimic lab setup. Units are in Meep units.

    Attributes:
        sweep_frequency (float): The frequency as part of a frequency sweep.
        base_frequency (float): Base frequency, remains constant. Defaults to 0.1.
        phase (float): The phase of the sweep frequency and first antenna's base frequency.
        d_phase(float): The scalar difference in phase between each antenna's base frequency.
    """
    sweep_frequency: float
    base_frequency: float = 0.1
    phase: float = 0.0
    phase_offset: float = 1.5


@dataclass
class RadPatternAnalysisConfig:
    """Configuration for radiation pattern analysis. Units are in Meep units.

    Attributes:
        source_frequency (float):
        steering_beam_base_frequency (float):
        sweep_start (float): Frequency to start the sweep.
        sweep_end (float): Frequency to end the sweep.
        df (float): Frequency steps to take during sweep between sweep_start and sweep_end.
        plane (Plane): Plane for analysis.
    """

    source_frequency: float
    steering_beam_base_frequency: float
    sweep_start: float
    sweep_end: float
    df: float
    plane: Plane
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
        rf_horn_config (AntennaConfig): Config of antenna to analyze.
        num_antenna (int): Number of antennas in array.
        resolution (int): Number of pixels per distance unit.
        dimensionality (Dimensionality): Number of dimensions to analyze.
        analysis_type_config (RadPatternAnalysisConfig | VSWRAnalysisConfig): Config for type of analysis to perform.
    """

    rf_horn_config: AntennaConfig
    num_antenna: int
    resolution: int
    dimensionality: Dimensionality
    analysis_type_config: RadPatternAnalysisConfig | VSWRAnalysisConfig
    analysis_type: AnalysisType = field(init=False)

    def __post_init__(self):
        self.analysis_type = self.analysis_type_config.analysis_type


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
