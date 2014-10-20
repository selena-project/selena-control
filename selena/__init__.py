# -*- coding: utf-8 -*-
#---------------------------------------------------------------------
#   Copyright (C) 2014 Dimosthenis Pediaditakis.
#   Copyright (C) 2014 Charalampos Rotsos.
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


"""Selena - a Xen-based network emulation framework with high fidelity.

"""

from __future__ import absolute_import

# import os
import sys

# Don't forget to also update ../setup.py when this file changes!
# This check is borrowed from the iPython project: https://github.com/ipython/ipython
v = sys.version_info
if v[:2] < (2, 7) or (v[0] >= 3 and v[:2] < (3, 3)):
    raise ImportError('Selena requires Python version 2.7 or 3.3 or above.')
del v

__title__ = 'selena'
__version__ = '0.1'
__release__ = '1'
__build__ = 0x000001
__author__ = 'Dimosthenis Pediaditakis, Charalampos Rotsos'
__license__ = 'BSD'
__copyright__ = 'Copyright 2014 Dimosthenis Pediaditakis, Charalampos Rotsos'


JSON_CONFIG = 'selenaConfig.json'
JSON_CONFIG_SCHEMA = 'selenaConfigSchema.json'
