import errno
import os
import sys
import xml.etree.cElementTree as ET
import vhdl_regex as vhdl
import subprocess
import shlex
import re
import language.test as test

hierXml = ET.Element("hier")

def runDesign(topModule, generateTB, simulator="ghdl") :
  # set compiler analyze command.
  topDir = vhdl.vhdlXml.attrib['dir']
  compileXml = ET.SubElement(vhdl.vhdlXml, "compiler")
  compileXml.attrib['name'] = 'ghdl'
  topEntities = vhdl.vhdlXml.findall(".//hier/module[@topEntity='true']")
  fileDict = dict()
  if topModule :
    topModule = topModule[0]
    topEntities = vhdl.vhdlXml.findall(".//hier/module[@name='{0}']"\
        .format(topModule))
  for te in topEntities :
    # Files needed to elaborate the design.
    files = set()
    neededEntity = set()
    topEntityName = te.attrib['name']
    neededEntity.add(topEntityName)
    children = te.findall(".//*")
    for child in children :
      neededEntity.add(child.attrib['name'])
    # get files we need to compile to elaborate this entity.
    for entityName in neededEntity :
      entity = vhdl.vhdlXml.find(".//entity[@name='{0}']".format(entityName))
      if entity is not None :
        fileOfEntity = entity.attrib['file']
        files.add(fileOfEntity)
      else :
        msg = "Horror : Entity not found \n"
        print(msg)
        return
    fileDict[topEntityName] = files

  # If generateTB is set then ignore the previous TB and generate  a new one.
  # Else execute the design as it is.
  if generateTB :
    newFileDict = dict()
    for entity in fileDict :
      # if this entity is already a testbench then remove it from the list and
      # add a new one.
      eXml = vhdl.vhdlXml.find(".//entity[@name='{0}']".format(entity))
      msg = "|- Generating testbench for entity {0} \n".format(entity)
      print(msg)
      if eXml.attrib['noPort'] == "true" : # It's a testbench.
        fileName = eXml.attrib['file']
        msg = "   |- Ignoring existing one \n"
        fileDict[entity].remove(fileName)
        print(msg)
        # add a new testbench. Need to find an entity which is its children.
        fileSet = fileDict[entity]
        # Get the name of entity this tb contains.
        compXml = vhdl.vhdlXml.find(".//architecture[@of='{0}']/component"\
            .format(entity))
        try:
            entityInTb = compXml.attrib['name']
            tbName = "auto_generated_"+entityInTb+".vhd"
            fileSet.add( vhdl.generateTestBench(entityInTb, tbName))
            tbEntity = "tb_"+entityInTb
            newFileDict[tbEntity] = fileSet
        except Exception as e:
            msg = "No test bench found in {0}".format(compXml)
            print(msg)
            return 
      else :                              # no testbench
        fileSet = set(fileDict[entity])
        tbName = "auto_generated_"+entity+".vhd"
        tbEntity = "tb_"+entity
        fileSet.add(vhdl.generateTestBench(entity, tbName))
        newFileDict[tbEntity] = fileSet
    # Copy the new file list to old one.
    fileDict = newFileDict

  # Great, now simulate.
  for entity in fileDict :
    runATopEntity(entity, fileDict[entity])

def runATopEntity(entityName, fileSet) :
  topdir = vhdl.vhdlXml.attrib['dir']
  workdir = topdir+"/work"
  try :
    os.makedirs(workdir)
  except OSError as exception :
    if exception.errno != errno.EEXIST :
      raise
  for file in fileSet : 
    filepath = topdir+file
    analyze(workdir, filepath)
  elaborate(workdir, entityName)
  generateTestVector(entityName)
  run(topdir, entityName)

def run(topdir, entityName, time=1000) :
  ''' Running the binary '''
  workdir = topdir+"/work"
  bin = workdir+"/"+entityName
  testVecPath = workdir+"/vector.test"
  msg = "Simulating design ...\n"
  print(msg)
  if not os.path.exists(testVecPath) :
    msg = "Error : Test vector is not generated. Existing...\n\
    Expecting {0}".format(testVecPath)
    print(msg)
    return

  if not os.path.isfile(bin) :
    msg = "Error : Binary not found. Existing."
    print(msg)
    return
  # Else run the command.
  command = "{0} --vcd={1}.vcd --stop-time={2}ns \n".format(
      bin, workdir+"/"+entityName, time)
  print(command)
  p = subprocess.Popen(shlex.split(command)
      , stdout = subprocess.PIPE
      , stderr = subprocess.PIPE)
  p.wait()
  status = p.stderr.readline()
  if status.__len__() > 0 :
      print("Error status :  {0}".format(str(status)))
  else :
    print("Successfully executed \n")

def analyze(workdir, filepath) :
  ''' Analyze a file. '''
  command = "ghdl -a --workdir={0} --work=work \
      --ieee=synopsys {1}".format(workdir, filepath)
  p1 = subprocess.Popen(shlex.split(command)
      , stdout = subprocess.PIPE
      , stderr = subprocess.PIPE)
  p1.wait()
  status = p1.stderr.readline()
  if status.__len__() > 0 :
    print("Compilation failed with error :  {0}".format(str(status)))
    sys.exit(0)
  else :
      print("Compiled : {0}\n".format(filepath))

def elaborate(workdir, entityname) :
  ''' Elaborate the file '''
  msg = "Elaborating entity {0} \n".format(entityname)
  print(msg)
  bin = workdir+"/"+entityname
  # Before elaboration, check if binary already exists. If yes then remove it.
  if os.path.exists(bin) :
    os.remove(bin)
  command = "ghdl -e --workdir={0} --work=work -o {1} {2}".format(workdir
      , bin, entityname)
  msg = "{0} \n".format(command)
  print(msg)
  p = subprocess.Popen(shlex.split(command)
      , stdout = subprocess.PIPE
      , stderr = subprocess.PIPE
      )
  # Wait for some time. Let the file being saved.
  p.wait()
  if not os.path.isfile(bin) :
      print( "ERROR : Could not elaborate entity : {0}".format(entityname))
      print("\n\t|- Failed with : {1}".format(p.stderr.readline()))
  else :
      print("Elaborated successfully! \n")

def getNextLevelsOfHier(archName, elemXml, hasParents, childLess,
    alreadyAddedArcs) :
  '''
  Get the components of a xmlElem.
  @param elemXml : Xml element of archName 
  @param archName : name of the entity of this architecture
  '''
  if archName not in alreadyAddedArcs.keys() :
    msg = "Funtion validations error : {0} should have been added to args 2"
    print(msg)
    return None
  comps = elemXml.findall(".//architecture[@of='{0}']/*"\
      .format(archName))
  archXml = alreadyAddedArcs[archName]
  if len(comps) < 1 :
    msg = "No component found for {0}\n".format(archName)
    print(msg)
    childLess.add(archName)
    return elemXml
  for comp in comps :
    compName = comp.attrib['name']
    msg = "Component {0} found for entity {1}\n".format(compName, archName)
    print(msg)
    if comp.attrib['isInstantiated'] == "true" :
      hasParents.add(compName)
      # Now check if architecture of this component was already added.
      if compName in alreadyAddedArcs.keys() :
        compXml = alreadyAddedArcs[compName]
        archXml.append(compXml)
      else :
        compXml = ET.Element("module")
        compXml.attrib['name'] = compName 
        alreadyAddedArcs[compName] = compXml
        archXml.append(compXml)
    else :
      msg = "{0} component is not instantited.\n".format(compName)
      print(msg)


def getHierarchy(elemXml) : 
  ''' Generate the hierarchy and store it in a xml element elemXml
  '''
  global hierXml

  allEntities = set()
  hasParents = set()
  childLess = set()
  # keep the aleady added xml elements of architecture in a dictionary.
  alreadyAddedArcs = dict()
  # get the list of entities we have.
  entities = elemXml.findall('entity')
  # collect all entities
  for entity in entities : 
    entityName = entity.attrib['name']
    allEntities.add(entityName)
    # If this entity is already added to hierarchy then ignore it otherwise
    # create an xml element of it.
    if entityName not in alreadyAddedArcs.keys() :
      entityXml = ET.Element("module")
      entityXml.attrib['name'] = entityName 
      alreadyAddedArcs[entityName] = entityXml
    else :
      entityXml = alreadyAddedArcs[entityName]
    # Pass this name of entity along with root xmlElement to be processed.
    getNextLevelsOfHier(entityName, elemXml, hasParents
        , childLess , alreadyAddedArcs)
  
  # Here we should have two sets. Nodes which do not have children and nodes
  # which do not have parents. Nodes with following properties can not be
  # top-modules.
  # 1. Those who belongs to hasParents set.
  topModulesSet = allEntities - hasParents
  for topModule in topModulesSet :
    x = (alreadyAddedArcs[topModule])
    x.attrib['topEntity'] = "true"
    hierXml.append(x)

def execute(topdir, files, top, generateTB) :
  ''' Top most function in this folder.'''
  # We must delete all files automatically generated before (if any). All such
  # files have auto_generated_ prefix.
  newFiles = set()
  for file in files :
    if re.search(r"auto_generated_", file) : pass 
    else : newFiles.add(file)
  files = newFiles
  msg = "Building design out of files ... Done"
  print(msg)
  vhdl.processFiles(topdir, files)
  print("Processing design ... ")
  global hierXml
  getHierarchy(vhdl.vhdlXml) 
  vhdl.vhdlXml.append(hierXml)
  
  # Run each top-entity.
  print("Elaborating each design ...")
  runDesign(top, generateTB)

def generateTestVector(entityName) :
  top = vhdl.vhdlXml.attrib['dir']
  print("Generating vector.test file.")
  # call this function now.
  test.testEntity(entityName, top)
  return
