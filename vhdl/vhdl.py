import errno
import os
import sys
import xml.etree.ElementTree as ET
import vhdl_parser
import subprocess
import shlex
import re
import debug.debug as debug
import inspect
import methods.command as cmd

class VHDL(vhdl_parser.VHDLParser):
    ''' Class for vhdl '''

    def __init__(self, topdir, compiler):
        self.topdir = topdir
        self.workdir = os.path.join(self.topdir, 'work')
        self.hierXml = ET.Element("hier")
        self.topModule = None
        self.moduleList = set()
        self.genericsDict = dict()
        self.compiler = compiler
        self.runtime = 1000
        self.prefix = '__auto_genereted_'
        self.signalDict = dict()
        self.testVectorFile = None
        self.generateTB = None
        self.tempDir = '_temp'
        if not os.path.isdir(self.tempDir):
            os.makedirs(self.tempDir)

    def runATopEntity(self, entityName, fileSet) :
        """Running a top entity
        """
        topdir = self.vhdlXml.attrib['dir']
        self.workdir = os.path.join(topdir, "work")
        try :
            os.makedirs(self.workdir)
        except OSError as exception :
            if exception.errno != errno.EEXIST :
                raise
        for file in fileSet : 
            filepath = os.path.join(topdir, file)
            self.analyze(filepath)
        self.elaborate(entityName)
        if not self.testVectorFile:
            self.generateTestVector(entityName)
        self.run(entityName=entityName)

    def simulateUsingVsim(self, entityName, fileSet):
        cmd.runCommand(["vlib", self.workdir])
        for file in fileSet:
            file = os.path.join(self.topdir, file)
            debug.printDebug("STEP"
                    , "Compiling {0} using modelsim".format(file)
                    )
            cmd.runCommand(["vcom", file])
        if None:
            cmd.runCommand(["vsim", "-c", "-do", "run {}; quit".format(self.runtime)
                , entityName]
                , stdout=None, stderr=None
                )

    def run(self,  entityName, time=1000) :
        ''' Running the binary '''
        if "ghdl" in self.compiler:
            self.simulator = self.compiler
            workdir = self.workdir
            bin = workdir+"/"+entityName
            debug.printDebug("STEP", "Simulating design")
            if not os.path.isfile(bin) :
                msg = "Error : Binary not found. Existing."
                debug.printDebug("WARN", msg)
                return
            # Else run the command.
            command = "{0} --vcd={1}.vcd --stop-time={2}ns \n".format(
                    bin, workdir+"/"+entityName, time)
            cmd.runCommand(shlex.split(command))

        if "vsim" in self.compiler:
            print("using vsim")


    def analyze(self, filepath) :
        ''' Analyze a file. '''
        workdir = self.workdir
        if "ghdl" in self.compiler:
            command = "ghdl  -a --workdir={0} --work=work \
                --ieee=synopsys {1}".format(workdir, filepath)
            cmd.runCommand(shlex.split(command))
        elif "vsim" in self.compiler:
            cmd.runCommand(["vlib", self.workdir])
            cmd.runCommand(["vcom", filepath])
        else:
            debug.printDebug("WARN"
                    , "Unknown compiler %s " % self.compiler
                    )
            return None

    def elaborate(self, entityname) :
        ''' Elaborate the file '''
        if "ghdl" in self.compiler:
            workdir = self.workdir
            debug.printDebug("STEP", "Elaborating entity {0}".format(entityname))
            bin = os.path.join(self.workdir, entityname)
            # Before elaboration, check if binary already exists. If yes then remove
            # it.
            if os.path.exists(bin):
                os.remove(bin)
            command = "ghdl -e --workdir={0} --work=work -o {1} {2}".format(workdir
                , bin, entityname)
            cmd.runCommand(shlex.split(command))
        else:
            pass

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
            debug.printDebug("DEBUG"
                    , "No component found for {0}".format(archName)
                    )
            childLess.add(archName)
            return 
        for comp in comps :
            compName = comp.attrib['name']
            instanceOf = comp.attrib['instance_of']
            debug.printDebug("DEBUG"
                    , "Component {0} found for entity {1}".format(
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
                    compXml = ET.Element("component")
                    compXml.attrib['name'] = compName 
                    compXml.attrib['instance_of'] = instanceOf
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
            # otherwise create an xml element of it.
            if entityName not in alreadyAddedArcs.keys() :
                entityXml = ET.Element("module")
                entityXml.attrib['name'] = entityName 
                alreadyAddedArcs[entityName] = entityXml

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

    def main(self, files, args) :
        ''' Top most function in this folder.'''

        self.generateTB = args.generate_tb
        self.testVectorFile = args.test_vector_file
        self.topModule = args.top_module
        # We must delete all files automatically generated before (if any). All
        # such files have auto_generated_ prefix.
        newFiles = set()
        for file in files :
            if re.search(self.prefix, file) : pass 
            else : newFiles.add(file)
        files = newFiles

        debug.printDebug("STEP", "Building design out of files.")
        parseVhdl = vhdl_parser.VHDLParser(topdir=self.topdir)
        self.vhdlXml = parseVhdl.parseFiles(files)

        debug.printDebug("STEP", "Processing design and building hierarchy")
        self.getHierarchy() 

        # dump the xml for debugging purpose.
        with open("vhdl.xml", "w") as f:
            f.write(ET.tostring(self.vhdlXml))
        with open("hier.xml", "w") as f:
            f.write(ET.tostring(self.hierXml))
        
        # Run each top-entity
        self.runDesign(self.generateTB)

    def generateTestVector(self, entityName) :
        top = self.vhdlXml.attrib['dir']
        debug.printDebug("TODO", "Generating vector.test file.")
        # call this function now.
        #test.testEntity(entityName, top)
        return

    def runDesign(self, generateTB):
        """ Run the damn design
        """
        # check for compiler. If it does not exists, quit.
        self.topdir = self.vhdlXml.attrib['dir']
        compileXml = ET.SubElement(self.vhdlXml, "compiler")
        compileXml.attrib['name'] = self.compiler
        if self.topModule is None and len(self.moduleList) > 0:
            self.topModule = self.moduleList[0].strip()
        elif self.topModule:
            pass
        else:
            debug.printDebug("WARN"
                    , "Could not find any top-module %s " % self.topModule
                    , frame = inspect.currentframe()
                    )
            return 0

        self.topEntities = list()
        for t in self.vhdlXml.findall('.//entity[@name]'):
            # topModule is a list of entities.
            if t.get('name') in self.topModule:
                self.topEntities.append(t)

        # Now work on all entities collected.
        self.fileDict = dict()
        for te in self.topEntities :
            # Files needed to elaborate the design.
            files = set()
            neededEntity = set()
            topEntityName = te.attrib['name']
            neededEntity.add(topEntityName)
            children = te.findall("component")
            for child in children :
                neededEntity.add(child.attrib['instance_of'])

            # get files we need to compile to elaborate this entity.
            for entityName in neededEntity :
                entity = self.vhdlXml.find(
                        "entity[@name='{0}']".format(entityName)
                        )
                if entity is not None :
                    fileOfEntity = entity.attrib['file']
                    files.add(fileOfEntity)
                else :
                    raise UserWarning, "Entity {0} not found".format(entity)

            self.fileDict[topEntityName] = files
      
        # If generateTB is set then ignore the previous TB and generate  a new one.
        # Else execute the design as it is.
        if not generateTB:
            debug.printDebug("INFO"
                    , "Not generating testbenches. In fact doing nothing more"
                    )
            return None 
        else:
            newFileDict = dict()
            [self.testBench(file, newFileDict) for file in self.fileDict]

        # Copy the new file list to old one.
        self.fileDict = newFileDict
      
        # Great, now simulate.
        for entity in self.fileDict:
            self.runATopEntity(entity, self.fileDict[entity])
      


    def testBench(self, entity, newFileDict):
        """Generate the test-bench """
        
        # if this entity is already a testbench then remove it from the list and
        # add a new one.
        eXml = self.vhdlXml.find(".//entity[@name='{0}']".format(entity))
        debug.printDebug("STEP"
                , "Generating testbench for entity {0}".format(entity)
                )
        if eXml.attrib['noPort'] == "true": # It's a testbench.
            fileName = eXml.attrib['file']
            debug.printDebug("WARN"
                    , "Entity {} in {} is a testbench. Ignoring it..".format(
                        entity
                        , fileName
                        )
                    )
            # add a new testbench. Need to find an entity which is its children.
            fileSet = self.fileDict[entity]
            self.fileDict[entity].remove(fileName)
            newFileDict[entity] = fileSet
        else :                              # no testbench
            fileSet = set(self.fileDict[entity])
            tbName = self.prefix + entity + ".vhd"
            tbEntity = "tb_"+entity
            fileSet.add(
                    self.generateTestBench(entity, tbName, self.testVectorFile)
                    )
            newFileDict[tbEntity] = fileSet
