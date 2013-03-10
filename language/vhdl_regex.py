import sys
import re
import pprint
import os
import errno
import subprocess

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

    self.allcomponents = list()

    self.topmodule = None

  def designPrint(self) :
    for i in self.allcomponents :
      print("Component : {0} ".format(i))
    for i in self.entities :
      entity = i
      print("Entity : {}".format(i))
      print(" Body : {0}".format(self.entity_bodies[i]))

  def findTopModule(self) :
    noOfTopModules = 0
    for en in self.entities :
      if en in self.allcomponents : pass
      else :
        noOfTopModules += 1
        self.topmodule = en

    if noOfTopModules != 1 :
      print("Not a single topmodule found.")
      sys.exit(0)
    else :
      print("Found a top module.")

design = Design()

def parseTxt(txt) :
  '''
  Parse the given 'txt'. Construct a design object which has topmodule.
  If this topmodule is not a test bench then write one. Compile and simulate.
  '''
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
    component_pat = r'\s*component\s+(?P<comp_name>\w+)(((?!component).)*)\s*end\s+component'
    mm = re.findall(component_pat, arch_body, re.IGNORECASE | re.DOTALL)
    components = []
    for ii in mm :
      components.append(ii[0])
    design.components[arch_name] = components
    design.allcomponents += components
  

def getDesign(files) :
  ''' Process all files to get the heirarchy of design.
  '''
  for file in files :
    with open(file, "r") as f :
      print("Parsing file {0}".format(file))
      txt = ""
      for line in f :
        if(line.strip()[0:2] == "--") : pass 
        else : 
          txt += line
      parseTxt(txt)
  design.findTopModule()

## Compile and run the design.
def compileAndRun(files, topmodule) :
  command_string = "ghdl {0} --std=93 --workdir={1} --work=work --ieee=synopsys "
  topentity = design.topmodule
  for file in files :
    filename = os.path.basename(file)
    dirpath = os.path.dirname(file)
    # create the work dir.
    workdir = dirpath+"/work"
    try :
      os.makedirs(workdir)
    except OSError as exception :
      if exception.errno != errno.EEXIST :
        raise
    command = command_string.format( '-a', workdir)
    subprocess.check_call(("{0} {1}".format(command, file)), shell=True)
    print("|- Compilation successful : {0}".format(file))
  
  print("Elaborating : {0}".format(topentity))
  command = command_string.format('-e', workdir)
  binpath = dirpath+"/"+topentity
  subprocess.check_call(("{0} -o {2} {1}".format(
     command
    ,topentity
    , binpath
    )), shell=True)
  command = '{0} --vcd={1} --stop-time=1ms'.format(binpath
      , dirpath+"/"+topentity+".vcd")
  subprocess.check_call(command, shell=True)

def processTheFiles(files) :
  print("Processing all files.")
  getDesign(files)
  topmodule = design.topmodule
  # get the port information out of topmodule.
  topentity = design.entity_bodies[topmodule]
  port_regex = r'port\s*\(.*\)\s*;'
  m = re.search(port_regex, topentity, re.IGNORECASE | re.DOTALL)
  if not m :
    print("No port specified in this entity. Looks like it is testbench.")
    print("-- Compile and run it.")
    compileAndRun(files, topmodule)
  else :
    print("Write a test-bench.")
