#!/usr/bin/env python 
import curses
import argparse
import os

def findListings(dirs, regex=None) :
  listings = set()
  for dir in dirs :
    dir = dir.pop()
    for dirPath, subdirPath, fileList in os.walk(dir) :
      for fname in fileList :
        fileFullPath = os.path.join(dir, fname)
        listings.add(fileFullPath)
  if not regex :
    return listings
  else :
    import re
    return set(filter(lambda x : re.match(regex, x), listings))


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

  class Args:
    pass 
  args = Args()
  parser.parse_args(namespace=args)
  files = findListings(args.d, regex=".*py$")
  print(files)

