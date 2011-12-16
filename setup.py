#!/usr/bin/env python

from distutils.core import setup

setup(name='seqlabd',
      version='0.1',
      description='Clinical Sequencing Lab Daemon',
      author='Frederick J. Ross',
      author_email='fredross@uw.edu',
      url='',
      packages=[],
      install_requires=['pydaemonize','pyinotify'],
     )
