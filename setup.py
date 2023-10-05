from setuptools import setup, find_packages

setup(
    name = "tcod-ansi-terminal",
    version = "0.0.1",
    description = "ANSI terminal support for Python TCOD.",
    author = "Max Whitney",
    author_email = "mwhitney@alumni.sfu.ca",
    python_requires='>=3.7',
    package_dir = {'': "src"},
    packages = find_packages(where='src/'),
    install_requires = [
        'numpy', # just needs to match tcod
        'tcod~=16.1',
        'typing-extensions~=4.7; python_version < "3.8"'
    ],
    package_data = {
        'tcod_ansi_terminal': ["py.typed"]
    },
)
