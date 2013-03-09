#!/usr/bin/env python 
import curses
import argparse
import os
import language.vhdl_regex as vhdl

def findListings(dirs, regex=None) :
  listings = set()
  for dir in dirs :
    dir = dir.pop()
    for root, subdirPath, fileList in os.walk(dir) :
      for fname in fileList :
        fileFullPath = os.path.join(root, fname)
        listings.add(fileFullPath)
  if not regex :
    return frozenset(listings)
  else :
    import re
    return frozenset(filter(lambda x : re.match(regex, x), listings))


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
  files = findListings(args.d, regex=".*mux.*vhd$")
  if len(files) < 1 :
    print("No file is found with regex {0} in directories"
        +" {1}".format(regex,args.d))
    sys.exit();
  else :
    design = vhdl.getDesign(files)
  print(design)

