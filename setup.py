try:
    from distutils.core import setup
except ImportError:
    from setuptools import setup
import os
import sys

if sys.argv[-1] == 'cheeseit!':
    os.system('python setup.py sdist upload')
    sys.exit()

with open("README.rst") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="Mongoom",
    version="0.1.1",
    description="An Object-Mapper for MongoDB.",
    long_description=readme,
    author="Dan Bradham",
    author_email="danielbradham@gmail.com",
    url="http://mongoom.readthedocs.org",
    include_package_data=True,
    license=license,
    zip_safe=False,
    package_data={"": ["LICENSE"]},
    packages=["mongoom"],
    package_dir={"mongoom": "mongoom"},
    install_requires = ["pymongo"],
    classifiers=(
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ),
)
