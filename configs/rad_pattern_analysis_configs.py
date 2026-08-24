from models import Plane, RadPatternAnalysisConfig

ANALYSIS_CONFIG_1HORN_RAD_PATTERN = RadPatternAnalysisConfig(
    steering_beam_base_frequency=0.1,
    source_amplitude=1.0,
    sweep_start=0.1989,
    sweep_end=0.4,
    d_f=0.1,
    phase=0.0,
    plane=Plane.E_PLANE,
    d_phase=1.5,
    num_antenna=2,
    y_offset=10,
)
