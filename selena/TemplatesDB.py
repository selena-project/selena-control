# -*- coding: utf-8 -*-
#---------------------------------------------------------------------
#   Copyright (C) 2014 Dimosthenis Pediaditakis.
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

from Singleton import Singleton
from selena.SelenaLogger import slog, LOG_LEVELS, S_DEBUG, S_INFO, S_WARN, S_ERROR, S_INFO, S_CRIT

"""
TemplatesDB module
==================
A single instance of the database that holds the information for VM templates.
"""

class TemplatesDB(object):
    """
    The TemplatesDB Class is used to hold the set of available VM templates.
    """
    __metaclass__ = Singleton

    DB = {}

    def __init__(self, configuration=[]):
        """
        Initializes the database of VM templates using a configuration dictionary.

        :param configuration: The dictionary with the template definitions
        """
        if configuration:
            self.addTemplatesFromConfig(configuration)

    def addTemplatesFromConfig(self, configuration=[]):
        for tplDict in configuration:
            id = str(tplDict['Name'])
            S_DEBUG("Importing Vm template %s:\n%s\n", id, str(tplDict))
            tplDict.pop('Name', None)
            TemplatesDB.DB[id] = tplDict.copy()


templatesI = TemplatesDB()
templatesDB = TemplatesDB.DB
importTemplates = templatesI.addTemplatesFromConfig
