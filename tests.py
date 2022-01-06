import unittest
import pathlib
from core import *

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

    def test_get_latest_version_with_none_type(self):
        """
        Test that function returns the latest version.
        """
        versions = []

        result = get_latest_version(versions)

        self.assertIsNone(result)

    def test_compare_versions(self):
        """
        Test that version comparisons work correctly.
        """
        a = (1, 5, 0)
        b = (1, 5, 10)
        c = (1, 4)
        d = (1,)

        result = (
            compare_versions(a, "=", a) and
            compare_versions(b, "", b) and
            compare_versions(a, "!=", b) and
            compare_versions(a, "<", b) and
            compare_versions(a, "<=", a) and
            compare_versions(b, ">", a) and
            compare_versions(b, "<=", b) and
            compare_versions(b, "~>", a) and
            compare_versions(b, "~>", c)
        )

        self.assertTrue(result)

    def test_compare_versions_with_none_types(self):
        """
        Test that null values passed to compare_versions result in a value of False.
        """
        a = (1, 5, 0)
        b = (1, 5, 10)

        result = (
            compare_versions(a, "=", ()) and
            compare_versions("", "=", b)
        )

        self.assertFalse(result)

    def test_compare_versions_with_invalid_pessimistic_constraint(self):
        """
        Test that null values passed to compare_versions result in a value of False.
        """
        a = (1, 5, 10)
        b = (1,)
        with self.assertRaises(ValueError):
            compare_versions(a, "~>", b)

    def test_get_allowed_versions_no_constraints(self):
        """
        Test passing no constraints.  It should return all available versions.
        """
        available_versions = ["v0.1.0","v0.1.1","v0.1.3","v0.1.4","v1.0.0","v1.1.2","v2.0.0","v2.0.1","v2.1.0"]
        self.assertEqual(get_allowed_versions(available_versions), available_versions)

    def test_get_allowed_versions_lower_constraint_no_operator(self):
        """
        Test passing a lower constraint with no operator.  Should result an equal operator (=).
        """
        available_versions = ["v0.1.0","v0.1.1","v0.1.3","v0.1.4","v1.0.0","v1.1.2","v2.0.0","v2.0.1","v2.1.0"]
        lower_constraint = (0, 1, 3)
        self.assertEqual(get_allowed_versions(available_versions, lower_constraint), ["v0.1.3"])

    def test_get_allowed_versions_one_constraint(self):
        """
        Test passing a lower constraint.
        """
        available_versions = ["v0.1.0","v0.1.1","v0.1.3","v0.1.4","v1.0.0","v1.1.2","v2.0.0","v2.0.1","v2.1.0"]
        lower_constraint = (2, 0, 0)
        lower_constraint_operator = ">"
        self.assertEqual(get_allowed_versions(available_versions, lower_constraint, lower_constraint_operator), ["v2.0.1", "v2.1.0"])

    def test_get_allowed_versions_two_constraints(self):
        """
        Test passing a lower and upper constraint.
        """
        available_versions = ["v0.1.0","v0.1.1","v0.1.3","v0.1.4","v1.0.0","v1.1.2","v2.0.0","v2.0.1","v2.1.0"]
        lower_constraint = (2, 0, 0)
        lower_constraint_operator = ">="
        upper_constraint = (2, 1, 0)
        upper_constraint_operator = "<"
        self.assertEqual(get_allowed_versions(available_versions, lower_constraint, lower_constraint_operator, upper_constraint, upper_constraint_operator), ["v2.0.0", "v2.0.1"])

    def test_color(self):
        self.assertEqual(color("ok_blue"), "\033[94m")

    def test_get_status_up_to_date(self):
        """
        Test that the correct version change status is returned ((*) up-to-date).
        """
        current_version = "1.0.0"
        latest_available_version = "1.0.0"
        latest_allowed_version = "1.0.0"

        status = get_status(current_version, latest_available_version, latest_allowed_version)

        self.assertIn("(*) up-to-date", status)

    def test_get_status_upgraded_to_latest(self):
        """
        Test that the correct version change status is returned ((->) upgraded to latest).
        """
        current_version = "1.0.0"
        latest_available_version = "2.0.0"
        latest_allowed_version = "2.0.0"

        status = get_status(current_version, latest_available_version, latest_allowed_version)

        self.assertIn("(->) upgraded to latest", status)

    def test_get_status_upgraded_to_allowed(self):
        """
        Test that the correct version change status is returned ((>) upgraded to allowed).
        """
        current_version = "1.0.0"
        latest_available_version = "3.0.0"
        latest_allowed_version = "2.0.0"

        status = get_status(current_version, latest_available_version, latest_allowed_version)

        self.assertIn("(>) upgraded to allowed", status)

    def test_get_status_downgraded_to_latest(self):
        """
        Test that the correct version change status is returned ((<-) downgraded to latest).
        """
        current_version = "3.0.0"
        latest_available_version = "2.0.0"
        latest_allowed_version = "2.0.0"

        status = get_status(current_version, latest_available_version, latest_allowed_version)

        self.assertIn("(<-) downgraded to latest", status)

    def test_get_status_downgraded_to_allowed(self):
        """
        Test that the correct version change status is returned ((<) downgraded to allowed).
        """
        current_version = "3.0.0"
        latest_available_version = "2.0.0"
        latest_allowed_version = "1.0.0"

        status = get_status(current_version, latest_available_version, latest_allowed_version)

        self.assertIn("(<) downgraded to allowed", status)

    def test_get_status_pinned(self):
        """
        Test that the correct version change status is returned ((.) version pinned).
        """
        current_version = "1.0.0"
        latest_available_version = "2.0.0"
        latest_allowed_version = "1.0.0"

        status = get_status(current_version, latest_available_version, latest_allowed_version)

        self.assertIn("(.) version pinned", status)

    def test_get_status_no_suitable_version(self):
        """
        Test that the correct version change status is returned ((x) no suitable version).
        """
        current_version = "1.0.0"
        latest_available_version = "1.0.0"
        latest_allowed_version = None

        status = get_status(current_version, latest_available_version, latest_allowed_version)

        self.assertIn("(x) no suitable version", status)


if __name__ == '__main__':
    unittest.main()