from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

import meep as mp
import numpy as np
import pandas as pd
from numpy.typing import NDArray

from analysis import Analysis
from models import (
    AnalysisConfig,
    Dimensionality,
    Near2FarDimensions,
    Plane,
    RadPatternResults,
)
from utilities import plot_radiation_pattern

N2F_BOX_MARGIN = 1


@dataclass
class Result:
    """Result of a run of radiation pattern analysis for a singular frequency.

    Attributes:
        frequency (float): Frequency of the run that produced this result. Units: Meep units.
        angles (NDArray[np.float32]): Angles analyzed. 1D array. Units: Radians.
        directivity (NDArray[np.float64]): Directivity expressed in decibles. 1D array. Units: dBi.
    """

    frequency: float
    angles: NDArray[np.float32]
    directivity: NDArray[np.float64]


class RadPatternAnalysis(Analysis):
    def __init__(self, analysis_config: AnalysisConfig, output_folder: str):
        super().__init__(analysis_config=analysis_config, output_folder=output_folder)
        self.results: RadPatternResults | None = None

    def _get_near2far_dimensions(self) -> Near2FarDimensions:
        x_coords = [vertex.x for prism in self.geometry for vertex in prism.vertices]
        y_coords = [vertex.y for prism in self.geometry for vertex in prism.vertices]
        z_coords = [vertex.z for prism in self.geometry for vertex in prism.vertices]

        x_min = min(x_coords)
        x_max = max(x_coords)
        y_min = min(y_coords)
        y_max = max(y_coords)

        dims = Near2FarDimensions(
            x_size=(x_max - x_min) + (2 * N2F_BOX_MARGIN),
            y_size=(y_max - y_min) + (2 * N2F_BOX_MARGIN),
            x_center=(x_min + x_max) / 2,
            y_center=(y_min + y_max) / 2,
        )
        if self.analysis_config.dimensionality == Dimensionality.THREE_DIMENSIONAL:
            z_min = min(z_coords)
            z_max = max(z_coords)
            dims.z_size = (z_max - z_min) + (2 * N2F_BOX_MARGIN)
            dims.z_center = (z_min + z_max) / 2

        return dims

    def _get_near2far_region(
        self, sim: mp.Simulation, frequency: float
    ) -> mp.Near2FarRegion:
        dims = self._get_near2far_dimensions()
        if self.analysis_config.dimensionality == Dimensionality.TWO_DIMENSIONAL:
            dims.z_size = dims.y_size
            dims.z_center = 0.0

        pos_y = mp.Near2FarRegion(
            center=mp.Vector3(
                x=dims.x_center, y=dims.y_center + dims.y_size / 2, z=dims.z_center
            ),
            size=mp.Vector3(x=dims.x_size, y=0, z=dims.z_size),
            weight=+1,
        )
        neg_y = mp.Near2FarRegion(
            center=mp.Vector3(
                x=dims.x_center, y=dims.y_center - dims.y_size / 2, z=dims.z_center
            ),
            size=mp.Vector3(x=dims.x_size, y=0, z=dims.z_size),
            weight=-1,
        )
        pos_x = mp.Near2FarRegion(
            center=mp.Vector3(
                x=dims.x_center + dims.x_size / 2, y=dims.y_center, z=dims.z_center
            ),
            size=mp.Vector3(x=0, y=dims.y_size, z=dims.z_size),
            weight=+1,
        )
        neg_x = mp.Near2FarRegion(
            center=mp.Vector3(
                x=dims.x_center - dims.x_size / 2, y=dims.y_center, z=dims.z_center
            ),
            size=mp.Vector3(x=0, y=dims.y_size, z=dims.z_size),
            weight=-1,
        )
        n2fs_to_add = [pos_y, neg_y, pos_x, neg_x]

        if self.analysis_config.dimensionality == Dimensionality.THREE_DIMENSIONAL:
            pos_z = mp.Near2FarRegion(
                center=mp.Vector3(
                    x=dims.x_center, y=dims.y_center, z=dims.z_center + dims.z_size / 2
                ),
                size=mp.Vector3(x=dims.x_size, y=dims.y_size, z=0),
                weight=-1,
            )
            neg_z = mp.Near2FarRegion(
                center=mp.Vector3(
                    x=dims.x_center, y=dims.y_center, z=dims.z_center - dims.z_size / 2
                ),
                size=mp.Vector3(x=dims.x_size, y=dims.y_size, z=0),
                weight=-1,
            )
            n2fs_to_add.extend([pos_z, neg_z])

        return sim.add_near2far(
            frequency,
            0,  # nfreq
            1,  # df
            *n2fs_to_add,
        )

    def _get_sources(self, frequency: float) -> list[mp.Source]:
        sources = []
        for i, antenna in enumerate(self.antennas):
            antenna.set_source(
                x_offset=self.analysis_config.x_offset * i,
                y_offset=self.analysis_config.y_offset * i,
                frequency=frequency,
                base_phase_offset=self.analysis_type_config.d_phase * i,
            )
            sources.extend(antenna.sources)
        return sources

    def _calculate_radiation_pattern(
        self,
        frequency: float,
        sim: mp.Simulation,
        near2far_region: mp.DftNear2Far,
    ) -> Result:
        if self.analysis_type_config.plane == Plane.E_PLANE:
            npts = 360
        elif self.analysis_type_config.plane == Plane.H_PLANE:
            npts = 180
        r = 1000
        angles = 2 * np.pi / npts * np.arange(npts)
        E = np.zeros((npts, 3), dtype=np.complex128)
        H = np.zeros((npts, 3), dtype=np.complex128)
        for n in range(npts):
            ff = sim.get_farfield(
                near2far=near2far_region,
                x=mp.Vector3(r * np.cos(angles[n]), r * np.sin(angles[n])),
            )
            E[n, :] = [np.conj(ff[j]) for j in range(3)]
            H[n, :] = [ff[j + 3] for j in range(3)]
        Px = np.real(E[:, 1] * H[:, 2] - E[:, 2] * H[:, 1])
        Py = np.real(E[:, 2] * H[:, 0] - E[:, 0] * H[:, 2])
        Pz = np.real(E[:, 0] * H[:, 1] - E[:, 1] * H[:, 0])
        Pr = np.sqrt(np.square(Px) + np.square(Py) + np.square(Pz))
        directivity = 10.0 * np.log10(Pr / max(Pr))

        return Result(frequency=frequency, angles=angles, directivity=directivity)

    def _aggregate_results(
        self, base_results: list[Result], sweep_results: list[Result]
    ) -> RadPatternResults:
        frequencies = np.array([result.frequency for result in base_results])
        angles = base_results[0].angles
        base_directivity = np.stack([result.directivity for result in base_results])
        sweep_directivity = np.stack([result.directivity for result in sweep_results])

        df = pd.DataFrame(
            {
                "frequency": np.repeat(frequencies, len(angles)),
                "angle": np.tile(angles, len(frequencies)),
                "base_directivity": base_directivity.ravel(),
                "sweep_directivity": sweep_directivity.ravel(),
            }
        )
        return RadPatternResults(
            frequencies=frequencies,
            angles=angles,
            base_directivity=base_directivity,
            sweep_directivity=sweep_directivity,
            df=df,
        )

    def run_one_sim(self, frequency) -> tuple[Result, Result]:
        sim = self.setup_sim(frequency=frequency)
        base_n2f_region = self._get_near2far_region(
            sim=sim,
            frequency=self.analysis_type_config.steering_beam_base_frequency,
        )
        sweep_n2f_region = self._get_near2far_region(
            sim=sim, frequency=float(frequency)
        )
        sim.run(until=100)
        base_result = self._calculate_radiation_pattern(
            frequency=frequency,
            sim=sim,
            near2far_region=base_n2f_region,
        )
        sweep_result = self._calculate_radiation_pattern(
            frequency=frequency,
            sim=sim,
            near2far_region=sweep_n2f_region,
        )
        sim.reset_meep()
        return base_result, sweep_result

    def run_sim(self):
        self._create_antennas()
        frequencies = np.arange(
            self.analysis_type_config.sweep_start,
            self.analysis_type_config.sweep_end,
            self.analysis_type_config.d_f,
        )
        base_results = []
        sweep_results = []

        with ProcessPoolExecutor(max_workers=self.max_parallelization) as executor:
            futures = [executor.submit(self.run_one_sim, frequency) for frequency in frequencies]
            for future in as_completed(futures):
                base_result, sweep_result = future.result()
                base_results.append(base_result)
                sweep_results.append(sweep_result)

        self.results = self._aggregate_results(
            base_results=base_results, sweep_results=sweep_results
        )
        self.results.df.to_csv(f"{self.output_folder}/results.csv")

    def plot_results(self, lab_data_file: Path | str | None = None):
        plot_radiation_pattern(
            sim_results=self.results,
            output_folder=self.output_folder,
            lab_data_file=lab_data_file,
        )
