#!/usr/bin/env python2.7
import argparse
import os
import sys
import math
import language.vhdl as vhdl
import sql

def findListings(dirs, topDir, regex=None) :
  listings = set()
  i = 0
  for dir in dirs :
    dir = dir[i]
    i += 1
    for root, subdirPath, fileList in os.walk(dir) :
      for fname in fileList :
        fileFullPath = os.path.join(root, fname)
        query = '''INSERT INTO files 
          (name_regex, name, path, top_dir)
          VALUES (?, ?, ?, ?)'''
        c = sql.conn.cursor()
        if not regex :
          c.execute(query, ('.*', fname, root, topDir,))
          listings.add(fileFullPath)
        else :
          import re
          if re.match(regex, fname) :
            c.execute(query, (regex, fname, root, topDir,))
            listings.add(fileFullPath)
          else : pass

  sql.conn.commit()
  return frozenset(listings)
  

def findTopDir(dirs) :
  ''' Return the top-most directory in a given list of directories '''
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
  parser.add_argument('-l', metavar='language', nargs=1
      , required = True
      , help = 'Which languag (supported : vhdl )')
  parser.add_argument('-t', metavar='top_module', nargs=1
      , dest = 'topModule'
      , required = False
      , help = 'Optional : Top module in your design.'
      )

  class Args: pass 
  args = Args()
  parser.parse_args(namespace=args)
  
  if args.l[0] == "vhdl" :
    #mc.initCurses()
    file_regex = ".*\.vhd$"
    
    topDir = findTopDir(args.d)
    sql.initDB("vhdl", topDir)
    
    files = findListings(args.d, topDir, regex=file_regex)
    if len(files) < 1 :
      print("No file is found with regex {0} in directories"
        +" {1}".format(regex, args.d))
      sys.exit();
    #vhdl.processTheFiles(topDir, files)
    vhdl.processFilesAndBuildDb()
  else :
    #mc.initCurses()
    msg = "Unsupported language : {0}".format(args.l)
    #mc.writeOnWindow(mc.msgWindow, msg)
    print(msg)
  # close the db when done
  sql.closeDB()
