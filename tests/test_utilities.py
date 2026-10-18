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
