import unittest
from pathlib import Path

import tests.mock_models as mm
import utilities as u


class TestUtilities(unittest.TestCase):
    def test_resolve_output_folder_includes_dir(self):
        """Tests resolve_output_folder() when output_folder includes the results directory
        """

        output_folder = "results/test1"

        res = u.resolve_output_folder(output_folder=output_folder)

        self.assertIsInstance(res, Path)
        expected_path = (Path(__name__).parent / "results").resolve() / "test1"
        self.assertEqual(res, expected_path)
