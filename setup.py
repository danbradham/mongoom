try:
    from distutils.core import setup
except ImportError:
    from setuptools import setup
from mongoom import __version__

with open("Readme.rst") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

package_data = {"": ["LICENSE"]}

setup(
    name="Mongoom",
    version=__version__,
    description="An Object-Mapper for MongoDB.",
    long_description=readme,
    author="Dan Bradham",
    author_email="danielbradham@gmail.com",
    url="http://www.danbradham.com",
    packages=["mongoom"],
    package_dir={"mongoom": "mongoom"},
    package_data=package_data,
    include_package_data=True,
    license=license,
    zip_safe=False)
