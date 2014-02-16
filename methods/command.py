#!/usr/bin/env python

"""command.py: Run a command in python.

Last modified: Sat Jan 18, 2014  05:01PM

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2013, NCBS Bangalore"
__credits__          = ["NCBS Bangalore", "Bhalla Lab"]
__license__          = "GPL"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@iitb.ac.in"
__status__           = "Development"


import subprocess 
import shlex
import debug.debug as debug
import sys

def runCommand(command, shell=False, **kwargs):
    if type(command) is list:
        pass
    else:
        command = shlex.split(command)
    try:
        p = subprocess.Popen(command
                , stdin = kwargs.get('stdin', subprocess.PIPE)
                , stdout = kwargs.get('stdout', subprocess.PIPE)
                , stderr = kwargs.get('stderr', subprocess.PIPE)
                )
        p.wait()
    except Exception as e:
        debug.printDebug("ERROR", "Failed with exception %s " % e)
        debug.printDebug("DEBUG", "Command was:  {}".format(command))
        sys.exit(0)


