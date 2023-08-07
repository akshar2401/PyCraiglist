from EntityToExtract import ExtractionOptions, EntityToExtract
from ResultsSet import ResultsSet
from collections import deque
class LocationType:
    Country = "Country"
    State = "State"
    Province = "Province"
    Region = "Region"
    Craiglist = "Craiglist"
    Area = "Area"
    LocationTypes = [Country, State, Province, Region, Craiglist, Area]
    Plurals = {"Countries": Country, "States": State, "Provinces": Province, "Regions": Region, "Craiglists":Craiglist, "Areas": Area}

class CraiglistNode:
    def __init__(self, name: str, isCraiglist: bool, url: str, locationTypes: list, friendlyName: str = ""):
        self.name = name
        self.isCraiglist = isCraiglist
        self.url = url
        self.locationTypes = locationTypes if locationTypes is not None else list()
        self.friendlyName = friendlyName
        self.children = list()
        self.__attrsList = ['name', 'isCraiglist', 'url', 'locationsTypes', 'friendlyName', 'children']

    def find(self, func):
        results = ResultsSet()
        self.__recursiveFilter(self, results, func, stopFirst=True)
        return results.first()

    def filter(self, func) -> ResultsSet:
        results = ResultsSet()
        self.__recursiveFilter(self, results, func)
        return results
        
    def __recursiveFilter(self, craiglistNode, results: ResultsSet, filterFunc, stopFirst = False):
        queue = deque([craiglistNode])
        while queue:
            top = queue.popleft()
            if filterFunc(top):
                results.add(top)
            if stopFirst and results.any():
                break
            for childNode in top.children:
                queue.append(childNode)

    def __iter__(self):
        queue = deque([self])
        while queue:
            top = queue.popleft()
            yield top
            for childNode in top.children:
                queue.append(childNode)

    def allCraiglists(self) -> ResultsSet:
        return self.filter(lambda node: node.isCraiglist)
    
    def getLocation(self, location):
        return self.find(lambda node: location.lower() in node.name.lower() or location.lower() in node.friendlyName.lower())
    

    def getNodesBasedOnLocTypes(self, locationType: str) -> ResultsSet:
        return self.filter(lambda node: locationType in node.locationTypes)

    def getNodeBasedOnLocTypes(self, locationType: str):
        return self.find(lambda node: locationType in node.locationTypes)

    def __str__(self):
        return "{} (isCraigList: {}, url: {}, locationTypes: {})".format(self.name, self.isCraiglist, self.url, self.locationTypes)
    def print(self):
        header= str(self)
        print(header)
        for child in self.children:
            print("    ", end = "")
            child.print()
    def __getitem__(self, name):
        if isinstance(name, int):
            iterator = self.__iter__()
            for _ in range(name-1):
                next(iterator, None)
            return next(iterator, None)

        if isinstance(name, str):
            if name.lower() == "craiglists":
                return self.allCraiglists()
            elif name in LocationType.LocationTypes:
                return self.getNodeBasedOnLocTypes(name)
            elif name in LocationType.Plurals:
                return self.getNodesBasedOnLocTypes(LocationType.Plurals[name])
            else: return self.getLocation(name)
    def __call__(self, filter, infer = True):
        if callable(filter): 
            results = self.filter(filter)
            if infer and len(results) == 1:
                return next(iter(results))
            return results
        backupResult = self.__getitem__(filter)
        return backupResult

    def __getattr__(self, name):
        return self.__getitem__(name)
        

class CraiglistSites(EntityToExtract):
    __instance = None
    def __init__(self):
        extractionOptions = ExtractionOptions(url = "https://www.craigslist.org/about/sites")
        super().__init__(extractionOptions)
        self.extractedSites = None
    def extract(self):
        craiglistSites = super().extractInformation()
        craigList = CraiglistNode("ALL", False, None, [], "All Craiglists")
        columns = craiglistSites.find_all('div', class_ = "colmask")
        for column in columns:
            regionHeader = column.find_previous_sibling()
            region = regionHeader.find('a')
            craiglistRegion = CraiglistNode(
                                region['name'], 
                                False,
                                None, 
                                [LocationType.Region] + ([LocationType.Country] if region['name'].lower() in ['us', 'ca'] else []),
                                regionHeader.get_text()                              
                              )
            craigList.children.append(craiglistRegion)
            for siteSection in column.find_all('ul'):
                sectionHeader = siteSection.find_previous_sibling()
                sectionLocationType = None
                if craiglistRegion.name.lower() == 'us':
                    sectionLocationType = [LocationType.State]
                elif craiglistRegion.name.lower() == 'ca':
                    sectionLocationType = [LocationType.Province]
                else:
                    sectionLocationType = [LocationType.Country]
                craigListSection = CraiglistNode(sectionHeader.get_text(),False, None, sectionLocationType,sectionHeader.get_text())
                craiglistRegion.children.append(craigListSection)
                for site in siteSection.find_all('a'):
                    urlToCraiglist = site['href']
                    name = site['href'].split("//")[1].split(".")[0]
                    craiglist = CraiglistNode(name, True, urlToCraiglist, [LocationType.Craiglist], friendlyName = site.get_text().strip(" "))
                    craigListSection.children.append(craiglist)
        self.extractedSites = craigList
    @classmethod
    def getCraiglists(cls) -> CraiglistNode:
        if cls.__instance is None:
            cls.__instance: CraiglistSites = CraiglistSites()
            cls.__instance.extract()
        return cls.__instance.extractedSites

