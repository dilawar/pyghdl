import math
import mycurses as mc
import vhdl as vhdl

def testVCD(vcds) :
  pass

# if an entity named foo is being tested. This function must be named test_foo.
def test_mux2(entityName, testDir) : 
  testFileName = testDir+"/work/vector.test"
  with open(testFileName, "w") as testF :
    testF.write("-- Generated automatically.\n")
  return 

