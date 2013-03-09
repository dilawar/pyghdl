import re
import pprint

pp = pprint.PrettyPrinter(indent=2)

class Design :
  def __init__(self) :
    # entity in design
    self.entities = list()
    self.entity_bodies = dict()
    
    # Architecture of an entity
    self.architectures = dict()

    # Component inside architecture
    self.components = dict()

  def designPrint(self) :
    for i in self.components :
      print("Component : {0} {1}".format(i, self.components[i]))
    for i in self.entities :
      entity = i
      print("Entity : {}".format(i))
      print(" Body : {0}".format(self.entity_bodies[i]))

design = Design()

def parseTxt(txt) :
  pattern = r'entity\s+(?P<name>\w+)\s+is\s*(?P<body>.*)end\s*(entity)?\s*(?P=name)?\s*;'
  entity = re.compile(pattern, re.IGNORECASE | re.DOTALL);
  m = entity.finditer(txt)
  for i in m :
    match = i.groupdict()
    design.entities.append(match['name'])
    design.entity_bodies[match['name']] = match['body']

  #architecture_body = '.*(component\s+(?P<component_name>\w+)\s+(.*)end\s+component.*)*.*'
  architecture_body = '(?P<arch_body>.*)'
  pattern = r'architecture\s+(?P<arch_name>\w+)\s+of\s+(?P<arch_of>\w+)\s+is\s+{0}'.format(
      architecture_body)
  architecture = re.compile(pattern, re.IGNORECASE | re.DOTALL);
  m = architecture.finditer(txt)
  for i in m :
    match = i.groupdict()
    arch_name = match['arch_name']
    arch_body = match['arch_body']
    arch_of = match['arch_of']
    del match['arch_body']
    component_pat = r'\s*component\s+(?P<comp_name>\w+)(((?!component).)*)end\s+component\s*;'
    mm = re.findall(component_pat, arch_body, re.IGNORECASE | re.DOTALL)
    components = []
    for ii in mm :
      components.append(ii[0])
    design.components[arch_name] = components
  

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
  design.designPrint()
