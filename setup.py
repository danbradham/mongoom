try:
    from distutils.core import setup
except ImportError:
    from setuptools import setup
from pymongorm import __version__

with open("Readme.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

package_data = {"": ["LICENSE"]}

setup(
    name="PyMongORM",
    version=__version__,
    description="An Object-Relational Mapping for MongoDB.",
    long_description=readme,
    author="Dan Bradham",
    author_email="danielbradham@gmail.com",
    url="http://www.danbradham.com",
    packages=["pymongorm"],
    package_dir={"pymongorm": "pymongorm"},
    package_data=package_data,
    include_package_data=True,
    license=license,
    zip_safe=False)
