import time
import sys
import re
import os
import errno
import shlex
import subprocess
from language.vcd import parse_vcd
from language.test import testVCD
import xml.etree.cElementTree as ET
import errno
import debug.debug as debug
import collections


class VHDLParser:

    def __init__(self, topdir=""):
        self.tb = ""
        self.topdir = topdir
        self.vhdlXml = ET.Element("design")

    def testbenchFromDict(self, tDict):
        testbench = '''
ENTITY tb_{0} IS END;
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

ARCHITECTURE arch OF tb_{0} IS 

\t----------------------------------------------------------------
\t-- Component declaration.
\t----------------------------------------------------------------
\tCOMPONENT {0} 
\t\tPORT ( \n'''.format(tDict.get('comp_name'))
        testbench += "{0}".format(tDict.get('comp_decl'))
        testbench = testbench[0:-2]
        testbench += ''');
\tEND COMPONENT;
\t
\t-- Signals in entity 
'''
        testbench += "{0}".format(tDict.get('signal_decl'))
        testbench += '''
BEGIN
\t-- Instantiate a dut 
'''
        testbench += "{0}".format(tDict.get('dut_instance'))
        testbench += '''
\ttest : PROCESS 
\t\t-- Declare variables to store the values stored in test files. 
'''
        testbench += "{0}".format(tDict['variables'])
        testbench += '''
\t\t-- File and its minions.
\t\tFILE vector_file : TEXT OPEN read_mode IS "{0}";'''.format(tDict['vector_file_path'])
        testbench += '''
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
\t\t\t-- Read other singals etc. '''
        testbench += "{0}".format(tDict.get('asserts'))
        testbench += '''
\t\tEND LOOP;
\t\tASSERT false REPORT "Test complete";
\t\tWAIT;
\tEND PROCESS;
END ARCHITECTURE arch;
-- Testbech ends here.
  '''
        self.tb = testbench
        return testbench
        
    def parseTxt(self, txt, fileName) :
        '''
        Parse the given 'txt'. Construct a design object which has topmodule.
        If this topmodule is not a test bench then write one. Compile and simulate.
        '''
        elemXml = self.vhdlXml
        topdir = self.vhdlXml.attrib['dir']
        if not topdir:
            raise IOError, "Can't fetched dir from designXMl. Got {0}".format(topdir)
        pattern = r'entity\s+(?P<name>\w+)\s+is\s*(?P<body>.*)'\
          +'end\s*(entity)?\s*(?P=name)?\s*;'
        entity = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        m = entity.finditer(txt)
        for i in m :
            match = i.groupdict()
            body = match['body']
            entityXml = ET.SubElement(elemXml, "entity")
            #entityXml.text = str(body)
            entityXml.attrib['name'] = match['name']
            baseName = fileName.replace(topdir,"")
            entityXml.attrib['file'] = baseName
            entityXml.attrib['noPort'] = 'false'
            genericPattern = re.compile(r'generic\s*\(((?!port).)+\)\s*;'
                , re.IGNORECASE | re.DOTALL)
            genericMatch = genericPattern.finditer(body) 
            for gi in genericMatch :
                genericText = gi.group(0)
                genericXml = ET.SubElement(entityXml, "generic")
                genericXml.text = genericText
            portExpr = re.compile(r'port\s*\(((?!end).)+\)\s*;'
                    , re.IGNORECASE | re.DOTALL
                    )
            portMatch = portExpr.search(body)
            if portMatch :
                portText = portMatch.group(0)
                self.parsePortText(entityXml, portText)
            else:
                entityXml.attrib['noPort'] = "true"
      
        architecture_body = '(?P<arch_body>((?!entity).)+)'
        pattern = r'architecture\s+(?P<arch_name>\w+)\s+of\s+(?P<arch_of>\w+)'\
            +'\s+is\s+{0}'.format( architecture_body)
        architecture = re.compile(pattern, re.IGNORECASE | re.DOTALL);
        m = architecture.finditer(txt)
        for i in m :
            match = i.groupdict()
            arch_name = match['arch_name']
            arch_body = match['arch_body']
            arch_of = match['arch_of']
            archXml = ET.SubElement(elemXml, "architecture")
            archXml.attrib['name'] = arch_name
            archXml.attrib['of'] = arch_of
            self.parseArchitectureText(archXml, arch_body)


    def parseArchitectureText(self, elemXml, arch_body) :
        ''' 
        Parse the architecture text and find out which component is instantiated
        in this architecture.
        '''
        assert len(arch_body) > 2, "Text in architecture {0}".format(arch_body)
        instanceDict = collections.defaultdict(list)
        component_inst_expr = r'(?P<instance_name>\w+)\s*\:\s*'\
            +'(?P<arch_name>\w+)\s+(generic|port)\s+(map)'
        pattern = re.compile(component_inst_expr, re.IGNORECASE | re.DOTALL)
        mm = pattern.finditer(arch_body) 
        for ii in mm :
            instanceName = ii.groupdict()['instance_name']
            instanceOf = ii.groupdict()['arch_name']
            instanceDict[instanceOf].append(instanceName)
      
        # Not all components are instantiated. Some are imported from libraries.
        # Following take care of instantiated components. 
        component_decl_pat = r'\s*component\s+(?P<comp_name>\w+)'\
            +'(((?!component).)+)\s*end\s+component'
        pattern = re.compile(component_decl_pat, re.IGNORECASE | re.DOTALL)
        mm = pattern.finditer(arch_body)

        # keep a list of processed components.
        userDefinedComponents = list()
        libraryComponents = list()

        if mm:
            for ii in mm :
                compXml = ET.SubElement(elemXml, "component")
                comp_name = ii.groupdict()['comp_name']
                compXml.attrib['name'] = comp_name
                if instanceOf in instanceDict.keys():
                    userDefinedComponents.append(instanceOf)
                    compXml.attrib['isInstantiated'] = 'true'
                    compXml.attrib['type'] = 'user_defined'
                    for l in instanceDict[comp_name]:
                        instanceXml = ET.SubElement(compXml, "instance")
                        compXml.attrib['name'] = l
                else :
                    compXml.attrib['isInstantiated'] = 'false'

        for comp in instanceDict:
            if comp not in userDefinedComponents:
                # This most likely to be imported from other library.
                compXml = ET.SubElement(elemXml, "component")
                compXml.attrib['isInstantiated'] = 'true'
                compXml.attrib['type'] = 'library_defined'
                for l in instanceDict[comp]:
                    instanceXml = ET.SubElement(compXml, "instance")
                    compXml.attrib['name'] = l


    def parsePortText(self, elemXml, portText) :
      '''
      Parse the port-text and add them to xml.
      '''
      pattern = re.compile(r'port\s*\((?P<port_body>.*)\s*\)\s*;'
          , re.IGNORECASE | re.DOTALL)
      m = pattern.match(portText)
      if m :
        ports = m.groupdict()['port_body']
        ports = ports.split(";")
        for portDecl in ports :
          portList, typeAndDir = portDecl.split(":")
          portList = portList.strip().split(",")
          for port in portList :
            portXml = ET.SubElement(elemXml, "port")
            portXml.text = port.strip()
            dirTypeExp = re.compile(r'(?P<dir>\w+)\s+(?P<type>.+)\s*'
                , re.IGNORECASE | re.DOTALL)
            dirTypeM = dirTypeExp.match(typeAndDir.strip())
            dirTypeDict = dirTypeM.groupdict()
            dir = dirTypeDict['dir']
            type = dirTypeDict['type']
            portXml.attrib['direction'] = dir
            portXml.attrib['type'] = type
      else :
          print("[ERROR] Empty port list")
          return

    def toVHDLXML(self, elemXml, files) :
        ''' Process all files to get the heirarchy of design.
        '''
        for file in files:
            with open(file, "r") as f:
                txt = ""
                for line in f:
                    if(line.strip()[0:2] == "--") : pass 
                    else: txt += line
                assert len(txt) > 3, "File contains: {0}".format(txt)
                debug.printDebug("INFO", "Parsing file : {0}".format(file))
                self.parseTxt(txt, file)
        return elemXml
       
    def generateTestBench(self, entity, tbName) :
        ''' Add a test-bench 
        tbName : file name of tb
        '''
        tDict = dict()        # To keep the data to create testbench.
        tDict['comp_name'] = entity
        topDir = self.vhdlXml.attrib['dir']
        # Delete previous testbench 
        tbPath = topDir+tbName
        tDict['vector_file_path'] = topDir+"/work/vector.test"
        try :
            os.remove(tbPath)
        except OSError, e: 
            if e.errno != errno.ENOENT:
                raise
        # Fill in testbench
        tDict['comp_decl'] = ""
        ports = self.vhdlXml.findall(".//entity[@name='{0}']/port".format(entity))
        for p in ports:
            tDict['comp_decl'] += ("\t\t"+p.text+ " : "+p.attrib['direction']+ " "
                    + p.attrib['type']+";\n")
        
        # Signal declarations.
        tDict['signal_decl'] = ''
        for p in ports :
            tDict['signal_decl'] += ("\tSIGNAL "+p.text+" : "
                + " "+p.attrib['type']+";\n")
          
        dut = "\tdut : {0} PORT MAP( \n".format(entity)
        for p in ports :
          dut += "\t\t{0} => {0},\n".format(p.text)

        dut = dut[0:-2]+");"
        tDict['dut_instance'] = dut
        
        # variables.
        variables = ""
        for p in ports :
            portExpr = "tmp_"+p.text+" : "+" "+p.attrib['type']
            variables += "\t\tVARIABLE "+ portExpr +";\n"
        tDict['variables'] = variables
        
        # Generate assert lines
        tDict['asserts'] = self.generateAssertLines(ports)
        
        # Create a testbench
        t = self.testbenchFromDict(tDict)
        try:
            with open(tbPath, "w") as f :
                f.write(t)
        except Exception as e:
            raise IOError, "Failed to write testbench", e
        return tbName


    def generateAssertLines(self, ports ):
        assertLine = ""
        for p in ports :
            port = p.text
            assertLine += "\n\t\t\t-- read {0} value\n".format(port)
            assertLine += "\t\t\tread(l, {0}, good_val);\n".format("tmp_"+port)
            assertLine += '\t\t\tassert good_val REPORT "bad {0} value";\n'.format(port)
            if p.attrib['direction'] == "out" :
                # Out port. Assert the value.
                line = "\t\t\tassert {0} = {1} REPORT \"vector mismatch\";"\
                        .format("tmp_" + port, port)
                assertLine += line
            assertLine += '\t\t\tread(l, space); -- skip a space\n'

        assertLine += "\n\n\t\t\t-- Assign temp signals to ports \n" 
        for p in ports:
            port = p.text
            assertLine += "\t\t\t{0} <= {1};\n".format(port, "tmp_"+port)
        return assertLine

    def parseFiles(self, files):
        ''' Process the all file listings. 
        '''
        currentTime = time.strftime('%Y-%m-%d %H-%M')
        self.vhdlXml.attrib['langauge'] ="vhdl"
        self.vhdlXml.attrib['timestamp'] = currentTime
        self.vhdlXml.attrib['dir'] = self.topdir
        return self.toVHDLXML(self.vhdlXml, files)
