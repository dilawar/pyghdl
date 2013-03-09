import ply.lex as lex 
from ply.lex import TOKEN
import os

keywords = (
   'USE', "OF",
   'ARCHITECTURE', 'ENTITY', 'COMPONENT', 'PROCESS', 'IS',
   'SIGNAL', 'BEGIN', 'BLOCK', 'FUNCTION',
   'BIT', 
   'PORT', 'IN', 'OUT', 'INOUT', 'GENERIC',
   'TYPE',
   'WAIT', 'ON', 'ASSERT', 'SEVERITY', 'NOTE', 'WARNING'
   'FOR', 'IF', 'CASE', 'ELSE', 'ELSIF', 'THEN', 'WHILE', 'LOOP', 'WHEN',
   'CONSTANT', 'DOWNTO', 'UPTO',
   'END',
  )

keyword_map = {}
for keyword in keywords:
    keyword_map[keyword.lower()] = keyword

tokens = keywords + ( 'NUMBER'
  , 'ID'
  , 'PLUS'
  , 'MINUS'
  , 'TIMES'
  , 'DIVIDE'
  , 'LPAREN'
  , 'EQUAL'
  , 'RPAREN'
  , 'SEMICOLON'
  , 'COMMA'
  , 'DECIMAL'
  , 'COLON'
  , 'GT'
  , 'LT'
  , 'ASSIGN_OP'
  , 'SPECIAL'
  # Grammar rule which we'll parse without caring for details.
  , 'type_decl'
  , 'procedure_definition'
  )   
    

# regular expression rules for simple tokens
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_EQUAL = r'='
t_SEMICOLON = r';'
t_COMMA = r','
t_DECIMAL = r'\.'
t_COLON = r':'
t_GT = r'>'
t_LT = r'<'
t_SPECIAL = r'[\'\"]'
t_ASSIGN_OP = r':='
t_ignore_COMMENT = r'--.*'

# Grammar rules parsed as token.
t_procedure_definition = r'procedure[.\n]+is[.\n]+begin[.\n]+end\s+procedure\s*(\w+\s*)?'
identifier = r'[a-zA-Z_][0-9a-zA-Z_]*'

@TOKEN(identifier)
def t_ID(t) : 
  t.type = keyword_map.get(t.value, "ID")
  return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)    
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex(debug=True) 

import ply.yacc as yacc 

def p_design(p) :
  ''' design : design unit
             | unit
             '''
def p_unit(p) :
  ''' unit : header  
            | entity 
            | architecture  
            '''

def p_header(p) :
  ''' header : USE library SEMICOLON '''

def p_library(p) :
  '''library : library DECIMAL ID 
             | ID DECIMAL ID '''

def p_entity(p) :
  '''entity : ENTITY ID IS entity_body END ENTITY SEMICOLON
            | ENTITY ID IS entity_body END ENTITY ID SEMICOLON
            '''

def p_entity_body(p) :
  '''entity_body : generic_decl ports
                 | ports 
                 '''

def p_generic_decl(p) :
  ''' generic_decl : GENERIC LPAREN generic_stmts RPAREN SEMICOLON '''

def p_generic_stmts(p) :
  ''' generic_stmts : generic_stmt COMMA generic_stmts  
                    | generic_stmt 
                    '''

def p_generic_stmt(p) :
  ''' generic_stmt : ID 
                   | ID COLON porttype 
                   | ID COLON porttype ASSIGN_OP ID 
                   '''

def p_ports(p) :
  ''' ports : PORT LPAREN portlist RPAREN SEMICOLON '''

def p_portlist(p) :
  ''' portlist : portdecl SEMICOLON portlist
               | portdecl 
               '''

def p_portdecl(p) :
  ''' portdecl : portnames COLON portdir porttype '''

def p_portnames(p) :
  ''' portnames : ID COMMA portnames
                | ID 
                '''

def p_portdir(p) :
  ''' portdir : IN 
              | OUT 
              | INOUT 
              '''

def p_porttype(p) :
  '''porttype : BIT 
              | ID 
              | bit_vector
              '''
def p_bit_vector(p) :
  ''' bit_vector : ID LPAREN NUMBER DOWNTO NUMBER RPAREN 
                 | ID LPAREN NUMBER UPTO NUMBER RPAREN 
                 '''

def p_architecture(p) :
  '''architecture : ARCHITECTURE ID OF ID IS architecture_body END ARCHITECTURE SEMICOLON 
                  | ARCHITECTURE ID OF ID IS architecture_body END ARCHITECTURE ID SEMICOLON
                  '''

def p_architecture_body(p) :
  '''architecture_body : arch_expressions SEMICOLON architecture_body
                       | arch_expressions SEMICOLON '''

def p_arch_expressions(p) :
  ''' arch_expressions : type_decl
                       | procedure_definition
                       | ID '''

def p_error(p) :
  print("Syntax error at token {0}".format(p))

def getDesign(files) :
  for file in files :
    if os.path.isfile(file) :
      print("For file {0}".format(file))
      with open(file, "r") as f :
        txt = f.read()
        parser = yacc.yacc(debug=True)
        parser.parse(txt, lexer=lexer)
    else :
      print("File {} does not exists".format(file))
