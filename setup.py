from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="openvario-compman",
    version="0.4",
    description="Competition Manager for OpenVario",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kedder/openvario-compman",
    author="Andrey Lebedev",
    author_email="andrey.lebedev@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="openvario tui competition igc xcsoar",
    package_dir={"": "src"},
    packages=find_packages(where="src"),  # Required
    python_requires=">=3.7, <4",
    install_requires=["urwid", "aiohttp", "lxml", "openvario-shell"],
    extras_require={
        "dev": ["black", "mypy"],
        "test": ["pytest", "pytest-coverage", "pytest-asyncio", "pytest-mock"],
    },
    package_data={},
    data_files=[],
    entry_points={
        "console_scripts": ["compman=compman.main:main"],
        "ovshell.extensions": ["compman=compman.ovshell:extension"],
    },
    project_urls={},
)
