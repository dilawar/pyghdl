#!/usr/bin/env python
import argparse
import os
import sys
import math
import vhdl.vhdl as vhdl
import vhdl.test as test
import debug.debug as debug
import re
import subprocess

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

def findExecutable(prgmToCheck):
    paths = os.environ['PATH'].split(os.pathsep)
    for p in paths:
        pathToCheck = os.path.join(p, prgmToCheck)
        if os.path.isfile(pathToCheck) and os.access(pathToCheck, os.X_OK):
            return pathToCheck
    return None

def findCompiler(language):
    if language == 'vhdl':
        # Try for ghdl
        if not findExecutable("ghdl"):
            if not findExecutable("vsim"):
                debug.printDebug("ERROR"
                        , "Can't find a suitable compiler on your system" +
                        " Use -c switch from command line"
                        )
                sys.exit(0)
            else:
                return findExecutable("vsim")
        else:
            return findExecutable("ghdl")
    else:
        debug.printDebug("ERROR"
                , "Unknown language {}".format(language)
                )
        sys.exit(0)
            

def main():
    # Argument parser.
    description = '''Write testbench for vhdl and run it using ghdl/vsim.'''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--design-directory', '-d', metavar='design_directory'
            , nargs=1
            , action='append'
            , required = True
            , help = 'Top directory containing your VHDL design.'
            )
    parser.add_argument('--language', '-l'
            , metavar = 'language'
            , default = "vhdl"
            , help = 'Which language (supported : vhdl )'
            )
    parser.add_argument('--compiler', '-c'
            , metavar='compiler'
            , required = False
            , help = "Optional: Specify a compiler or I'll try to guess on system"
            )
    parser.add_argument('--top-module', '-t', metavar='top_module'
            , nargs = 1
            , required = False
            , default = None
            , help = 'Optional : Top module in your design.'
            )
    parser.add_argument('--test-vector-file', '-v', metavar='test_vector'
            , required = False
            , default = None
            , help = 'Test vector file which test-bench should use'
            )
    parser.add_argument('--generate-tb', '-r', metavar='auto_test'
            , nargs = 1
            , required = False
            , default = True
            , help = 'Testbench will be generated automatically.'
            )
 
    class Args: pass 
    args = Args()
    parser.parse_args(namespace=args)
    if args.test_vector_file:
        args.test_vector_file = os.path.join(os.getcwd(), args.test_vector_file)
        if not os.path.isfile(args.test_vector_file):
            debug.printDebug("ERROR"
                    , "Test vector file %s not found " % args.test_vector_file 
                    )
            sys.exit(-11)
        else: pass
    if args.language == "vhdl":
        file_regex = ".*\.vhdl?$"
        files = findListings(args.design_directory, regex=file_regex)
        if len(files) < 1 :
            debug.printDebug("WARN"
                 , "No file is found with regex {0} in directories {1}".format( 
                     file_regex
                     , args.design_directory)
                 )
            sys.exit(-10);
        topDir = findTopDir(args.design_directory)
        compiler = args.compiler 
        if not compiler:
            compiler = findCompiler("vhdl")
        vhdlObj = vhdl.VHDL(topDir, compiler)
        vhdlObj.main(files, args)
    else:
        debug.printDebug("INFO",  "Unsupported language : {0}".format(args.language))
        debug.printDebug("DEBUG", "Languge specified {0}".format(args.language))
        raise UserWarning("Unsupported language. {0}".format(args.language))

if __name__ == "__main__":
    main()
