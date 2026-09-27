from models import Plane, RadPatternAnalysisConfig
from utilities import frequency_ghz2meep

"""
If you want to enter any of the frequencies in GHz, use the frequency_ghz2meep function
Ex: steering_beam_base_frequency = frequency_ghz2meep(3)

"""


ANALYSIS_CONFIG_1HORN = RadPatternAnalysisConfig(
    steering_beam_base_frequency=0.1,
    source_amplitude=1.0,
    sweep_start=0.1989,
    sweep_end=0.2,
    d_f=0.1,
    phase=0.0,
    plane=Plane.E_PLANE,
    d_phase=1.5,
    num_antenna=1,
    y_offset=10,
)
ANALYSIS_CONFIG_3HORNS = RadPatternAnalysisConfig(
    steering_beam_base_frequency=0.1,
    source_amplitude=1.0,
    sweep_start=0.1989,
    sweep_end=0.4,
    d_f=0.1,
    phase=0.0,
    plane=Plane.E_PLANE,
    d_phase=1.5,
    num_antenna=3,
    y_offset=10,
)
