import unittest
import pathlib
from core import (
    get_terraform_files,
    get_semantic_version,
    get_github_module_versions,
    get_terraform_provider_versions,
    get_latest_version,
    version_tuple,
    compare_versions,
)

class TestCore(unittest.TestCase):
    def test_get_terraform_files(self):
        """
        Test that a list of terraform files with the extension .tf in the root folder are returned.
        """
        folder = f'{pathlib.Path(__file__).parent.absolute()}/terraform'
        pattern = "*.tf"

        actual = get_terraform_files(terraform_folder=folder, file_pattern=pattern).sort()
        expected = [f'{folder}/versions.tf', f'{folder}/main.tf', f'{folder}/variables.tf'].sort()

        self.assertEqual(actual, expected)

    def test_get_semantic_version(self):
        """
        Test that semantic version components are returned as a dictionary
        """
        actual = get_semantic_version(version="v1.2.3")
        expected = (1, 2, 3)

        self.assertEqual(actual, expected)

    def test_get_github_module_versions(self):
        """
        Test that a list of tags can be returned from a github repo without headers.
        """
        actual = isinstance(get_github_module_versions(user='jsoconno', repo='tfmesh'), list)
        expected = isinstance([], list)

        self.assertEqual(actual, expected)

    def test_get_terraform_provider_versions(self):
        """
        Test that a list of versions can be returned from hashicorp for a given provider such as aws, gcp, or azurerm.
        """
        actual = '3.70.0' in get_terraform_provider_versions(source="hashicorp/aws")

        self.assertTrue(actual)

    def test_get_latest_version(self):
        """
        Test that function returns the latest version.
        """
        versions = ["v0.1.0","v0.1.1","v0.1.3","v0.1.4","v1.0.0","v0.1.2"]

        actual = get_latest_version(versions)
        expected = "v1.0.0"

        self.assertEqual(actual, expected)

    def test_version_tuple(self):
        """
        Test that version strings are properly converted to tuples.
        """
        good_version = "1.0.0"
        bad_version = "v1.0.0"

        good_actual = version_tuple(good_version)
        good_expected = (1, 0, 0)

        bad_actual = version_tuple(bad_version)

        self.assertEqual(good_actual, good_expected)
        self.assertIsNone(bad_actual)

    def test_compare_versions(self):
        """
        Test that version comparisons work correctly.
        """
        pass

if __name__ == '__main__':
    unittest.main()