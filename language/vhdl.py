import sql as sql
import os
from pyparsing import *

vhdlcomment = "--" + restOfLine
identifier = Word(alphas, alphanums+"_")

begin = Literal("begin")
end = Literal("end")
isKeyword = Keyword("is")
ofKeyword = Keyword("of")

word = Word(alphas+"'.")
number = Word(nums+".")
digit = Word(nums)
parenOpen = Suppress("(")
parenClose = Suppress(")")
semicolon = Suppress(";")
comma = Suppress(",")
init = Literal(":=")
colon = Suppress(":")
plus = Literal('+')
minus = Literal('-')
divide = Literal('/')
mult = Literal('*')
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
  range = Group(Literal("natural") + Literal("range") + Literal("<>"))

  ## This is port
  portName = identifier.setResultsName("portName")

  portType = identifier + Optional(parenOpen \
      + ((digit + identifier + digit) \
      | (range) )+ parenClose)
  
  portDirection = identifier
  portList =  Group(portName + ZeroOrMore(comma + portName))
  port =  portList + colon + portDirection + portType 
  ports = port + ZeroOrMore( semicolon + port)
  portExpr = Group(Keyword("port") + parenOpen + ports \
      + parenClose + semicolon)
  
  ## This is generic 
  genericDeclaration = portList + colon + portType \
      + Optional( init + identifier)
  genericExpr = Keyword("generic") + parenOpen + genericDeclaration \
      + parenClose + semicolon
  # This is entity 
  entityBodyExpr = ZeroOrMore(genericExpr) + ZeroOrMore(portExpr)
  entityName = identifier
  entityExpr = Keyword("entity") + entityName + Keyword("is") \
      + entityBodyExpr + Keyword("end") \
      + Optional(Keyword("entity")) + Optional(identifier) \
      + semicolon  
  
  # This is architecture 
  archName = identifier 

  # Declarations in architecture 
  variable_decl = Keyword("variable") + identifier + colon \
      + portType + semicolon
  type_decl = Keyword("type") + identifier + isKeyword \
      + portType + ofKeyword + portType + semicolon
  archDecls = OneOrMore(type_decl | variable_decl )

  archStatements = "lala"
  archBodyExpr = archDecls + begin + archStatements \
      + end + Optional(archName) + semicolon 
  architectureExpr = Keyword("architecture") + archName + Keyword("of") \
      + entityName + Literal("is") + archBodyExpr \
      + Keyword("end") + Optional(Keyword("architecture")) \
      + Optional(archName) + semicolon 

  # Full design 

  # What we want to ignore
  entityExpr.ignore(genericExpr)
  designExpr = OneOrMore( entityExpr + architectureExpr )
  designExpr.ignore(vhdlcomment)

  archDecls.validate()
  for i in archDecls.searchString(txt) :
    print i
    


