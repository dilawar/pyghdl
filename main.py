#!/usr/bin/env python3
import curses
import argparse
import os
import sys
import language.vhdl_regex as vhdl

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
    import re
    return frozenset(filter(lambda x : re.match(regex, x), listings))

def findTopDir(dirs) :
  dList = list()
  for dir in dirs :
    for d in dir :
      if os.path.isdir(d) :
        dList.append(d)
  return min(dList, key=len)

if __name__=="__main__" :
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

  class Args: pass 
  args = Args()
  parser.parse_args(namespace=args)
  files = findListings(args.d, regex=".*\/mux\.vhd$")
  if len(files) < 1 :
    print("No file is found with regex {0} in directories"
        +" {1}".format(regex,args.d))
    sys.exit();
  else :
    topDir = findTopDir(args.d)
    vhdl.processTheFiles(topDir, files)

