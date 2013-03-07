#!/usr/bin/env python 
import curses
import argparse


# Argument parser.
description = '''Python front-end of ghdl written for personal convenience.'''
parser = argparse.ArgumentParser(description=description)
parser.add_argument('-d', metavar='design_directory', nargs=1
    , action='append'
    , required = True
    , help = 'Location of directory where your VHDL design.')
parser.add_argument('-t', metavar='top_module', nargs=1
    , dest = 'topModule'
    , required = False
    , help = 'Optional : Top module in your design.'
    )

args = parser.parse_args()

