from setuptools import setup, find_packages

setup(
   name = "tcod-terminal",
   version = "0.0.1",
   description = "Real terminal support for tcod.",
   author = "Max Whitney",
   author_email = "mwhitney@alumni.sfu.ca",
   package_dir = {'': "src"},
   packages = find_packages(where='src/'),
   install_requires = [
      'numpy~=1.18.4',
      'tcod~=11.12.1'
   ],
   package_data = {
       'tcod_terminal': ["py.typed"]
   },
)
