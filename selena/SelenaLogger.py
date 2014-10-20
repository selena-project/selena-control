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


"""
Selena logging module
=====================
The is the main logging module of Selena which is imported from other
places to enerate logging informaiton of various levels.
"""

import logging
from logging import Logger
from Singleton import Singleton

DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

class SelenaLogger(Logger, object):
    """
    This is the main Selena logger Class
    """
    __metaclass__ = Singleton

    def __init__(self):
        """Selena logger constructor

        Creates the main instance of the Selena logging module.
        """
        Logger.__init__(self, "selena")

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(DEFAULT_LOG_LEVEL)

        # create formatter
        formatter = logging.Formatter(DEFAULT_LOG_FORMAT)

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        self.addHandler(ch)

        # set the logger level
        self.setLevel(DEFAULT_LOG_LEVEL)

    def setAllLevels(self, pLevel):
        """
        Sets the logging level for the logger itself and for all its handlers.

        :param pLevel: The request logging level
        """
        # Set the level for all handlers
        for handler in self.handlers:
            handler.setLevel(pLevel)
        # Set the level for the logger
        self.setLevel(pLevel)



slog = SelenaLogger()

S_DEBUG, S_INFO, S_WARN, S_ERROR, S_CRIT = [slog.debug, slog.info, slog.warning, slog.error, slog.critical]
