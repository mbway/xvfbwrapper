#!/usr/bin/env python3


"""distutils setup/install script for xvfbwrapper"""


import os
import setuptools


VERSION = '0.2.10.dev'


this_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_dir, 'README.rst')) as f:
    LONG_DESCRIPTION = '\n' + f.read()


setuptools.setup(
    name='xvfbwrapper',
    version=VERSION,
    py_modules=['xvfbwrapper'],
    author='Corey Goldberg',
    description='Manage headless displays with Xvfb (X virtual framebuffer)',
    long_description=LONG_DESCRIPTION,
    url='https://github.com/cgoldberg/xvfbwrapper',
    download_url='https://pypi.python.org/project/xvfbwrapper',
    keywords='xvfb headless virtual display x11 testing'.split(),
    license='MIT',
    classifiers=[
        'Operating System :: Unix',
        'Operating System :: POSIX :: Linux',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
