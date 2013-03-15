import errno
import os
import sys
import xml.etree.cElementTree as ET
import vhdl_regex as vhdl
import mycurses as mc
import subprocess
import shlex

hierXml = ET.Element("hier")

def runDesign(generateTB, simulator="ghdl") :
  # set compiler analyze command.
  compileXml = ET.SubElement(vhdl.vhdlXml, "compiler")
  compileXml.attrib['name'] = 'ghdl'
  topEntities = vhdl.vhdlXml.findall(".//hier/module[@isTopmodule='True']")
  fileDict = dict()
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
        mc.writeOnWindow(mc.dataWindow, msg)
        return
    fileDict[topEntityName] = files
  mc.writeOnWindow(mc.dataWindow, "\n")

  # If generateTB is set then ignore the previous TB and generate  a new one.
  # Else execute the design as it is.
  if generateTB :
    mc.writeOnWindow(mc.processWindow, "\n")
    newFileDict = dict()
    for entity in fileDict :
      # if this entity is already a testbench then remove it from the list and
      # add a new one.
      eXml = vhdl.vhdlXml.find(".//entity[@name='{0}']".format(entity))
      msg = "|- Generating testbench for entity {0} \n".format(entity)
      mc.writeOnWindow(mc.processWindow, msg)      
      if eXml.attrib['noPort'] == "true" : #its a testbench
        fileName = eXml.attrib['file']
        msg = "   |- Ignoring existing one \n"
        fileDict[entity].remove(fileName)
        mc.writeOnWindow(mc.processWindow, msg)
        # add a new testbench
        fileSet = fileDict[entity]
        fileSet.add( vhdl.generateTestBench(entity))
        # Get the name of entity this tb contains.
        compXml = vhdl.vhdlXml.find(".//architecture[@of='{0}']/component"\
            .format(entity))
        entityInTb = compXml.attrib['name']
        newFileDict[entityInTb] = fileSet
      else :                              # no testbench
        fileSet = set(fileDict[entity])
        fileSet.add(vhdl.generateTestBench(entity))
        newFileDict[entity] = fileSet
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
  run(workdir, entityName)

def run(workdir, entityName, time=1000) :
  ''' Running the binary '''
  bin = workdir+"/"+entityName
  if not os.path.isfile(bin) :
    msg = "Error : Binary not found. Existing."
    mc.writeOnWindow(mc.msgWindow, msg
        , opt=mc.curses.color_pair(1))
    return
  # Else run the command.
  command = "{0} --vcd={1}.vcd --stop-time={2}ns \n".format(
      bin, workdir+"/"+entityName, time)
  mc.writeOnWindow(mc.dataWindow, command)
  p = subprocess.Popen(shlex.split(command)
      , stdout = subprocess.PIPE
      , stderr = subprocess.PIPE)
  p.wait()
  status = p.stderr.readline()
  if status.__len__() > 0 :
    mc.writeOnWindow(mc.msgWindow
        , "Failed to run with error :  {0}".format(str(status))
        , indent=2)
  else :
    msg = "Successfully executed \n"
    mc.writeOnWindow(mc.msgWindow, msg)

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
    mc.writeOnWindow(mc.msgWindow
        , "Compilation failed with error :  {0}".format(str(status))
        , opt=mc.curses.color_pair(1)
        , indent=2)
    sys.exit(0)
  else :
    msg = "Compiled : {0}\n".format(filepath)
    mc.writeOnWindow(mc.msgWindow, msg)

def elaborate(workdir, entityname) :
  ''' Elaborate the file '''
  msg = "Elaborating entity {0} \n".format(entityname)
  mc.writeOnWindow(mc.msgWindow, msg)
  bin = workdir+"/"+entityname
  # Before elaboration, check if binary already exists. If yes then remove it.
  if os.path.exists(bin) :
    os.remove(bin)
  command = "ghdl -e --workdir={0} --work=work -o {1} {2}".format(workdir
      , bin, entityname)
  msg = "Executing :\n"
  mc.writeOnWindow(mc.msgWindow, msg, opt=mc.curses.color_pair(2))
  msg = "{0} \n".format(command)
  mc.writeOnWindow(mc.msgWindow
      , msg 
      , opt=mc.curses.color_pair(1)
      )
  p = subprocess.Popen(shlex.split(command)
      , stdout = subprocess.PIPE
      , stderr = subprocess.PIPE
      )
  # Wait for some time. Let the file being saved.
  p.wait()
  if not os.path.isfile(bin) :
    mc.writeOnWindow(mc.msgWindow
        , "ERROR : Could not elaborate entity : {0}".format(entityname)
        , opt=mc.curses.color_pair(2))
    output = "\n\t|- Failed with : {1}".format(bin
        , p.stderr.readline())
    #mc.writeOnWindow(mc.msgWindow, output, indent=2
    #  , opt=mc.curses.color_pair(1)
    #  )
  else :
    mc.writeOnWindow(mc.msgWindow
        , "Elaborated successfully! \n"
        , opt=mc.curses.color_pair(2)
        )

def getHierarchy(elemXml) : 
  global hierXml
  addedEntityXml = dict()
  entityRank = dict()
  elemXml = ET.ElementTree(elemXml)
  entityList = list()
  root = elemXml.getroot()
  if elemXml :
    entities = elemXml.findall('entity')
    # collect all entities
    for entity in entities : 
      entityList.append(entity.attrib['name'])
     
    archs = elemXml.findall('architecture')
    archOfList = list()
    for arch in archs :
      archOfList.append(arch.attrib['of'])

    # build the hierarchy
    while(len(archOfList) > 0) : 
      arch_of = archOfList.pop()
      if arch_of not in addedEntityXml.keys() :
        xml = ET.Element("module")
        xml.attrib['isTopmodule'] = "False"
        xml.attrib['name'] = arch_of
        addedEntityXml[arch_of] = xml 
        entityRank[arch_of] = 0
      else :
        xml = addedEntityXml[arch_of]

      if root.find(".//*[@of='{0}']/component".format(arch_of)) is None :
        if arch_of not in addedEntityXml.keys() :
          # This is never added. It means it is independent and should have
          # non-zero rank.
          entityRank[arch_of] = 1
        else :
          # It has been addeded before. It can not be a top-entity in any case.
          entityRank[arch_of] = 0
        msg = "{0} has no component.\n".format(arch_of)
        #mc.writeOnWindow(mc.dataWindow, msg)
      else :
        components = root.findall(".//*[@of='{0}']/component".format(arch_of))
        entityRank[arch_of] = 1
        for component in components :
          cName = component.attrib['name']
          archOfList.append(cName)
          if cName not in addedEntityXml.keys() :
            cXml = ET.Element("module")
            cXml.attrib['name'] = cName
            cXml = ET.SubElement(xml)
            cXml.attrib['name'] = cName
            entityRank[cName] = 0
          else :
            cXml = addedEntityXml[cName]
            xml.append(cXml)

          msg = "{0} has component : {1} \n".format(arch_of
              , component.attrib['name'])
          #mc.writeOnWindow(mc.dataWindow, msg )
    #mc.writeOnWindow(mc.dataWindow, str(entityRank))

    ## Great now. We can write the hierarchy to hierXml element.
    for i in entityRank :
      if entityRank[i] == 1 :
        addedEntityXml[i].attrib['isTopmodule'] = "True"
        hierXml.append(addedEntityXml[i])
  else :
    msg = "Empty design... Quiting."
    mc.writeOnWindow(mc.msgWindow, msg)
    return

def execute(topdir, files, generateTB=True) :
  msg = "Building design out of files ..."
  mc.writeOnWindow(mc.processWindow, msg)
  msg = " Done \n"
  mc.writeOnWindow(mc.processWindow, msg
      , opt=mc.curses.color_pair(1))
  vhdl.processFiles(topdir, files)
  msg = "Processing design ... "
  global hierXml
  getHierarchy(vhdl.vhdlXml) 
  mc.writeOnWindow(mc.processWindow, msg)
  msg = " Done \n"
  mc.writeOnWindow(mc.processWindow, msg
      , opt=mc.curses.color_pair(1))
  vhdl.vhdlXml.append(hierXml)
  
  # Run each top-entity.
  msg = "Elaborating each design ..."
  mc.writeOnWindow(mc.processWindow, msg)
  runDesign(generateTB)
  msg = "Done \n"
  mc.writeOnWindow(mc.processWindow, msg
      , opt=mc.curses.color_pair(1))
  
  tree = ET.ElementTree(vhdl.vhdlXml)
  tree.write("design.xml")
