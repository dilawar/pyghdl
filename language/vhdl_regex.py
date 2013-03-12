import sys
import re
import pprint
import os
import errno
import subprocess

pp = pprint.PrettyPrinter(indent=2)

testbench = '''
ENTITY testbench IS END;
-------------------------------------------------------------------------------
-- This testbench is automatically generated. May not work.
-- A file called vector.test must be generated in the same directory where
-- this testbench is saved. Each value must be separed by a space. 

-- time [in_port ] [out_port] 
-- They must be in the same order in which they appear in entity.
-------------------------------------------------------------------------------
LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE std.textio.ALL;
USE work.ALL;

ARCHITECTURE arch OF testbench IS 

\t----------------------------------------------------------------
\t-- Component declaration.
\t----------------------------------------------------------------
\tCOMPONENT dut 
\t\t{0}
\tEND COMPONENT;
\t
\t-- Signals in entity
{1}
BEGIN
\t-- Instantiate a dut
{2}
\ttest : PROCESS 
\t\t-- Declare variables to store the values stored in test files.
{3} 
\t\t-- File and its minions.
\t\tFILE vector_file : text IS IN "vector.test";
\t\tVARIABLE l : LINE;
\t\tVARIABLE r : REAL;
\t\tVARIABLE vector_time : TIME;
\t\tVARIABLE space : CHARACTER;
\t\tVARIABLE good_number, good_val : BOOLEAN;
\tBEGIN
\t\tWHILE NOT endfile(vector_file) LOOP 
\t\t\treadline(vector_file, l);
\t\t\t-- Read the time from the begining of the line. Skip the line if it doesn't
\t\t\t-- start with a number.
\t\t\tread(l, r, good => good_number);
\t\t\tNEXT WHEN NOT good_number;
\t\t\t-- Convert real number to time
\t\t\tvector_time := r*1 ns;
\t\t\tIF (now < vector_time) THEN
\t\t\tWAIT FOR vector_time - now;
\t\t\tEND IF;
\t\t\t-- Skip a space
\t\t\tread(l, space);
\t\t\t-- Read other singals etc.
{4}
\t\tEND LOOP;
\t\tASSERT false REPORT "Test complete";
\t\tWAIT;
\tEND PROCESS;
END ARCHITECTURE arch;
-- Testbech ends here.
'''

class Design :
  
  class TopEntity : 
    def  __init__(self) :
      self.name = ''
      self.ports = dict()
  
  def __init__(self) :
    # entity in design
    self.entities = list()
    # Root dir of design.
    self.binpath = None
    self.entity_bodies = dict()
    # Architecture of an entity
    self.architectures = dict()
    # Component inside architecture
    self.components = dict()

    self.allcomponents = list()

    self.topmodule = None
    self.objTopEntity = self.TopEntity()


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


def parseTxt(design, txt) :
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
  

def getDesign(design, files) :
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
      parseTxt(design, txt)
  design.findTopModule()

## Compile and run the design.
def compileAndRun(design, files, topmodule) :
  command_string = "ghdl {0} --std=93 --workdir={1} --work=work --ieee=synopsys "
  topentity = design.objTopEntity.name
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
  bin = dirpath+"/"+topentity
  subprocess.check_call(("{0} -o {2} {1}".format(
     command
    ,topentity
    , bin
    )), shell=True)
  command = '{0} --vcd={1} --stop-time=1ms'.format(bin
      , dirpath+"/"+topentity+".vcd")
  subprocess.check_call(command, shell=True)


def addATestBench(design) :
  ''' Add a test-bench '''
  global testbench
  _topmodule = design.objTopEntity.name
  print("Writing test-bench for entity {0}".format(design.topmodule))
  entityBody = design.entity_bodies[_topmodule]
  port_regex = re.compile(r'port\s*\((?P<port_body>.*)\s*\)\s*;'
      , re.IGNORECASE | re.DOTALL)
  m = port_regex.search(entityBody)
  if m :
    portExpr = m.groupdict()['port_body']
    ports = portExpr.split(";")
    portDict = dict()
    for port in ports :
      port = port.strip()
      portlist, dirAndType = port.split(":")
      portlist = portlist.split(",")
      dir = dirAndType.split()[0]
      type = dirAndType.split()[1:]
      for p in portlist :
        portDict[p.strip()] = (dir, type)
    design.objTopEntity.ports = portDict
    signals = ""
    for port in design.objTopEntity.ports :
      signals += "\tSIGNAL " + port  \
           + ": " + design.objTopEntity.ports[port][1][0]+";\n"

    dut = "\tuut : dut ".format(_topmodule) + " PORT MAP (\n";
    portmap = ""
    for port in design.objTopEntity.ports :
      portmap += "\t\t{0} => {0},\n".format(port)

    portmap = portmap[0:-2]
    dut += (portmap + "\n\t);")
    variables = ""
    for port in design.objTopEntity.ports :
      variables += ("\t\tVARIABLE " + "tmp_"+port + " : " + 
          design.objTopEntity.ports[port][1][0] + ";\n")
    assertLines = generateAssertLines(design)
    assignStatements = "\t\t\t--Assign the values"
    # Fill the testbench.
    testbench = testbench.format(entityBody, signals, dut
          , variables, assertLines
          )
  else :
    print("No port is found. This is an error.")
    sys.exit(1)

def generateAssertLines(design ) :
  assertLine = ""
  for port in design.objTopEntity.ports :
    assertLine += "\n\t\t\t-- read {0} value\n".format(port)
    assertLine += "\t\t\tread(l, {0}, good_val);\n".format("tmp_"+port)
    assertLine += '\t\t\tassert good_val REPORT "bad {0} value";\n'.format(port)
    if design.objTopEntity.ports[port][0] == "out" :
      # Out port. Assert the value.
      line = "\t\t\tassert {0} = {1} REPORT \"vector mismatch\";\n".format( 
          "tmp_"+port, port
          )
      assertLine += line
    assertLine += '\t\t\tread(l, space); -- skip a space\n'

  assertLine += "\n\n\t\t\t-- Assign temp signals to ports \n" 
  for port in design.objTopEntity.ports :
    assertLine += "\t\t\t{0} <= {1};\n".format(port, "tmp_"+port)
  return assertLine
  

def processTheFiles(topdir, files) :
  ''' Process the all file listings. '''
  print("Processing all files.")
  design = Design()
  getDesign(design, files)
  topmodule = design.topmodule
  design.objTopEntity.name = topmodule
  # get the port information out of topmodule.
  topentity = design.entity_bodies[topmodule]
  port_regex = r'port\s*\(.*\)\s*;'
  m = re.search(port_regex, topentity, re.IGNORECASE | re.DOTALL)
  if not m :
    print("NOTICE : No port specified in this entity. Looks like it is testbench.")
    print("-- Compile and run it.")
    compileAndRun(design, files, topmodule)
  else :
    addATestBench(design)
    with open("{0}/testbench.vhd".format(topdir), "w") as testF :
      testF.write(testbench)
    # Now, we should generate a file which contains test-vectors. This file must
    # be named vector.test. Ordering of port must be the same as it is in entity
    # declaration. Then we can compile the testbench and run it.
