import sql as sql
import os
from pyparsing import *

identifier = Word(alphas, alphanums+"_")
begin = Literal("begin")
end = Literal("end")
word = Word(alphas+"'.")
number = Word(nums+".")
parenOpen = Literal("(")
parenClose = Literal(")")
semicolon = Literal(";")
comma = Literal(",")
colon = Literal(":")

plus = Literal('+')
minus = Literal('-')
divide = Literal('/')
mult = Literal('*')
init = Literal(":=")
assign = Literal("<=")

specialChar = oneOf("! @ # $ % ^ & ")
operator  = plus | minus | divide | mult | assign | init 

anyWord = identifier | number | parenClose | parenOpen | semicolon \
    | comma | colon | operator | specialChar

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
  
  ## This is port
  portType = Group(identifier | identifier + parenOpen + OneOrMore(identifier) \
      + parenClose)
  portDirection = Group(identifier)
  port =  Group(identifier + Optional(comma + identifier) + colon \
      + portDirection + portType )
  ports = port + Optional( semicolon + port)
  portExpr = Group(Literal("port") + parenOpen + ports + parenClose + semicolon)
  
  ## This is generic 
  genericDeclaration = identifier + colon + portType \
      + Optional( init + identifier)
  genericExpr = Literal("generic") + parenOpen + genericDeclaration \
      + parenClose + semicolon
  # This is entity 
  entityBodyExpr = ZeroOrMore(genericExpr | portExpr)
  entityName = identifier
  entityExpr = Literal("entity") + entityName + Literal("is") \
      + entityBodyExpr + Literal("end") \
      + Optional(Literal("entity")) + Optional(identifier) \
      + semicolon  
  
  # This is architecture 
  archName = identifier 
  anyStmts = OneOrMore(anyWord)
  archDecls = OneOrMore( anyStmts )
  archStatements = OneOrMore( anyStmts)
  archBodyExpr = archDecls + begin + archStatements \
      + end + Optional(archName) + semicolon 
  architectureExpr = Literal("architecture") + archName + Literal("of") \
      + entityName + Literal("is") + archBodyExpr \
      + Literal("end") + Optional(Literal("architecture")) \
      + Optional(archName) + semicolon 

  for i in architectureExpr.scanString(txt) :
    print i
    


