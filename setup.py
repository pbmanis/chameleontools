from setuptools import setup, find_packages
import os

# Use Semantic Versioning, http://semver.org/
version_info = (0, 1, 9, '')
__version__ = '%d.%d.%d%s' % version_info


setup(name='chameleontools',
      version=__version__,
      description='Tools for monitoring the Chameleon Vision II laser',
      url='http://github.com/pbmanis/chameleontools',
      author='Paul B. Manis',
      author_email='pmanis@med.unc.edu',
      license='MIT',
      packages=find_packages(include=['chameleontools*']),
      zip_safe=False,
      entry_points={
          'console_scripts': [
               'chameleon=src.ChameleonQuery2:main',
          ]
      },
      classifiers = [
             "Programming Language :: Python :: 2.7+",
             "Development Status ::  Beta",
             "Environment :: Console",
             "Intended Audience :: Neuroscientists",
             "License :: MIT",
             "Operating System :: OS Independent",
             "Topic :: Scientific Software :: Tools :: Python Modules",
             "Topic :: Equipment :: Multiphoton :: Neuroscience",
             ],
    )
      