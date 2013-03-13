import sql as sql
import os
from pyparsing import *

identifier = Word(alphas, alphanums+"_")
assign = Literal(":=")
word = Word(alphas+"'.")
number = Word(nums+".")
parenOpen = Literal("(")
parenClose = Literal(")")
semicolon = Literal(";")
comma = Literal(",")
colon = Literal(":")

def processFilesAndBuildDb() :
  conn = sql.conn 
  c = conn.cursor()
  query = "SELECT name, path, top_dir FROM files"
  for row in c.execute(query) :
    name, path, topDir = row
    parseFile(name, path, topDir) 


def parseFile(name, path, topDir) :
  ''' Parse files and build elements table. '''
  filepath = path+"/"+name 
  if not os.path.isfile(filepath) :
    print("File {0} does not exists on disk. Path \n : \t {1}".format(
      name, filepath))
    return
  else :
    with open(filepath, "r") as vhdlFile :
      txt = vhdlFile.read()
    
  ## Great, now look out for entities. 
  portType = Group(identifier | identifier + parenOpen + OneOrMore(identifier) \
      + parenClose)
  portDirection = Group(identifier)
  port =  Group(identifier + Optional(comma + identifier) + colon \
      + portDirection + portType )
  ports = port + Optional( semicolon + port)
  portExpr = Group(Literal("port") + parenOpen + ports + parenClose + semicolon)
  genericDeclaration = identifier + colon + portType \
      + Optional( assign + identifier)
  genericExpr = Literal("generic") + parenOpen + genericDeclaration \
      + parenClose + semicolon
  entityBodyExpr = ZeroOrMore(genericExpr | portExpr)
  entityExpr = Literal("entity") + identifier + Literal("is") \
      + entityBodyExpr + Literal("end") \
      + Optional(Literal("entity")) + Optional(identifier) \
      + semicolon  
       
  for i in entityExpr.scanString(txt) :
    print i
    


