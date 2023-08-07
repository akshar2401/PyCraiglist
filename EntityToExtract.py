import requests
from bs4 import BeautifulSoup
class ExtractionOptions:
    def __init__(self, url, session = None):
        self.url = url
        self.parser = "html.parser"
        self.session = None
class EntityToExtract(object):
    def __init__(self, extractionOptions: ExtractionOptions):
        self.extractionOptions = extractionOptions
    def extractInformation(self, options = None) -> BeautifulSoup:
        if options is None: options = self.extractionOptions
        if options.session:
            with options.session.get(options.url) as response:
                rawInfo = response.text
                return BeautifulSoup(rawInfo, options.parser)
        else:
            rawInfo = requests.get(options.url).text
            return BeautifulSoup(rawInfo, options.parser)
    def extract(self):
        pass