import os
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install


def readme():
    with open('README.md') as f:
        return f.read()


class CustomInstall(install):
    """
    Custom handler for the 'install' command.
    """
    def run(self):
        subprocess.check_call("make", shell=True)
        super().run()


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name="srtm4",
      version="1.0",
      description='SRTM4 elevation data reader',
      long_description=readme(),
      author='Carlo de Franchis, Enric Meinhardt, Gabriele Facciolo',
      packages=find_packages(),
      install_requires=requirements,
      cmdclass={'install': CustomInstall},
      zip_safe=False)
