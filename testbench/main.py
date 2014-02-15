#!/usr/bin/env python2.7
import argparse
import os
import sys
import math
import vhdl.vhdl as vhdl
import vhdl.test as test
import debug.debug as debug
import re

def findListings(dirs, regex=None) :
   listings = set()
   i = 0
   for dir in dirs :
       dir = dir[i]
       i += 1
       for root, subdirPath, fileList in os.walk(dir) :
           for fname in fileList :
               fileFullPath = os.path.join(root, fname)
               listings.add(fileFullPath)
   if not regex :
       return frozenset(listings)
   else :
       return frozenset(filter(lambda x : re.match(regex, x), listings))

def findTopDir(dirs) :
  dList = list()
  for dir in dirs :
    for d in dir :
      if os.path.isdir(d) :
        dList.append(d)
  return min(dList, key=len)

def main():
   # Argument parser.
   description = '''Write testbench for vhdl and run it using ghdl/vsim.'''
   parser = argparse.ArgumentParser(description=description)
   parser.add_argument('-d', metavar='design_directory', nargs=1
           , action='append'
           , required = True
           , help = 'Top directory containing your VHDL design.'
           )
   parser.add_argument('-l', metavar='language', nargs=1
           , default = "vhdl"
           , help = 'Which language (supported : vhdl )'
           )
   parser.add_argument('-t', metavar='top_module', nargs=1
           , required = False, default=None
           , help = 'Optional : Top module in your design.'
           )
   parser.add_argument('-r', metavar='auto_test', nargs=1
           , required = False
           , default=True
           , help = 'Optional : If specified testbenches will be generated \
                   automatically.'
            )
 
   class Args: pass 
   args = Args()
   parser.parse_args(namespace=args)
   if args.l == "vhdl" :
       file_regex = ".*\.vhdl?$"
       files = findListings(args.d, regex=file_regex)
       if len(files) < 1 :
           debug.printDebug("WARN", "No file is found with regex \
                   {0} in directories {1}".format( file_regex, args.d))
           sys.exit();
       topDir = findTopDir(args.d)
       vhdlObj = vhdl.VHDL(topDir)
       vhdlObj.execute(files, top=args.t, generateTB=args.r)
   else:
       debug.printDebug("INFO",  "Unsupported language : {0}".format(args.l))
       debug.printDebug("DEBUG", "Languge specified {0}".format(args.l))
       raise UserWarning, "Unsupported language. {0}".format(args.l)

if __name__ == "__main__":
    main()
