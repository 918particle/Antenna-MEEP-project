import copy
from unittest.mock import MagicMock

import meep as mp

import models as mds

MOCK_PRISM1 = mp.Prism(
    vertices=[
        mp.Vector3(0.5, -14, -1),
        mp.Vector3(0.5, -14.8, -1),
        mp.Vector3(1, -14.5, -1),
        mp.Vector3(1, -14, -1),
    ],
    height=3,
    axis=mp.Vector3(0, 0, 1),
)
MOCK_PRISM2 = mp.Prism(
    vertices=[
        mp.Vector3(-0.3, 12, -1),
        mp.Vector3(-0.3, 12.5, 1),
        mp.Vector3(-1, -14.5, 1),
        mp.Vector3(-1, -14, -1),
    ],
    height=3,
    axis=mp.Vector3(0, 0, 1),
)
MOCK_PRISM3 = mp.Prism(
    vertices=[
        mp.Vector3(-0.3, 14, -1),
        mp.Vector3(-0.3, 12.6, 1),
        mp.Vector3(-1, -14.5, 1),
        mp.Vector3(-1, -14, -1),
    ],
    height=3,
    axis=mp.Vector3(0, 0, 1),
)
MOCK_GEOMETRY = [MOCK_PRISM1, MOCK_PRISM2, MOCK_PRISM3]


MOCK_ANALYSIS_CONFIG_2D = mds.AnalysisConfig(
    antenna_config=MagicMock(spec=mds.AntennaConfig),
    resolution=20,
    dimensionality=mds.Dimensionality.TWO_DIMENSIONAL,
    analysis_type_config=MagicMock()
)
MOCK_ANALYSIS_CONFIG_RAD_2D = copy.copy(MOCK_ANALYSIS_CONFIG_2D)
MOCK_ANALYSIS_CONFIG_RAD_2D.analysis_type = mds.AnalysisType.RAD_PATTERN