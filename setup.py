from setuptools import setup, find_packages
import sys, os

version = '0.0.1'

setup(name='merveilles_io',
      version=version,
      author='Quinlan Pfiffer',
      author_email='qpfiffer@gmail.com',
      license='LICENSE',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'flask',
          'beautifulsoup4',
      ],
      )
