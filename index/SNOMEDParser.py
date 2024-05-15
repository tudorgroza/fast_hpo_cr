class SNOMEDParser:
    conceptDescriptions = {}
    concepts = {}
    subTree = {}

    def __init__(self, descFile, relationsFile):
        self.conceptDescriptions = {}
        self.concepts = {}
        self.subTree = {}

        self.readLabels(descFile)
        self.readRelations(relationsFile)

    def readLabels(self, descFile):
        with open(descFile, 'r') as fh:
            lines = fh.readlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith('id'):
                continue

            tabs = line.split('\t')
            if int(tabs[2]) != 1:
                continue
            if tabs[5] != 'en':
                continue
            lst = []
            if tabs[4] in self.conceptDescriptions:
                lst = self.conceptDescriptions[tabs[4]]
            lst.append(tabs[7])
            self.conceptDescriptions[tabs[4]] = lst

    def readRelations(self, relationsFile):
        with open(relationsFile, 'r') as fh:
            lines = fh.readlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith('id'):
                continue

            tabs = line.split('\t')
            if int(tabs[2]) == 0:
                continue
            sourceId = tabs[4]
            destinationId = tabs[5]

            if int(tabs[6]) == 0 and tabs[7] == '116680003':
                if destinationId in self.concepts:
                    conceptData = self.concepts[destinationId]
                    children = []
                    if 'children' in conceptData:
                        children = conceptData['children']
                    children.append(sourceId)
                    conceptData['children'] = children
                    self.concepts[destinationId] = conceptData
                else:
                    children = []
                    children.append(sourceId)
                    self.concepts[destinationId] = {
                        'uri': destinationId,
                        'label': self.conceptDescriptions[destinationId],
                        'children': children
                    }

                if not sourceId in self.concepts:
                    self.concepts[sourceId] = {
                        'uri': sourceId,
                        'label': self.conceptDescriptions[sourceId],
                        'children': []
                    }

    def trim(self, uri):
        uriData = self.concepts[uri]
        for child in uriData['children']:
            self.subTree[child] = self.concepts[child]
            self.compileChildren(child)

    def compileChildren(self, uri):
        uriData = self.concepts[uri]
        for child in uriData['children']:
            if child in self.subTree:
                continue
            self.subTree[child] = self.concepts[child]
            self.compileChildren(child)

    def getSubTree(self):
        return self.subTree
