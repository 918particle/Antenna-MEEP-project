
import meep as mp

from antenna import Antenna
from models import AntennaConfig, Dimensionality, SourceConfig


class RFHorn(Antenna):
    def __init__(self, antenna_config: AntennaConfig, source_config: SourceConfig):
        super().__init__(antenna_config=antenna_config, source_config=source_config)

    def _set_geometry_rad_pattern(self) -> None:
        sides = mp.get_GDSII_prisms(
            material=mp.metal,
            gdsii_filename=self._file_config.file_path,
            layer=self._file_config.horn_sides_layer,
            zmin=-self.antenna_config.z_thickness,
            zmax=self.antenna_config.z_thickness,
        )
        self.geometry.extend(sides)
        back = mp.get_GDSII_prisms(
            material=mp.metal,
            gdsii_filename=self._file_config.file_path,
            layer=self._file_config.back_plug_layer,
            zmin=-self.antenna_config.z_thickness,
            zmax=self.antenna_config.z_thickness,
        )
        self.geometry.extend(back)
        if self.dimensionality == Dimensionality.THREE_DIMENSIONAL:
            bottom = mp.get_GDSII_prisms(
                material=mp.metal,
                gdsii_filename=self._file_config.file_path,
                layer=self._file_config.horn_top_layer,
                zmin=-self.antenna_config.z_thickness,
                zmax=-self.antenna_config.z_thickness + self.antenna_config.xy_thickness,
            )
            self.geometry.extend(bottom)
            top = mp.get_GDSII_prisms(
                material=mp.metal,
                gdsii_filename=self._file_config.file_path,
                layer=self._file_config.horn_top_layer,
                zmin=self.antenna_config.z_thickness - self.antenna_config.xy_thickness,
                zmax=self.antenna_config.z_thickness,
            )
            self.geometry.extend(top)

    def _set_geometry_vswr(self) -> None:
        sides = mp.get_GDSII_prisms(
            material=mp.metal,
            gdsii_filename=self._file_config.file_path,
            layer=self._file_config.horn_sides_layer,
            zmin=-self.antenna_config.z_thickness,
            zmax=self.antenna_config.z_thickness,
        )
        self.geometry.extend(sides)
        conductors = mp.get_GDSII_prisms(
            material=mp.metal,
            gdsii_filename=self._file_config.file_path,
            layer=self._file_config.conductive_layer,
            zmin=-self.antenna_config.z_thickness,
            zmax=self.antenna_config.z_thickness,
        )
        self.geometry.extend(conductors)
        dielectric = mp.get_GDSII_prisms(
            material=mp.Medium(epsilon=2),
            gdsii_filename=self._file_config.file_path,
            layer=self._file_config.dielectric_layer,
            zmin=-self.antenna_config.z_thickness,
            zmax=self.antenna_config.z_thickness,
        )
        self.geometry.extend(dielectric)


    def _set_source_rad_pattern(
        self,
        d_phase: float,
        x_offset: float = 0.0,
        y_offset: float = 0.0,
    ):
        src_vol = mp.GDSII_vol(
            fname=self._file_config.file_path,
            layer=self._file_config.source_layer,
            zmin=-self.antenna_config.xy_thickness / 2,
            zmax=self.antenna_config.xy_thickness / 2,
        )
        src_vol.center = src_vol.center + mp.Vector3(x_offset, y_offset, 0)

        self.base_source = mp.Source(
            mp.CustomSource(
                src_func=self._rad_pattern_source_function(
                    frequency=self.source_config.base_frequency,
                    phase=self.source_config.phase + d_phase,
                ),
                start_time=0.0,
            ),
            component=mp.Ey,
            volume=src_vol,
            amplitude=1,
        )
