import re
import pprint

pp = pprint.PrettyPrinter(indent=2)
design = []

def parseTxt(txt) :
  #entity_name = '\w+'
  #generic_decl = '(\s*\w+\s*(\s*\:\s*\w+\s*\:\=\s*\w+\s*)?)'
  #generic_list = '({0}[,])*{0}'.format(generic_decl)
  #generic = '(generic\s*\(\s*{0}\s*\);)*'.format(generic_list)
  #port_name = '\w+'
  #port_list = '({0}\s*\,\s*)*{0}'.format(port_name)
  #port_decl = '{0}\:\s*\w+\s+\w+\s*(\([^;]*\))?(;)?'.format(port_list)

  ##ports = 'port\s*\(.*\)\s*;'
  #ports = 'port\s*\({0}+\)\s*;'.format(port_decl)
  #entity_body = '(?P<generic>{0})*\s*(?P<ports>{1})?'.format(generic, ports)
  #pattern = r'''entity\s+(?P<name>{0}\s*)is\s+{1}\s+end\s+entity(\s+\w+)?\s*;'''.format(
  #    entity_name
  #    , entity_body
  #)
  pattern = r'entity\s+(?P<name>\w+)\s+is\s*(?P<body>.*)end\s+entity(\s+\w+)?\s*;'
  entity = re.compile(pattern, re.IGNORECASE | re.DOTALL);
  m = entity.finditer(txt)
  for i in m :
    match = i.groupdict()
    design.append(match)
    

def getDesign(files) :
  for file in files :
    with open(file, "r") as f :
      print("Parsing file {0}".format(file))
      txt = ""
      for line in f :
        if(line.strip()[0:2] == "--") : pass 
        else : 
          txt += line
      parseTxt(txt)
