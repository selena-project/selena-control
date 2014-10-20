#!/usr/bin/env python
# -*- coding: utf-8 -*-

#---------------------------------------------------------------------
#   Copyright (C) 2014 Dimosthenis Pediaditakis
#   Copyright (C) 2014 Charalampos Rotsos
#
#   All rights reserved.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions
#   are met:
#     1. Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.
#     2. Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#   THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
#   ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#   ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
#   FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#   DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
#   OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#   HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#   LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
#   OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
#---------------------------------------------------------------------

from __future__ import print_function
from setuptools import setup, find_packages
from codecs import open  # To use a consistent encoding
from os import path
import sys
import selena

here = path.abspath(path.dirname(__file__))


def read_file(fname):
    with open(path.join(here, fname), encoding='utf-8') as f:
        return f.read()

# This check is also made in selena/__init__, don't forget to update both when
# changing Python version requirements.
# this check is borrowed from the iPython project: https://github.com/ipython/ipython
v = sys.version_info
if v[:2] < (2,7) or (v[0] >= 3 and v[:2] < (3,3)):
    error = "ERROR: IPython requires Python version 2.7 or 3.3 or above."
    print(error, file=sys.stderr)
    sys.exit(1)

scripts = [path.join('bin', filename) for filename in ['selena']]

setup(
    name="Selena",
    version=selena.__version__,
    author=selena.__author__,
    author_email='dimosthenes@gmail.com, h.rotsos@gmail.com',
    description="Selena - a Xen-based network emulation framework with high fidelity.",
    long_description=read_file('DESCRIPTION'),
    license=selena.__license__,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: System :: Emulators"],
    url="http://selena-project.github.io",
    keywords="network xen emulation time-dilation sdn openflow xcp",
    packages=["selena"],
    install_requires=['setuptools', "docutils", "Sphinx", "jsonschema", "rfc3987"],
    #include_package_data=True,
    package_data={'selena': [selena.JSON_CONFIG, selena.JSON_CONFIG_SCHEMA]},
    #scripts=scripts
    #scripts=path.join(here, 'bin/selena') # "bin/selena" #
    #data_files=[('/usr/local/bin', ['bin/expManagerClient.py', 'bin/expManagerServer.py', 'bin/selena'])]
)
