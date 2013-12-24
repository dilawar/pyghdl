import time
import sys
import re
import os
import errno
import shlex
import subprocess
import xml.etree.cElementTree as ET
import errno
import debug.debug as debug
import collections
import tb_generator as tb


class VHDLParser(tb.TestBench):

    def __init__(self, topdir=""):
        self.tb = ""
        self.topdir = topdir
        self.workdir = os.path.join(self.topdir, 'work')
        self.vhdlXml = ET.Element("design")
        
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
            genericPattern = re.compile(
                    r'generic\s*\((?P<list>((?!port).)+)\s*\)\s*;'
                , re.IGNORECASE | re.DOTALL)
            genericMatch = genericPattern.finditer(body) 
            for gi in genericMatch :
                genericText = gi.group('list')
                genericXml = ET.SubElement(entityXml, "generics")
                genericXml.text = genericText
                generics = genericText.split(';')
                for g in generics:
                    g = g.strip()
                    genXml = ET.SubElement(genericXml, "generic")
                    m = re.search(r'(?P<name>\w+)\s*\:\s*', g)
                    genXml.attrib['lhs'] = m.group('name')
                    g = g.replace(m.group(0), '')
                    genXml.attrib['rhs'] = g

            # ports 
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
                        compXml.attrib['instance_of'] = instanceOf
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
                    compXml.attrib['instance_of'] = instanceOf


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
              portList, typeAndDir = portDecl.split(":", 1)
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
                    else: 
                        # Remove the comme\nts from the end of line
                        line = re.sub(r'\-\-.*', '', line)
                        txt += line
                assert len(txt) > 3, "File contains: {0}".format(txt)
                debug.printDebug("INFO", "Parsing file : {0}".format(file))
                self.parseTxt(txt, file)
        return elemXml
       
    def parseFiles(self, files):
        ''' Process the all file listings. 
        '''
        currentTime = time.strftime('%Y-%m-%d %H-%M')
        self.vhdlXml.attrib['langauge'] ="vhdl"
        self.vhdlXml.attrib['timestamp'] = currentTime
        self.vhdlXml.attrib['dir'] = self.topdir
        return self.toVHDLXML(self.vhdlXml, files)

    def formatGenericText(self, genericXml):
        """Given generic xml, for a generic list for component
        """
        newText = []
        for gen in genericXml:
            txt = gen.attrib['lhs']
            if ":=" in gen.attrib['rhs']:
                txt += ' => ' + gen.attrib['rhs'].split(":=")[-1]
            newText.append(txt)
        return ",\n\t\t".join(newText)
    
    def formatPortText(self, ports):
        newText = set()
        for p in ports:
            p = p.text
            p = p.strip()
            if p: newText.add("{0} => {0}".format(p))
            else: pass
        return ',\n\t\t'.join(newText)


    def populateGenericDict(self, genXml, entityName):
        """Create generic for this entity
        """
        generics = dict()
        for xml in genXml:
            rhs = xml.attrib['rhs']
            lhs = xml.attrib['lhs']
            if ":=" in rhs:
                generics[lhs] = rhs.split(":=")[-1]
            else:
                generics[lhs] = None
        self.genericsDict[entityName] = generics
        return generics 
    
    def replaceGenericWithValue(self, txt, genericDict, entity):
        for k in genericDict:
            if k in txt:
                if genericDict[k] is None:
                    msg = "Can't find the value for generic {0}.".format(k)
                    msg += " Can't produce a testbench. Initialize generics"
                    msg += " in entity with some default values. "
                    msg += " In entity %s" % entity
                    debug.printDebug("ERR", msg)
                    sys.exit()
                else:
                    txt = txt.replace(k, genericDict[k])
            else: pass
        return txt

