import math

import meep as mp

from models import AnalysisConfig, Dimensionality, Dimensions, Direction
from utilities import get_geometry_orientation


class Cable:
    def __init__(
        self,
        analysis_config: AnalysisConfig,
        is_infinite: bool = False,
        cell_dims: Dimensions | None = None,
    ):
        self.dimensionality: Dimensionality = analysis_config.dimensionality
        self.antenna_config = analysis_config.antenna_config
        self.is_infinite = is_infinite
        self.cell_dims = cell_dims
        self._file_config = self.antenna_config.gdsii_file_config

        self.geometry: list[mp.GeometricObject] | None = None
        self.conductor: list[mp.GeometricObject] | None = None
        self.dielectric: list[mp.GeometricObject] | None = None

        if is_infinite and not isinstance(cell_dims, Dimensions):
            raise ValueError("When 'is_infinite' is True, cell_dims must be provided.")

    def set_geometry(self) -> None:
        self.geometry = []

        wire = mp.get_GDSII_prisms(
            material=mp.metal,
            GDSIIFile=str(self._file_config.file_path),
            Layer=self._file_config.wire_layer,
            zmin=-self.antenna_config.wire_thickness / 2,
            zmax=self.antenna_config.wire_thickness / 2,
        )
        self.geometry.extend(wire)

        main_conductor = mp.get_GDSII_prisms(
            material=mp.metal,
            GDSIIFile=str(self._file_config.file_path),
            Layer=self._file_config.main_conductive_layer,
            zmin=-self.antenna_config.antenna_height / 2,
            zmax=self.antenna_config.antenna_height / 2,
        )
        self.conductor = main_conductor
        self.geometry.extend(main_conductor)

        main_dielectric = mp.get_GDSII_prisms(
            material=mp.Medium(epsilon=2),
            GDSIIFile=str(self._file_config.file_path),
            Layer=self._file_config.main_dielectric_layer,
            zmin=-self.antenna_config.antenna_height / 2
            + self.antenna_config.top_bottom_thickness,
            zmax=self.antenna_config.antenna_height / 2
            - self.antenna_config.top_bottom_thickness,
        )
        self.dielectric = main_dielectric
        self.geometry.extend(main_dielectric)

        if self.dimensionality == Dimensionality.THREE_DIMENSIONAL:
            top_conductor = mp.get_GDSII_prisms(
                material=mp.metal,
                GDSIIFile=str(self._file_config.file_path),
                Layer=self._file_config.top_bottom_conductive_layer,
                zmin=-self.antenna_config.antenna_height / 2,
                zmax=-self.antenna_config.antenna_height / 2
                + self.antenna_config.top_bottom_thickness,
            )
            self.geometry.extend(top_conductor)

            bottom_conductor = mp.get_GDSII_prisms(
                material=mp.metal,
                GDSIIFile=str(self._file_config.file_path),
                Layer=self._file_config.top_bottom_conductive_layer,
                zmin=self.antenna_config.antenna_height / 2
                - self.antenna_config.top_bottom_thickness,
                zmax=self.antenna_config.antenna_height / 2,
            )
            self.geometry.extend(bottom_conductor)

            top_dielectric = mp.get_GDSII_prisms(
                material=mp.Medium(epsilon=2),
                GDSIIFile=str(self._file_config.file_path),
                Layer=self._file_config.top_bottom_dielectric_layer,
                zmin=self.antenna_config.wire_thickness,
                zmax=self.antenna_config.antenna_height / 2
                - self.antenna_config.top_bottom_thickness,
            )
            self.geometry.extend(top_dielectric)

            bottom_dielectric = mp.get_GDSII_prisms(
                material=mp.Medium(epsilon=2),
                GDSIIFile=str(self._file_config.file_path),
                Layer=self._file_config.top_bottom_dielectric_layer,
                zmin=-self.antenna_config.antenna_height / 2
                + self.antenna_config.top_bottom_thickness,
                zmax=-self.antenna_config.wire_thickness,
            )
            self.geometry.extend(bottom_dielectric)

        if self.is_infinite:
            self._extend_geometry_past_edge()

    def _update_prism_bounds(
        self, prism: mp.Prism, direction: Direction, new_end: float
    ):
        # get the maximum and minimum x or y
        if direction == Direction.Y_DIR:
            y_min = min(v.y for v in prism.vertices)
            y_max = max(v.y for v in prism.vertices)
            x_min = None
            x_max = None
        else:
            x_min = min(v.x for v in prism.vertices)
            x_max = max(v.x for v in prism.vertices)
            y_min = None
            y_max = None

        # if vertice is closer to min then it needs to extend to bottom bound of cell, else top bound
        if direction == Direction.Y_DIR:
            prism.vertices = [
                mp.Vector3(
                    v.x,
                    -new_end
                    if abs(v.y - y_min) < abs(v.y - y_max)
                    else new_end,
                    v.z,
                )
                for v in prism.vertices
            ]
        else:
            prism.vertices = [
                mp.Vector3(
                    -new_end
                    if abs(v.x - x_min) < abs(v.x - x_max)
                    else new_end,
                    v.y,
                    v.z,
                )
                for v in prism.vertices
            ]

    def _extend_geometry_past_edge(self):
        dir = get_geometry_orientation(self.geometry)
        if dir == Direction.X_DIR:
            new_cable_end = self.cell_dims.x_dim + 1
        else:
            new_cable_end = self.cell_dims.y_dim + 1

        # for prism in self.geometry:
        #     self._update_prism_bounds(prism=prism, direction=dir, new_end=new_cable_end)
