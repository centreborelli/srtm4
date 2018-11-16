import os
import subprocess
from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
from setuptools.command.build_py import build_py


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


class CustomBuildPy(build_py):
    def run(self):
        super().run()
        subprocess.check_call("make", shell=True)
        subprocess.check_call("cp -r bin build/lib/", shell=True)


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name="srtm4",
      version="0.15",
      description='SRTM4 elevation data reader',
      long_description=readme(),
      url='https://github.com/cmla/srtm4',
      author='Carlo de Franchis, Enric Meinhardt, Gabriele Facciolo',
      author_email='carlo.de-franchis@ens-cachan.fr',
      py_modules=['srtm4'],
      install_requires=requirements,
      cmdclass={'install': CustomInstall,
                'develop': CustomDevelop,
                'build_py': CustomBuildPy,
                'egg_info': CustomEggInfo},
      zip_safe=False)
