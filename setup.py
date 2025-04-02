from setuptools import find_packages, setup

setup(
    name="system_health_checker",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
