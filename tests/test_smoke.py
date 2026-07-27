def test_dependencies_import():
    import frontmatter  # noqa: F401
    import markdown  # noqa: F401
    import jinja2  # noqa: F401
    import yaml  # noqa: F401


def test_python_version():
    import sys
    assert sys.version_info[:2] >= (3, 11)
