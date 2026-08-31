import configs.antenna_configs as ac
import configs.rad_pattern_analysis_configs as rpac
import configs.vswr_analysis_configs as vac
from models import AnalysisConfig, Dimensionality

ANALYSIS_CONFIG_HORN_RAD_PATTERN = AnalysisConfig(
    antenna_config=ac.ANTENNA_CONFIG_TEST_HORN_1,
    resolution=20,
    dimensionality=Dimensionality.TWO_DIMENSIONAL,
    analysis_type_config=rpac.ANALYSIS_CONFIG_1HORN,
)
ANALYSIS_CONFIG_HORN_RAD_PATTERN_3D = AnalysisConfig(
    antenna_config=ac.ANTENNA_CONFIG_TEST_HORN_1,
    resolution=20,
    dimensionality=Dimensionality.THREE_DIMENSIONAL,
    analysis_type_config=rpac.ANALYSIS_CONFIG_1HORN,
)
ANALYSIS_CONFIG_HORN_VSWR = AnalysisConfig(
    antenna_config=ac.ANTENNA_CONFIG_TEST_HORN_1,
    resolution=20,
    dimensionality=Dimensionality.TWO_DIMENSIONAL,
    analysis_type_config=vac.ANALYSIS_CONFIG_1HORN,
)
