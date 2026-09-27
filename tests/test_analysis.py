import math
import unittest

import tests.mock_models as mm
from analysis import CELL_PADDING
from rad_pattern_analysis import RadPatternAnalysis


class TestAnalysis(unittest.TestCase):
    def test_get_cell_dimensions_2D(self):
        mock_analysis = RadPatternAnalysis(
            analysis_config=mm.MOCK_ANALYSIS_CONFIG_RAD_2D,
            output_folder="test",
        )
        mock_analysis.geometry = mm.MOCK_GEOMETRY
        mock_vertices = [
            vertice for prism in mock_analysis.geometry for vertice in prism.vertices
        ]
        max_x = max([abs(vertice.x) for vertice in mock_vertices])
        max_y = max([abs(vertice.y) for vertice in mock_vertices])

        res = mock_analysis._get_cell_dimensions()

        self.assertEqual(res[0], math.ceil(max_x + CELL_PADDING) * 2)
        self.assertEqual(res[1], math.ceil(max_y + CELL_PADDING) * 2)
        self.assertEqual(res[2], 0)  # Should be 0 because analysis is 2D

    def test_get_cell_dimensions_3D(self):
        mock_analysis = RadPatternAnalysis(
            analysis_config=mm.MOCK_ANALYSIS_CONFIG_RAD_3D,
            output_folder="test",
        )
        mock_analysis.geometry = mm.MOCK_GEOMETRY
        mock_vertices = [
            vertice for prism in mock_analysis.geometry for vertice in prism.vertices
        ]
        max_x = max([abs(vertice.x) for vertice in mock_vertices])
        max_y = max([abs(vertice.y) for vertice in mock_vertices])
        max_z = max([abs(vertice.z) for vertice in mock_vertices])

        res = mock_analysis._get_cell_dimensions()

        self.assertEqual(res[0], math.ceil(max_x + CELL_PADDING) * 2)
        self.assertEqual(res[1], math.ceil(max_y + CELL_PADDING) * 2)
        self.assertEqual(res[2], math.ceil(max_z + CELL_PADDING) * 2)
