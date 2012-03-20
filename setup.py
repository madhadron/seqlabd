#!/usr/bin/env python

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy

setup(name='seqlabd',
      version='0.1',
      description='Clinical Sequencing Lab Daemon',
      author='Frederick J. Ross',
      author_email='fredross@uw.edu',
      url='',
      packages=['seqlab', 'seqlab.subcommands', 'seqlab.daemons'],
      install_requires=['pydaemonize','pyinotify'],
      cmdclass = {'build_ext': build_ext},
      ext_modules = [Extension("seqlab.ab1", ["seqlab/ab1.pyx"])],
      include_dirs = [numpy.get_include(),],
      scripts=['bin/sequencereportd', 'bin/dailysummaryd',
               'bin/seqlab']
     )
