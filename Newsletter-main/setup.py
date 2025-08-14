from typing import List
from setuptools import setup, find_packages

HYPEN_E_DOT = "-e ."


def read_requirements(file_path: str) -> List[str]:
    """
    This function will return the list of requirements.
    """
    requirements = []
    with open(file_path, encoding="utf-8") as file_obj:  # Ensure UTF-8 encoding
        requirements = file_obj.readlines()
        requirements = [
            req.strip() for req in requirements if req.strip()
        ]  # Remove empty lines and strip whitespace

        if HYPEN_E_DOT in requirements:
            requirements.remove(HYPEN_E_DOT)

    return requirements


setup(
    name="Newsletter",
    version="0.0.1",
    author="Trijesh Chodvadiya",
    author_email="trijesh.chodvadiya90@gmail.com",
    packages=find_packages(),
    install_requires=read_requirements("requirements.txt"),
)
