import configs.antenna_configs as ac
import configs.rad_pattern_analysis_configs as rcac
from models import AnalysisConfig, Dimensionality

ANALYSIS_CONFIG_1HORN_RAD_PATTERN = AnalysisConfig(
    antenna_config=ac.ANTENNA_CONFIG_TEST_HORN_1,
    resolution=20,
    dimensionality=Dimensionality.TWO_DIMENSIONAL,
    analysis_type_config=rcac.ANALYSIS_CONFIG_1HORN_RAD_PATTERN,
)
ANALYSIS_CONFIG_1HORN_RAD_PATTERN2 = AnalysisConfig(
    antenna_config=ac.ANTENNA_CONFIG_TEST_HORN_1,
    resolution=20,
    dimensionality=Dimensionality.TWO_DIMENSIONAL,
    analysis_type_config=rcac.ANALYSIS_CONFIG_1HORN_RAD_PATTERN,
)
