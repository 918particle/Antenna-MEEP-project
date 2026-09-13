import configs.gdsii_configs as gc
from models import AntennaConfig, AntennaType

ANTENNA_CONFIG_TEST_HORN_1 = AntennaConfig(
    antenna_type=AntennaType.RF_HORN,
    gdsii_file_config=gc.GDSII_CONFIG_TEST_HORN_1,
    horn_height=3.5,
    top_bottom_thickness=0.5,
    wire_thickness=0.5,
)
