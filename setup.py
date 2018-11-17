import os
import sys
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

        # the next 3 lines are a workaround for the fact that on Ubuntu 18.04
        # sys.prefix doesn't match the path where setuptools puts data_files,
        # in opposition to what is said here:
        # https://github.com/pypa/sampleproject/blob/master/setup.py#L168
        data_prefix = sys.prefix
        if data_prefix == '/usr':
            data_prefix = '/usr/local'

        subprocess.check_call("make CURDIR={}".format(data_prefix), shell=True)
        subprocess.check_call("cp -r bin build/lib/", shell=True)


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
      version="0.20",
      description='SRTM4 elevation data reader',
      long_description=readme(),
      url='https://github.com/cmla/srtm4',
      author='Carlo de Franchis, Enric Meinhardt, Gabriele Facciolo',
      author_email='carlo.de-franchis@ens-cachan.fr',
      py_modules=['srtm4'],
      install_requires=requirements,
      cmdclass={'develop': CustomDevelop,
                'build_py': CustomBuildPy}
      # the first item of the tuple below has to be "data" to match the path
      # hardcoded in the Makefile
      data_files=[('data', ['data/egm96-15.pgm'])],
      include_package_data=True,
      zip_safe=False)
