from CraiglistSites import CraiglistSites
from CraiglistAreas import CraiglistAreas
root = CraiglistSites.getCraiglists()
stateOfGeorgia = root.us.georgia
print(stateOfGeorgia)
print("\n\nCraiglists in Georgia State")
for child in stateOfGeorgia:
    print(child)
atlantaCraiglist = stateOfGeorgia.atlanta
CraiglistAreas.getAreas(atlantaCraiglist)
print("\n\nAreas Within Atlanta Craiglist")
for area in atlantaCraiglist:
    print(area)