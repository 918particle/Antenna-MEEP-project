import meep as mp
import numpy as np

from analysis import Analysis
from models import AnalysisConfig, Dimensionality, Near2FarDimensions


class RadPatternAnalysis(Analysis):
    def __init__(self, analysis_config: AnalysisConfig, output_file_base_name: str):
        super().__init__(
            analysis_config=analysis_config, output_file_base_name=output_file_base_name
        )
        self.projection_box: mp.DftNear2Far | None = None

    def _get_near2far_dimensions(self) -> Near2FarDimensions:
        x_coords = [vertex.x for prism in self.geometry for vertex in prism.vertices]
        y_coords = [vertex.y for prism in self.geometry for vertex in prism.vertices]
        z_coords = [vertex.z for prism in self.geometry for vertex in prism.vertices]

        x_min = min(x_coords)
        x_max = max(x_coords)
        y_min = min(y_coords)
        y_max = max(y_coords)

        dims = Near2FarDimensions(
            x_size=x_max - x_min,
            y_size=y_max - y_min,
            x_center=(x_min + x_max) / 2,
            y_center=(y_min + y_max) / 2,
        )
        if self.analysis_config.dimensionality == Dimensionality.THREE_DIMENSIONAL:
            z_min = min(z_coords)
            z_max = max(z_coords)
            dims.z_size = z_max - z_min
            dims.z_center = (z_min + z_max) / 2

        return dims

    def _get_projection_box(
        self, sim: mp.Simulation, frequency: float
    ) -> mp.Near2FarRegion:
        dims = self._get_near2far_dimensions()
        if self.analysis_config.dimensionality == Dimensionality.TWO_DIMENSIONAL:
            z_size = dims.y_size
            z_center = 0.0
        else:
            z_size = dims.z_size
            z_center = dims.z_center

        pos_y = mp.Near2FarRegion(
            center=mp.Vector3(
                x=dims.x_center, y=dims.y_center + dims.y_size / 2, z=z_center
            ),
            size=mp.Vector3(x=dims.x_size, y=0, z=z_size),
            weight=+1,
        )
        neg_y = mp.Near2FarRegion(
            center=mp.Vector3(
                x=dims.x_center, y=dims.y_center - dims.y_size / 2, z=z_center
            ),
            size=mp.Vector3(x=dims.x_size, y=0, z=dims.z_size),
            weight=-1,
        )
        pos_x = mp.Near2FarRegion(
            center=mp.Vector3(
                x=dims.x_center + dims.x_size / 2, y=dims.y_center, z=z_center
            ),
            size=mp.Vector3(x=0, y=dims.y_size, z=dims.z_size),
            weight=+1,
        )
        neg_x = mp.Near2FarRegion(
            center=mp.Vector3(
                x=dims.x_center - dims.x_size / 2, y=dims.y_center, z=z_center
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

    def run_sim(self):
        self._create_antennas()
        frequencies = np.arange(
            self.analysis_type_config.sweep_start,
            self.analysis_type_config.sweep_end,
            self.analysis_type_config.d_f,
        )
        for frequency in frequencies:
            sim = self.setup_sim()
            projection_box = self._get_projection_box(
                self, sim=sim, frequency=frequency
            )
