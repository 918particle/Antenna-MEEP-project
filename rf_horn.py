import meep as mp

from antenna import Antenna
from models import AnalysisConfig, Dimensionality


class RFHorn(Antenna):
    def __init__(self, analysis_config: AnalysisConfig):
        super().__init__(analysis_config=analysis_config)

    def _set_top_bottom_geometry(self) -> None:
        bottom = mp.get_GDSII_prisms(
            material=mp.metal,
            GDSIIFile=str(self._file_config.file_path),
            Layer=self._file_config.horn_top_layer,
            zmin=-self.antenna_config.horn_height / 2,
            zmax=-self.antenna_config.horn_height / 2
            + self.antenna_config.top_bottom_thickness,
        )
        self.geometry.extend(bottom)
        top = mp.get_GDSII_prisms(
            material=mp.metal,
            GDSIIFile=str(self._file_config.file_path),
            Layer=self._file_config.horn_top_layer,
            zmin=self.antenna_config.horn_height / 2
            - self.antenna_config.top_bottom_thickness,
            zmax=self.antenna_config.horn_height / 2,
        )
        self.geometry.extend(top)

    def _set_sides_geometry(self) -> None:
        sides = mp.get_GDSII_prisms(
            material=mp.metal,
            GDSIIFile=str(self._file_config.file_path),
            Layer=self._file_config.horn_sides_layer,
            zmin=-self.antenna_config.horn_height / 2,
            zmax=self.antenna_config.horn_height / 2,
        )
        self.geometry.extend(sides)

    def _set_geometry_rad_pattern(self) -> None:
        self._set_sides_geometry()
        back = mp.get_GDSII_prisms(
            material=mp.metal,
            GDSIIFile=str(self._file_config.file_path),
            Layer=self._file_config.back_plug_layer,
            zmin=-self.antenna_config.horn_height / 2,
            zmax=self.antenna_config.horn_height / 2,
        )
        self.geometry.extend(back)

        if self.dimensionality == Dimensionality.THREE_DIMENSIONAL:
            self._set_top_bottom_geometry()

    def _set_geometry_vswr_only_cable(self) -> None:
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
            zmin=-self.antenna_config.horn_height / 2,
            zmax=self.antenna_config.horn_height / 2,
        )
        self.conductor = main_conductor
        self.geometry.extend(main_conductor)

        main_dielectric = mp.get_GDSII_prisms(
            material=mp.Medium(epsilon=2),
            GDSIIFile=str(self._file_config.file_path),
            Layer=self._file_config.main_dielectric_layer,
            zmin=-self.antenna_config.horn_height / 2
            + self.antenna_config.top_bottom_thickness,
            zmax=self.antenna_config.horn_height / 2
            - self.antenna_config.top_bottom_thickness,
        )
        self.dielectric = main_dielectric
        self.geometry.extend(main_dielectric)

        if self.dimensionality == Dimensionality.THREE_DIMENSIONAL:
            top_conductor = mp.get_GDSII_prisms(
                material=mp.metal,
                GDSIIFile=str(self._file_config.file_path),
                Layer=self._file_config.top_bottom_conductive_layer,
                zmin=-self.antenna_config.horn_height / 2,
                zmax=-self.antenna_config.horn_height / 2
                + self.antenna_config.top_bottom_thickness,
            )
            self.geometry.extend(top_conductor)

            bottom_conductor = mp.get_GDSII_prisms(
                material=mp.metal,
                GDSIIFile=str(self._file_config.file_path),
                Layer=self._file_config.top_bottom_conductive_layer,
                zmin=self.antenna_config.horn_height / 2
                - self.antenna_config.top_bottom_thickness,
                zmax=self.antenna_config.horn_height / 2,
            )
            self.geometry.extend(bottom_conductor)

            top_dielectric = mp.get_GDSII_prisms(
                material=mp.Medium(epsilon=2),
                GDSIIFile=str(self._file_config.file_path),
                Layer=self._file_config.top_bottom_dielectric_layer,
                zmin=self.antenna_config.wire_thickness,
                zmax=self.antenna_config.horn_height / 2
                - self.antenna_config.top_bottom_thickness,
            )
            self.geometry.extend(top_dielectric)

            bottom_dielectric = mp.get_GDSII_prisms(
                material=mp.Medium(epsilon=2),
                GDSIIFile=str(self._file_config.file_path),
                Layer=self._file_config.top_bottom_dielectric_layer,
                zmin=-self.antenna_config.horn_height / 2
                + self.antenna_config.top_bottom_thickness,
                zmax=-self.antenna_config.wire_thickness,
            )
            self.geometry.extend(bottom_dielectric)

    def _set_geometry_vswr(self) -> None:
        self._set_geometry_vswr_only_cable()
        self._set_sides_geometry()

        if self.dimensionality == Dimensionality.THREE_DIMENSIONAL:
            self._set_top_bottom_geometry()

    def _set_source_rad_pattern(
        self,
        frequency: float,
        base_phase_offset: float,
        x_offset: float = 0.0,
        y_offset: float = 0.0,
    ):
        src_vol = mp.GDSII_vol(
            fname=str(self._file_config.file_path),
            layer=self._file_config.source_layer,
            zmin=-self.antenna_config.wire_thickness / 2,
            zmax=self.antenna_config.wire_thickness / 2,
        )
        src_vol.center = src_vol.center + mp.Vector3(x_offset, y_offset, 0)

        self.base_source = mp.Source(
            mp.CustomSource(
                src_func=self._continuous_wave_source(
                    frequency=self.analysis_type_config.steering_beam_base_frequency,
                    amplitude=self.analysis_type_config.source_amplitude,
                    phase=self.analysis_type_config.phase + base_phase_offset,
                ),
                start_time=1,
            ),
            component=mp.Ey,
            volume=src_vol,
            amplitude=1,
        )
        self.sweep_source = mp.Source(
            mp.CustomSource(
                src_func=self._continuous_wave_source(
                    frequency=frequency,
                    amplitude=self.analysis_type_config.source_amplitude,
                    phase=self.analysis_type_config.phase,
                ),
                start_time=1,
            ),
            component=mp.Ey,
            volume=src_vol,
            amplitude=1,
        )
        self.sources = [self.base_source, self.sweep_source]

    def _set_source_vswr(self):
        src_vol = mp.GDSII_vol(
            fname=str(self._file_config.file_path),
            layer=self._file_config.source_layer,
            zmin=-self.antenna_config.wire_thickness / 2,
            zmax=self.antenna_config.wire_thickness / 2,
        )

        self.pulse_source = mp.Source(
            mp.CustomSource(
                src_func=self._pulse_source(
                    sigma=self.analysis_type_config.source_sigma,
                    mu=self.analysis_type_config.source_mu,
                ),
                start_time=1,
            ),
            component=mp.Ey,
            volume=src_vol,
            amplitude=1,
        )
        self.sources = [self.pulse_source]
