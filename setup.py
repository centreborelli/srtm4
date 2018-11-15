import os
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info


def readme():
    with open('README.md') as f:
        return f.read()


class CustomInstall(install):
    def run(self):
        subprocess.check_call("make", shell=True)
        super().run()


class CustomDevelop(develop):
    def run(self):
        subprocess.check_call("make", shell=True)
        super().run()


class CustomEggInfo(egg_info):
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
      cmdclass={'install': CustomInstall,
                'develop': CustomDevelop,
                'egg_info': CustomEggInfo},
      zip_safe=False)
