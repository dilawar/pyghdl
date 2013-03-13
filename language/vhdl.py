import sql as sql
import os
from pyparsing import *

vhdlcomment = "--" + restOfLine
identifier = Word(alphas, alphanums+"_")
begin = Literal("begin")
end = Literal("end")
word = Word(alphas+"'.")
number = Word(nums+".")
digit = Word(nums)
parenOpen = Suppress("(")
parenClose = Suppress(")")
semicolon = Suppress(";")
comma = Suppress(",")
colon = Suppress(":")

plus = Literal('+')
minus = Literal('-')
divide = Literal('/')
mult = Literal('*')
init = Literal(":=")
assign = Literal("<=")
  
#sigType = Keyword("bit_vector") | Literal("std_logic_vector") \
#    | Keyword("integer") \
#    | Keyword("boolean") | Literal("bit") | Literal("std_logic")
#
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
  print("Parsing : \n {0}".format(filepath))
  if not os.path.isfile(filepath) :
    print("File {0} does not exists on disk. Path \n : \t {1}".format(
      name, filepath))
    return
  else :
    txt = ""
    with open(filepath, "r") as vhdlFile :
      txt = vhdlFile.read()
          
  ## Types 
  ## This is port
  portName = identifier.setResultsName("portName")

  portType = identifier + Optional(parenOpen + digit + identifier \
      + digit + parenClose)
  
  portDirection = identifier
  portList =  portName + ZeroOrMore(comma + portName) 
  port =  portList + colon + portDirection + portType 
  ports = port + ZeroOrMore( semicolon + port)
  portExpr = Group(Keyword("port") + parenOpen + ports \
      + parenClose + semicolon)
  
  ## This is generic 
  genericDeclaration = identifier + colon + portType \
      + Optional( init + identifier)
  genericExpr = Keyword("generic") + parenOpen + genericDeclaration \
      + parenClose + semicolon
  # This is entity 
  entityBodyExpr = Optional(genericExpr) + ZeroOrMore(portExpr)
  entityName = identifier
  entityExpr = Keyword("entity") + entityName + Keyword("is") \
      + entityBodyExpr + Keyword("end") \
      + Optional(Keyword("entity")) + Optional(identifier) \
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

  # Full design 
  designExpr = OneOrMore( entityExpr + architectureExpr )
  designExpr.ignore(vhdlcomment)

  for i in entityExpr.searchString(txt) :
    print i
    


