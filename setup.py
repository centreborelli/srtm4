import os
import sys
import site
import subprocess
from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.build_py import build_py


def readme():
    with open('README.md') as f:
        return f.read()


class CustomDevelop(develop):  # needed for "pip install -e ."
    def run(self):
        subprocess.check_call("make", shell=True)
        super().run()


class CustomBuildPy(build_py):  # needed for "pip install srtm4"
    def run(self):
        super().run()
        subprocess.check_call("make", shell=True)
        subprocess.check_call("cp -r bin data build/lib/", shell=True)


#class CustomInstall(install):
#    def run(self):
#        super().run()
#
#class CustomEggInfo(egg_info):
#    def run(self):
#        super().run()


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name="srtm4",
      version="1.0a2",
      description='SRTM4 elevation data reader',
      long_description=readme(),
      url='https://github.com/cmla/srtm4',
      author='Carlo de Franchis, Enric Meinhardt, Gabriele Facciolo',
      author_email='carlo.de-franchis@ens-cachan.fr',
      py_modules=['srtm4'],
      install_requires=requirements,
      cmdclass={'develop': CustomDevelop,
                'build_py': CustomBuildPy},
      include_package_data=True,
      python_requires='>=3',
      zip_safe=False)
