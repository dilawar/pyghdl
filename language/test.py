import re
import math
import vhdl_parser as vhdl

def testVCD(vcds) :
  pass

def getPortsOfComponent(archOfWhichEntity) :
  entityName = archOfWhichEntity.replace("tb_", "")
  ports = vhdl.vhdlXml.findall(".//entity[@name='{0}']/port"\
      .format(entityName))
  portDict = dict()
  for port in ports :
    portDict[port.text] = ( port.attrib['type'], port.attrib['direction'])
  return portDict

# if an entity named foo is being tested. This function must be named test_foo.
def testEntity(entityName, testDir) : 
  testFileName = testDir+"/work/vector.test"
  ports = getPortsOfComponent(entityName)
  supportedTypePattern = re.compile('(bit.*)|(std_logic.*)|(boolean)|(integer)|\
      (natural)|(positive)|(real)|(string)', re.IGNORECASES | re.DOTALL)
  for portName in ports :
    type, direction = ports[portName]
    if not supportedTypePattern.match(type) : 
      msg = ""
    mc.writeOnWindow(mc.dataWindow, direction+" "+type+"\n")

  with open(testFileName, "w") as testF :
    testF.write("-- Generated automatically.\n")
  return 

