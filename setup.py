import os
import subprocess
from codecs import open
from setuptools import setup
from setuptools.command import develop, build_py


def readme():
    with open('README.md', 'r', 'utf-8') as f:
        return f.read()


class CustomDevelop(develop.develop, object):
    """
    Class needed for "pip install -e ."
    """
    def run(self):
        subprocess.check_call("make", shell=True)
        super(CustomDevelop, self).run()


class CustomBuildPy(build_py.build_py, object):
    """
    Class needed for "pip install srtm4"
    """
    def run(self):
        super(CustomBuildPy, self).run()
        subprocess.check_call("make", shell=True)
        subprocess.check_call("mkdir -p build/lib/", shell=True)
        subprocess.check_call("cp -r bin data build/lib/", shell=True)


requirements = ['filelock',
                'numpy',
                'requests']

extras_require = {'test': ['pytest>=4.6', 'pytest-cov']}

setup(name="srtm4",
      version="1.1.4",
      description='SRTM4 elevation data reader',
      long_description=readme(),
      long_description_content_type='text/markdown',
      url='https://github.com/cmla/srtm4',
      author='Carlo de Franchis, Enric Meinhardt, Gabriele Facciolo',
      author_email='carlo.de-franchis@ens-cachan.fr',
      py_modules=['srtm4'],
      install_requires=requirements,
      extras_require=extras_require,
      cmdclass={'develop': CustomDevelop,
                'build_py': CustomBuildPy},
      include_package_data=True,
      python_requires='>=2.7',
      zip_safe=False)
