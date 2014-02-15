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

def runCommand(command, shell=False, **kwargs):
    try:
        p = subprocess.Popen(command
                , stdin = kwargs.get('stdin', subprocess.PIPE)
                , stdout = kwargs.get('stdout', subprocess.PIPE)
                , stderr = kwargs.get('stderr', subprocess.PIPE)
                )
    except Exception as e:
        print("Failed with exception %s " % e)
        print("Command was \n %s " % " ".join(command))


