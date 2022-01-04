import unittest
import pathlib
from core import get_terraform_file_list, get_semantic_version_components, get_github_tag_list, get_terraform_provider_version_list

class TestCore(unittest.TestCase):
    def test_get_terraform_file_list(self):
        """
        Test that a list of terraform files with the extension .tf in the root folder are returned.
        """
        folder = f'{pathlib.Path(__file__).parent.absolute()}/terraform'
        pattern = "*.tf"

        actual = get_terraform_file_list(terraform_folder=folder, file_pattern=pattern)
        expected = [f'{terraform_folder}/outputs.tf', f'{terraform_folder}/main.tf', f'{terraform_folder}/variables.tf']

        self.assertEqual(actual, expected)

    def test_get_semantic_version_components(self):
        """
        Test that semantic version components are returned as a dictionary
        """
        actual = get_semantic_version_components(version="v1.2.3")
        expected = {'version': '1.2.3', 'major': 1, 'minor': 2, 'patch': 3, 'pre_release': ''}

        self.assertEqual(actual, expected)

    def test_get_github_tag_list(self):
        """
        Test that a list of tags can be returned from a github repo without headers.
        """
        actual = isinstance(get_github_tag_list(user='jsoconno', repo='terrautomate'), list)
        expected = isinstance([], list)

        self.assertEqual(actual, expected)

    def test_get_terraform_provider_version_list(self):
        """
        Test that a list of versions can be returned from hashicorp for a given provider such as aws, gcp, or azurerm.
        """
        actual = isinstance(get_terraform_provider_version_list(provider="aws"), list)
        expected = isinstance([], list)

        self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()