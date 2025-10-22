from setuptools import setup, find_packages

setup(
    name="unified-theming",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0",
    ],
    python_requires=">=3.10",
)
