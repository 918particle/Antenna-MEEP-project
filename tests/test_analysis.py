import math
import unittest
from pathlib import Path
from unittest.mock import MagicMock, PropertyMock, patch

from parameterized import parameterized

import models as mds
import tests.mock_models as mm
from analysis import CELL_PADDING
from rad_pattern_analysis import RadPatternAnalysis
from vswr_analysis import VSWRAnalysis


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

        res = mock_analysis._get_cell_dimensions()

        # From mm.MOCK_GEOMETRY, max of the absolute value of each dimension
        # Hardcoding these here to check that the logic agrees that these are the answers
        max_x = 1
        max_y = 14.8
        max_z = 1

        self.assertEqual(res[0], math.ceil(max_x + CELL_PADDING) * 2)
        self.assertEqual(res[1], math.ceil(max_y + CELL_PADDING) * 2)
        self.assertEqual(res[2], math.ceil(max_z + CELL_PADDING) * 2)

    def test_set_up_output_directory(self):
        output_folder = "test_mock_output_folder"
        mock_analysis = RadPatternAnalysis(
            analysis_config=mm.MOCK_ANALYSIS_CONFIG_RAD_3D,
            output_folder=output_folder,
        )
        mock_analysis._set_up_output_directory(output_folder=output_folder)

        self.assertIsInstance(mock_analysis.output_folder, Path)
        self.assertTrue(mock_analysis.output_folder.is_dir())
        mock_analysis.output_folder.rmdir()

    def test_get_centering_adjustment(self):
        mock_analysis = RadPatternAnalysis(
            analysis_config=mm.MOCK_ANALYSIS_CONFIG_RAD_3D,
            output_folder="test",
        )
        mock_analysis.geometry = mm.MOCK_GEOMETRY

        mock_analysis._get_centering_adjustment()

        # From mm.MOCK_GEOMETRY, max of the absolute value of each dimension
        # Hardcoding these here to check that the logic agrees that these are the answers
        max_x = 1
        min_x = -1
        max_y = 14
        min_y = -14.8

        center_x = (max_x + min_x) / 2
        center_y = (max_y + min_y) / 2

        self.assertEqual(mock_analysis.x_centering_adjustment, 0 - center_x)
        self.assertEqual(mock_analysis.y_centering_adjustment, 0 - center_y)

    @parameterized.expand(
        [
            (
                "rad_pattern",
                RadPatternAnalysis(
                    analysis_config=mm.MOCK_ANALYSIS_CONFIG_RAD_2D,
                    output_folder="test",
                ),
                5,
            ),
            (
                "vswr",
                VSWRAnalysis(
                    analysis_config=mm.MOCK_ANALYSIS_CONFIG_VSWR_2D,
                    output_folder="test",
                ),
                1,
            ),
        ]
    )
    @patch("antenna.Antenna.set_geometry")
    def test_create_antennas(
        self,
        name: str,
        mock_analysis: RadPatternAnalysis | VSWRAnalysis,
        expected_num_antenna: int,
        mock_set_geometry,
    ):
        mock_analysis.geometry = mm.MOCK_GEOMETRY
        mock_analysis.analysis_type_config.num_antenna = 5
        mock_analysis.analysis_type_config.x_offset = 2
        mock_analysis.analysis_type_config.y_offset = 3

        # Don't want to actually run the set_geometry function here because we will test its functionality elsewhere
        mock_set_geometry.return_value = None
        mock_antenna = MagicMock()
        mock_antenna.geometry = mm.MOCK_GEOMETRY

        with patch.dict(
            "analysis.ANTENNA_CLASSES",
            {mds.AntennaType.RF_HORN: MagicMock(return_value=mock_antenna)},
        ):
            mock_analysis._create_antennas()

        # Testing that the geometery is set correctly
        self.assertEqual(
            mock_analysis.geometry, mm.MOCK_GEOMETRY * expected_num_antenna
        )

        # Testing that each call to set geometery appropriately increments the offset from the origin
        # Needs to be a seperate check since we mock out the results of set_geometry to always be the same
        called_x_offsets = [
            mock_antenna.set_geometry.call_args_list[i].kwargs["x_offset"]
            for i in range(expected_num_antenna)
        ]
        called_y_offsets = [
            mock_antenna.set_geometry.call_args_list[i].kwargs["y_offset"]
            for i in range(expected_num_antenna)
        ]

        expected_x_offsets = [i * 2 for i in range(expected_num_antenna)]
        expected_y_offsets = [i * 3 for i in range(expected_num_antenna)]

        self.assertEqual(called_x_offsets, expected_x_offsets)
        self.assertEqual(called_y_offsets, expected_y_offsets)
