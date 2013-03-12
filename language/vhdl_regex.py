import time
import sys
import re
import os
import errno
import shlex
import subprocess
import mycurses as mc
from language.vcd import parse_vcd
from language.test import testVCD

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
\tCOMPONENT {component_name}
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
\t\tFILE vector_file : text read_mode IS "vector.test";
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
    self.entity_files = dict()
    # Root dir of design.
    self.entity_bodies = dict()
    # Architecture of an entity
    self.architectures = dict()
    # Component inside architecture
    self.components = dict()

    self.allcomponents = list()

    self.topmodule = None
    self.topModuleFile = dict()
    self.topModules = list()
    self.objTopEntity = self.TopEntity()


  def designPrint(self) :
    for i in self.allcomponents :
      msg = "Component : {0} ".format(i)
      mc.writeOnWindow(mc.dataWin, msg)
    for i in self.entities :
      entity = i
      msg = "Entity : {}".format(i)
      mc.writeOnWindow(mc.dataWin, msg)
      msg = " Body : {0}".format(self.entity_bodies[i])
      mc.writeOnWindow(mc.dataWin, msg)

  def findTopModule(self) :
    noOfTopModules = 0
    for en in self.entities :
      if en in self.allcomponents : pass
      else :
        noOfTopModules += 1
        self.topmodule = en
        self.topModules.append(en)

    if noOfTopModules != 1 :
      msg = "More than one topmodule are found."
      mc.writeOnWindow(mc.msgWindow, msg)
      msg = ("We'll try to compile all of them.")
      mc.writeOnWindow(mc.msgWindow, msg, indent=2)
    else :
      msg = "Found a top module."
      mc.writeOnWindow(mc.msgWindow, msg)

def parseTxt(design, txt, fileName) :
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
    design.entity_files[match['name']] = fileName

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
      msg = "Parsing file {0}".format(file)
      mc.writeOnWindow(mc.msgWindow, msg)
      txt = ""
      for line in f :
        if(line.strip()[0:2] == "--") : pass 
        else : 
          txt += line
      parseTxt(design, txt, file)
  design.findTopModule()

## Compile and run the design.
def compileAndRun(design, files, topmodule, topdir, testVectors) :
  workdir = topdir+"/work"
  command_string = "ghdl {0} --workdir={1} --work=work --ieee=synopsys "
  topentity = design.objTopEntity.name
  workdir = "/"+"/".join([x for x in workdir.split("/") if len(x) > 1])
  for file in files :
    filename = os.path.basename(file)
    # create the work dir.
    try :
      os.makedirs(workdir)
    except OSError as exception :
      if exception.errno != errno.EEXIST :
        raise

    command = command_string.format( '-a', workdir)
    analyzeCommand = "{0} {1}".format(command, file)
    p1 = subprocess.Popen(shlex.split(analyzeCommand)
        , stdout = subprocess.PIPE
        , stderr = subprocess.PIPE
        )
    p1.wait()
    status = p1.stderr.readline()
    if status.__len__() > 0 :
      mc.writeOnWindow(mc.dataWindow
          , "Compilation failed with error :  {0}".format(str(status))
          , indent=2
          )
    else :
      msg = "Compile : {0}".format(file)
      mc.writeOnWindow(mc.msgWindow
          , msg
          )

  msg = "Elaborating : {0}".format(topentity)
  mc.writeOnWindow(mc.msgWindow, msg)

  command = command_string.format('-e', workdir)
  bin = topdir+"/"+topentity
  bin = "/"+"/".join([x for x in bin.split("/") if len(x) > 1])
  
  # Before elaboration, check if binary already exists. If yes then remove it.
  if os.path.exists(bin) :
    os.remove(bin)
  elabCommand = "{0} -o {2} {1}".format(command, topentity, bin)
  msg = "Executing :\n\t {0} ".format(elabCommand)
  mc.writeOnWindow(mc.processWindow
      , msg 
      , opt=mc.curses.color_pair(1)
      )
  p2 = subprocess.Popen(shlex.split(elabCommand)
      , stdout = subprocess.PIPE
      , stderr = subprocess.PIPE
      )
  # Wait for some time. Let the file being saved.
  p2.wait()
  if not os.path.isfile(bin) :
    mc.writeOnWindow(mc.dataWindow
        , "ERROR : Could not elaborate entity : {0}".format(topentity)
        , opt=mc.curses.color_pair(2))
    output = "{0} does not exists.\n Or failed with : {1}".format(bin
        , p2.stderr.readline())
    mc.writeOnWindow(mc.dataWindow, output, indent=2
      , opt=mc.curses.color_pair(1))
  else :
    mc.writeOnWindow(mc.dataWindow
        , "Elaborated successfully!"
        , opt=mc.curses.color_pair(2)
        )
    # Run the simulation.
    vcddir = topdir+"/waveforms"
    if not os.path.exists(vcddir) :
      os.makedirs(vcddir)
    vcdfile = vcddir+"/"+topentity+".vcd"
    vcdfile = "/"+"/".join([x for x in vcdfile.split("/") if len(x) > 1])
    command = '{0} --vcd={1} --stop-time=1000ns'.format(bin, vcdfile)
    p3 = subprocess.Popen(shlex.split(command)
        , stdout = subprocess.PIPE
        , stderr = subprocess.PIPE 
        )
    p3.wait()
    if testVectors :
      mc.writeOnWindow(mc.msgWindow, "Testing with test-vectors."
          , opt=mc.curses.color_pair(1))
    else :
      mc.writeOnWindow(mc.msgWindow, "Testing with user-provided test bench."
          , opt=mc.curses.color_pair(1))
      vcddata = parse_vcd(vcdfile)
      vcds = dict()
      for i in vcddata :
        if vcddata[i]['nets'][0]['hier'] == 'dut' :
          sigName = vcddata[i]['nets'][0]['name']
          vcds[sigName] = vcddata[i]['tv']
      testVCD(vcds)

def addATestBench(design) :
  ''' Add a test-bench '''
  global testbench
  _topmodule = design.objTopEntity.name
  msg = ("Writing test-bench for entity {0}".format(design.topmodule))
  mc.writeOnWindow(mc.processWindow, msg)
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

    dut = "\tdut : {0} ".format(_topmodule) + " PORT MAP (\n";
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
    testbench = testbench.format( entityBody, signals, dut
        , variables, assertLines
        , component_name = _topmodule
        )
  else :
    msg = "No port is found. This is an error."
    mc.writeOnWindow(mc.msgWindow, msg)
    mc.msgWindow.getch()
    mc.killCurses()
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
  

def compileAndRunATopModule(design, topDir
    , files
    , topModule
    , testVectors = False) :
  # get the port information out of topmodule.
  msg = "Compiling a top module : {0}".format(topModule)
  mc.writeOnWindow(mc.processWindow, msg)

  topentity = design.entity_bodies[topModule]
  topEntityFileName = design.entity_files[topModule]
  topEntityDir = os.path.dirname(topEntityFileName)

  port_regex = r'port\s*\(.*\)\s*;'
  m = re.search(port_regex, topentity, re.IGNORECASE | re.DOTALL)
  if not m :
    msg = "Found a testbench."
    mc.writeOnWindow(mc.msgWindow, msg, indent=3)
    msg = "|- Compile and run it."
    mc.writeOnWindow(mc.msgWindow, msg, indent=3)
    compileAndRun(design, files, topModule, topEntityDir, testVectors=False)
  else :
    msg = "Notice : No testbench found. Generating one."
    mc.writeOnWindow(mc.processWindow, msg, indent=1)
    addATestBench(design)
    testbenchFile = "{0}/testbench.vhd".format(topdir)
    with open(testbenchFile, "w") as testF :
      testF.write(testbench)

    # Add this testbench file to other files and compile the design.
    set(files).add(testbenchFile)

    # Now, we should generate a file which contains test-vectors. This file must
    # be named vector.test. Ordering of port must be the same as it is in entity
    # declaration. Then we can compile the testbench and run it.
    compileAndRunATopModule(design, topDir, files, topModule, testVectors=True)

def processTheFiles(topdir, files) :
  ''' Process the all file listings. '''
  msg = "Processing all files and finding designs.."
  mc.writeOnWindow(mc.processWindow, msg)
  design = Design()
  getDesign(design, files)
  for topmodule in design.topModules :
    design.objTopEntity.name = topmodule
    compileAndRunATopModule(design, topdir, files, topmodule)
  
