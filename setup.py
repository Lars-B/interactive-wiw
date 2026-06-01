from setuptools import setup, find_packages

setup(
    name="spreadvizapp",
    version="1.3.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=open("requirements.txt").read().splitlines(),
)
