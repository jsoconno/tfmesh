import re

def get_semantic_version(version):
    """
    Get a tuple of the semantic version components including major, minor, patch, and pre-release.
    """
    regex_pattern = r'([0-9]+)\.([0-9]+)\.([0-9]+)(?:-[A-Za-z-]+([0-9]+))?'

    try:
        version = re.findall(regex_pattern, version, re.MULTILINE)[0]
        version = tuple([int(x) for x in version if x != ''])
    except:
        version = None

    return version

print(get_semantic_version('v1.0.0-pre1'))