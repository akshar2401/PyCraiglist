class ResultsSet:
    def __init__(self):
        self.results = list()
    def add(self, result):
        self.results.append(result)
        
    def toDict(self, keySelector, elementSelector = lambda result: result):
        results = dict()
        for result in self.results:
            key = keySelector(result)
            element = elementSelector(result)
            results[key] = element
        return results

    def toIterable(self, key = lambda result: result):
        for result in self.results:
            yield key(result)
    def toList(self, key = lambda result: result):
        return list(self.toIterable(key))
    def first(self):
        if self.any():
            return self.results[0]
    def any(self):
        return len(self.results) > 0
    def __len__(self):
        return len(self.results)
    def __iter__(self):
        return iter(self.results)
    def __getitem__(self, index):
        return self.results[index]
    def __getattr__(self, name):

        for result in self.results:
            if hasattr(result, name):
                res = getattr(result, name)
                yield res
            else:
                yield None
        