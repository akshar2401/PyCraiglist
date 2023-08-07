from EntityToExtract import ExtractionOptions, EntityToExtract
from CraiglistSites import LocationType, CraiglistNode, CraiglistSites
import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor

class CraiglistAreas(EntityToExtract):
    MAX_THREADS = 25000
    def __init__(self, rootCraiglistNode: CraiglistNode):
        super().__init__(ExtractionOptions(None))
        self.rootNode = rootCraiglistNode

    async def __extract(self):
        sites = self.rootNode.allCraiglists()
        def extractInfos(session, site):
            options = ExtractionOptions(site.url, session = session)

            if site.url:
                try:
                    siteInfo = self.extractInformation(options)
                    subLinks = siteInfo.find('ul', class_ = "sublinks")
                    if subLinks:
                        for sublink in subLinks.find_all('a'):
                            url = site.url + sublink['href']
                            friendlyName = sublink['title']
                            name = sublink.get_text()
                            craiglistArea = CraiglistNode(name, False, url, [LocationType.Area], friendlyName)
                            site.children.append(craiglistArea)
                except: 
                    pass
        workers = min(CraiglistAreas.MAX_THREADS,len(sites))
        with ThreadPoolExecutor(max_workers=workers) as executor:
            with requests.Session() as session:
                loop = asyncio.get_event_loop() 
                tasks = [loop.run_in_executor(executor, extractInfos, *(session, site)) for site in sites]
                for _ in await asyncio.gather(*tasks):
                    pass
    def extract(self):
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(self.__extract())
        loop.run_until_complete(future)

        
    @classmethod
    def getAreas(cls, rootNode: CraiglistNode):
        CraiglistAreas(rootNode).extract()
