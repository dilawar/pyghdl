import xml.etree.cElementTree as ET
import vhdl_regex as vhdl
import mycurses as mc

hierXml = ET.Element("hier")

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
        mc.writeOnWindow(mc.dataWindow, msg)
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
          mc.writeOnWindow(mc.dataWindow, msg )
    mc.writeOnWindow(mc.dataWindow, str(entityRank))
  else :
    msg = "Empty design... Quiting."
    mc.writeOnWindow(mc.msgWindow, msg)
    return

def execute(topdir, files) :
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
  tree = ET.ElementTree(hierXml)
  tree.write("hier.xml")
