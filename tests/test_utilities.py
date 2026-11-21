import unittest
from pathlib import Path

from parameterized import parameterized

import tests.mock_models as mm
import utilities as u


class TestUtilities(unittest.TestCase):
    @parameterized.expand(
        [
            ("includes_directory_str", "results/test1"),
            ("without_directory_str", "test1"),
            ("includes_directory_path", Path("results/test1")),
            ("without_directory_path", Path("test1")),
        ]
    )
    def test_resolve_output_folder_includes_dir(
        self, name: str, output_folder: str | Path
    ):
        res = u.resolve_output_folder(output_folder=output_folder)

        self.assertIsInstance(res, Path)
        expected_path = (Path(__name__).parent / "results").resolve() / "test1"
        self.assertEqual(res, expected_path)

    # def test_get_cell_dimensions_2D(self):
    #     mock_analysis = RadPatternAnalysis(
    #         analysis_config=mm.MOCK_ANALYSIS_CONFIG_RAD_2D,
    #         output_folder="test",
    #     )
    #     mock_analysis.geometry = mm.MOCK_GEOMETRY
    #     mock_vertices = [
    #         vertice for prism in mock_analysis.geometry for vertice in prism.vertices
    #     ]
    #     max_x = max([abs(vertice.x) for vertice in mock_vertices])
    #     max_y = max([abs(vertice.y) for vertice in mock_vertices])

    #     res = get_cell_dimensions(
    #         geometry=mm.MOCK_GEOMETRY,
    #         analysis_config=mock_analysis,
    #         cell_padding=CELL_PADDING,
    #     )

    #     self.assertEqual(res[0], math.ceil(max_x + CELL_PADDING) * 2)
    #     self.assertEqual(res[1], math.ceil(max_y + CELL_PADDING) * 2)
    #     self.assertEqual(res[2], 0)  # Should be 0 because analysis is 2D

    # def test_get_cell_dimensions_3D(self):
    #     mock_analysis = RadPatternAnalysis(
    #         analysis_config=mm.MOCK_ANALYSIS_CONFIG_RAD_3D,
    #         output_folder="test",
    #     )
    #     mock_analysis.geometry = mm.MOCK_GEOMETRY

    #     res = mock_analysis._get_cell_dimensions()

    #     # From mm.MOCK_GEOMETRY, max of the absolute value of each dimension
    #     # Hardcoding these here to check that the logic agrees that these are the answers
    #     max_x = 1
    #     max_y = 14.8
    #     max_z = 1

    #     self.assertEqual(res[0], math.ceil(max_x + CELL_PADDING) * 2)
    #     self.assertEqual(res[1], math.ceil(max_y + CELL_PADDING) * 2)
    #     self.assertEqual(res[2], math.ceil(max_z + CELL_PADDING) * 2)