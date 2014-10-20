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


import os
import sys
import threading
import subprocess
import pwd


class CommandTools(object):
    '''
    classdocs
    '''
    
    path = ''
    rootDir = ''
    user = ''
    runningProcesses = []
    lock = None


    def __init__(self, 
                 path=os.environ['PATH'], 
                 rootDir=os.environ['HOME'],
                 user=os.environ['USER']):
        '''
        Constructor
        '''
        self.path = path
        self.rootDir = rootDir
        try:
            userRecord = pwd.getpwnam(user)
        except KeyError, err:
            print 'User could not be found'
            sys.exit(1)
        self.user = user
        self.lock = threading.RLock()
        
        
    def giveExecRights(self, rootDir, mfile, verbose=False):
        fullPath = os.path.join(rootDir, mfile)
        if(not os.path.exists(fullPath) or os.path.isdir(fullPath)):
            return False
        cmd = 'chmod u+x ' + fullPath
        if verbose:
            print cmd
        process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        process.wait()
        status = process.returncode
        if verbose:
            print 'Return status: ' + str(status)
        if status is not 0:
            return False
        return True
    
    
    def checkPathExists(self, rootDir, mfile=''):
        fullPath = os.path.join(rootDir, mfile)
        return os.path.exists(fullPath)
    
    
    def is_exe(self, fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
            
        
    def runScript(self, basedir, script, args='', verbose=False):
        fullPath = os.path.join(basedir, script)
        if ( (not self.checkPathExists(basedir, script)) or (not self.is_exe(fullPath))):
            if verbose:
                print 'File ' + fullPath + " doesn't exist or is not executable" 
            return False  
        status = 0
        output = ''
        origDir = os.getcwd()
        cmd = "./" + script + args 
    
        try:
            os.chdir(basedir)
            process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.lock.acquire()
            self.runningProcesses.append(process)
            self.lock.release() 
            process.wait()
            output = process.communicate()[0]
            status = process.returncode
            self.lock.acquire()
            self.runningProcesses.remove(process)
            self.lock.release()
        except OSError, exc:
            if verbose:
                print 'Unable to run test ' + fullPath
                print exc.strerror
            return (1, '')
        finally:
            os.chdir(origDir)
            
        if status is not 0 and verbose:
            print cmd + ' exited with value ' + str(status)
            
        return (status, output)
    
    def runCommand(self, pCommand):
        if (pCommand is None) or (type(pCommand) != str) or (len(pCommand) < 2):
            print "Bad command: \n" + pCommand + "\n"
            return None
        status = 0
        output = ''
        origDir = os.getcwd()
        try:
            process = subprocess.Popen(pCommand, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            self.lock.acquire()
            self.runningProcesses.append(process)
            self.lock.release()
            if not pCommand.strip().endswith('&'):
                process.wait()
                output = process.communicate()[0]
                status = process.returncode
            self.lock.acquire()
            self.runningProcesses.remove(process)
            self.lock.release()
        except OSError, exc:
            print 'Unable to run command: ' + pCommand
            print exc.strerror
            return None
        finally:
            os.chdir(origDir)
        if status is not 0:
            print 'Command exited with value ' + str(status)
            
        return (status, output)
    
    def stopAllProcesses(self):
        self.lock.acquire()
        for i, val in enumerate(self.runningProcesses):
            self.runningProcesses[i].terminate()
        self.lock.release()  


if __name__ == "__main__":
    print 'hello'
    myC = CommandTools()
    

        
        
