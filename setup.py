from setuptools import find_packages, setup
import os

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='databoxlib',
    packages=find_packages(include=['databoxlib']),
    version='0.1.1',
    description='Python library to interact with databox',
    author='DataEngineeringUnisoma',
    license='MIT',
    install_requires=['pyreadr'],
    setup_requires=[],
    tests_require=[],
    test_suite='tests',
    long_description=read('README.md'),

)