from nltk import download
from setuptools import find_packages, setup
from setuptools.command.install import install


class InstallCommand(install):
    def run(self):
        install.run(self)
        # Download WordNet data during the installation
        download("wordnet")


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="englishidioms",
    version="0.0.2",
    author="Mahmoud Zaghloul",
    description="An efficient Python package for detecting and identifying English idiomatic expressions and phrases within sentences.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    py_modules=["englishidioms"],
    package_dir={"englishidioms": "englishidioms"},
    install_requires=["nltk==3.7"],
    cmdclass={"install": InstallCommand},
)
