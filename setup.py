from setuptools import setup

__author__ = 'gm'

setup(name='fiduccia_mattheyses',
      version='1.0.0a',
      description='An implementation of the Fiduccia Mattheyses algorithm',
      url='https://github.com/GeoMSK/FiducciaMattheyses',
      author='George Mantakos',
      packages=['FiducciaMattheyses'],
      install_requires=[
          'numpy',
      ],
      zip_safe=False)

