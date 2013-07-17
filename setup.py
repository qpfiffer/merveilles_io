from setuptools import setup, find_packages
import sys, os

version = '0.0.1'

setup(name='merveilles_io',
      version=version,
      author='Quinlan Pfiffer',
      author_email='qpfiffer@gmail.com',
      license='LICENSE',
      packages=["merveilles_io"],
      package_dir = {'':'src'},
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'flask',
      ],
      entry_points={
          'console_scripts': [
              'merveilles_io = merveilles_io.main:main_production',
              'merveilles_io_dev = merveilles_io.main:main_debug',
          ]
      },
      )
