import errno
import os
import sys
import xml.etree.cElementTree as ET
import vhdl_regex
import subprocess
import shlex
import re
import language.test as test
import debug.debug as debug

class VHDL(vhdl_regex.VHDLParser):

    def __init__(self, topdir):
        self.topdir = topdir
        self.workdir = os.path.join(self.topdir, 'work')
        self.hierXml = ET.Element("hier")
        self.topModule = None
        self.genericsDict = dict()

    def runDesign(self, generateTB, simulator) :
        """ Run the damn design
        """
        # check for compiler. If it does not exists, quit.
        debug.printDebug("USER", "Using {0}".format(simulator))
        self.simulator = simulator
        try:
            subprocess.call([simulator, "--version"], stdout=subprocess.PIPE)
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                raise RuntimeError, "Simulator {0} not found".format(simulator)
            else:
                debug.printDebug("ERR"
                        , "Something went wrong when checking for {0}".format(
                            simulator
                            )
                        )
                raise e
        # set compiler analyze command.
        self.topdir = self.vhdlXml.attrib['dir']
        compileXml = ET.SubElement(self.vhdlXml, "compiler")
        compileXml.attrib['name'] = 'ghdl'
        topEntities = self.vhdlXml.findall(".//hier/module[@topEntity='true']")
        fileDict = dict()
        if self.topModule is not None and len(self.topModule) > 0:
            topEntities = self.vhdlXml.findall(
                    ".//hier/module[@name='{0}']".format(topModule)
                    )
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
                entity = self.vhdlXml.find(
                        ".//entity[@name='{0}']".format(entityName)
                        )
                if entity is not None :
                    fileOfEntity = entity.attrib['file']
                    files.add(fileOfEntity)
                else :
                    raise UserWarning, "Entity {0} not found".format(entity)
            fileDict[topEntityName] = files
      
        # If generateTB is set then ignore the previous TB and generate  a new one.
        # Else execute the design as it is.
        if not generateTB:
            return 

        newFileDict = dict()
        for entity in fileDict :
            # if this entity is already a testbench then remove it from the list and
            # add a new one.
            eXml = self.vhdlXml.find(".//entity[@name='{0}']".format(entity))
            debug.printDebug("INFO"
                    , "Generating testbench for entity {0}".format(entity)
                    )
            if eXml.attrib['noPort'] == "true": # It's a testbench.
                fileName = eXml.attrib['file']
                debug.printDebug("WARN", "Ignoring existing one")
                fileDict[entity].remove(fileName)
                # add a new testbench. Need to find an entity which is its children.
                fileSet = fileDict[entity]
                # Get the name of entity this tb contains.
                compXml = self.vhdlXml.find(
                        ".//architecture[@of='{0}']/component".format(entity)
                        )
                try:
                    entityInTb = compXml.attrib['name']
                    tbName = "auto_generated_"+entityInTb+".vhd"
                    fileSet.add( self.generateTestBench(entityInTb, tbName))
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
                fileSet.add(self.generateTestBench(entity, tbName))
                newFileDict[tbEntity] = fileSet
        # Copy the new file list to old one.
        fileDict = newFileDict
      
        # Great, now simulate.
        for entity in fileDict :
          self.runATopEntity(entity, fileDict[entity])
      
    def runATopEntity(self, entityName, fileSet) :
        topdir = self.vhdlXml.attrib['dir']
        self.workdir = os.path.join(topdir, "work")
        try :
            os.makedirs(self.workdir)
        except OSError as exception :
            if exception.errno != errno.EEXIST :
                raise
        for file in fileSet : 
            filepath = topdir+file
            self.analyze(filepath)
        self.elaborate(entityName)
        self.generateTestVector(entityName)
        self.run(entityName)

    def run(self, topdir, entityName, time=1000) :
        ''' Running the binary '''
        workdir = self.workdir
        bin = workdir+"/"+entityName
        testVecPath = os.path.join(workdir, "vector.test")
        debug.printDebug("STEP", "Simulating design")
        if not os.path.exists(testVecPath) :
            raise IOError, "{0} not found".format(testVecPath)

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
            print("Successfully executed")

    def analyze(self, filepath) :
        ''' Analyze a file. '''
        workdir = self.workdir
        if self.simulator == "ghdl":
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
                print("Compiled : {0}".format(filepath))

    def elaborate(self, entityname) :
        ''' Elaborate the file '''
        workdir = self.workdir
        debug.printDebug("STEP", "Elaborating entity {0} \n".format(entityname))
        bin = os.path.join(self.workdir, entityname)
        # Before elaboration, check if binary already exists. If yes then remove
        # it.
        if os.path.exists(bin):
            os.remove(bin)
        command = "ghdl -e --workdir={0} --work=work -o {1} {2}".format(workdir
            , bin, entityname)
        debug.printDebug("DEBUG", "Executing: \n$ {0}".format(command))
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

    def getNextLevelsOfHier(self, archName, hasParents, childLess , alreadyAddedArcs):
        '''
        Get the components of a xmlElem.
        @param elemXml : Xml element of archName 
        @param archName : name of the entity of this architecture
        '''
        if archName not in alreadyAddedArcs.keys():
            debug.printDebug("WARN", "Funtion validations error"\
                +": {0} should have been added to args 2".format(archName))
            return None
        comps = self.vhdlXml.findall(".//architecture[@of='{0}']/*".format(archName))
        archXml = alreadyAddedArcs[archName]
        if len(comps) < 1 :
            debug.printDebug("INFO"
                    , "No component found for {0}".format(archName)
                    )
            childLess.add(archName)
            return 
        for comp in comps :
            compName = comp.attrib['name']
            debug.printDebug("DEBUG", "Component {0} found for entity {1}".format(
                    compName
                    , archName
                    )
                )
            if comp.attrib['isInstantiated'] == "true":
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
                debug.printDebug("WARN"
                        , "Component {0} is not instantited.".format(compName)
                        )

    def getHierarchy(self): 
        ''' Generate the hierarchy and store it in a xml element elemXml
        '''
        allEntities = set()
        hasParents = set()
        childLess = set()
        # keep the aleady added xml elements of architecture in a dictionary.
        alreadyAddedArcs = dict()
        # get the list of entities we have.
        entities = self.vhdlXml.findall('entity')
        # collect all entities
        for entity in entities : 
            entityName = entity.attrib['name']
            allEntities.add(entityName)
            # If this entity is already added to hierarchy then ignore it
            # otherwise
            # create an xml element of it.
            if entityName not in alreadyAddedArcs.keys() :
                entityXml = ET.Element("module")
                entityXml.attrib['name'] = entityName 
                alreadyAddedArcs[entityName] = entityXml
            else :
                entityXml = alreadyAddedArcs[entityName]
                # Pass this name of entity along with root xmlElement to be
                # processed.
                self.getNextLevelsOfHier(entityName
                        , hasParents
                        , childLess
                        , alreadyAddedArcs
                        )
        
        # Here we should have two sets. Nodes which do not have children and
        # nodes which do not have parents. Nodes with following properties can
        # not be top-modules.  1. Those who belongs to hasParents set.
        topModulesSet = allEntities - hasParents
        for topModule in topModulesSet :
          x = (alreadyAddedArcs[topModule])
          x.attrib['topEntity'] = "true"
          self.hierXml.append(x)

    def execute(self, files, top, generateTB) :
        ''' Top most function in this folder.'''

        self.topModule = top
        # We must delete all files automatically generated before (if any). All
        # such files have auto_generated_ prefix.
        newFiles = set()
        for file in files :
            if re.search(r"auto_generated_", file) : pass 
            else : newFiles.add(file)
        files = newFiles

        debug.printDebug("STEP", "Building design out of files.")
        parseVhdl = vhdl_regex.VHDLParser(topdir=self.topdir)
        self.vhdlXml = parseVhdl.parseFiles(files)

        debug.printDebug("STEP", "Processing design")
        self.getHierarchy() 
        self.vhdlXml.append(self.hierXml)

        # Run each top-entity
        debug.printDebug("STEP", "Elaborating each design ...")
        self.runDesign(generateTB, "ghdl")

    def generateTestVector(self, entityName) :
        top = self.vhdlXml.attrib['dir']
        debug.printDebug("STEP", "Generating vector.test file.")
        # call this function now.
        test.testEntity(entityName, top)
        return
