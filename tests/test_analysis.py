import unittest

import tests.mock_models as tm
from rad_pattern_analysis import RadPatternAnalysis


class TestAnalysis(unittest.TestCase):
    def test_get_cell_dimensions_2D(self):
        mock_analysis = RadPatternAnalysis(
            analysis_config=tm.MOCK_ANALYSIS_CONFIG_RAD_2D,
            output_folder="test",
        )
        mock_analysis.geometry = tm.MOCK_GEOMETRY
        res = mock_analysis._get_cell_dimensions()

