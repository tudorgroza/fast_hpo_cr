import json

from FastHPOCR.util import ContentUtil
from FastHPOCR.util.CRConstants import NULL


class CRIndexKB:
    clusters = {}
    invertedClusters = {}
    hpoIndex = {}

    uriBasedIndex = {}
    uriCategories = {}
    clusterSetBasedIndex = {}
    catDictionary = {}

    def __init__(self):
        self.clusters = {}
        self.invertedClusters = {}
        self.catDictionary = {}
        self.uriCategories = {}

        self.hpoIndex = []
        self.uriBasedIndex = {}
        self.clusterSetBasedIndex = {}

    def addToInvertedClusters(self, token, clusterId):
        self.invertedClusters[token] = clusterId

    def prepareClustersToSerialise(self, baseClusters):
        for el in self.invertedClusters:
            clusterId = self.invertedClusters[el]
            self.clusters[clusterId] = [el]

        for clusterId in self.clusters:
            actualList = self.compileClusterList(clusterId, baseClusters)
            for el in self.clusters[clusterId]:
                if not el in actualList:
                    actualList.append(el)
            self.clusters[clusterId] = actualList

    def compileClusterList(self, clusterId, baseClusters):
        tokenList = []
        for token in baseClusters:
            if baseClusters[token] == clusterId:
                tokenList.append(token)
        return tokenList

    def setHPOIndex(self, termsToIndex):
        for uri in termsToIndex:
            entry = {
                'uri': uri,
                'labels': termsToIndex[uri]['labels']
            }
            if 'categories' in termsToIndex[uri]:
                entry['categories'] = termsToIndex[uri]['categories']
            self.hpoIndex.append(entry)

    def setCatDictionary(self, catDictionary):
        self.catDictionary = catDictionary

    def load(self, crIndexKBFile):
        with open(crIndexKBFile, 'r') as fh:
            crData = json.load(fh)

        self.clusters = crData['clusters']
        for clusterId in self.clusters:
            for entry in self.clusters[clusterId]:
                self.invertedClusters[entry] = clusterId

        self.hpoIndex = crData['termData']
        if 'catDictionary' in crData:
            self.catDictionary = crData['catDictionary']
        self.restructureHPOIndex()

    def restructureHPOIndex(self):
        for term in self.hpoIndex:
            uri = term['uri']
            labels = term['labels']

            clusterData = {}
            for label in labels:
                clusterSig = ContentUtil.clusterSignature(label['tokenSet'])
                length = label['length']

                clusterLenData = {}
                if clusterSig in self.clusterSetBasedIndex:
                    clusterLenData = self.clusterSetBasedIndex[clusterSig]

                lenLst = []
                if length in clusterLenData:
                    lenLst = clusterLenData[length]
                if not uri in lenLst:
                    lenLst.append(uri)
                clusterLenData[length] = lenLst
                self.clusterSetBasedIndex[clusterSig] = clusterLenData

                lst = []
                if clusterSig in clusterData:
                    lst = clusterData[clusterSig]
                lst.append(label)
                clusterData[clusterSig] = lst
            self.uriBasedIndex[uri] = clusterData
            if 'categories' in term:
                self.uriCategories[uri] = term['categories']

    def getClusterBasedTerms(self, clusterSig):
        if clusterSig in self.clusterSetBasedIndex:
            return self.clusterSetBasedIndex[clusterSig]
        return None

    def getLabelsForUri(self, uri, clusterSig):
        return self.uriBasedIndex[uri][clusterSig]

    def getCategoriesForUri(self, uri):
        if not self.catDictionary:
            return []

        if not uri in self.uriCategories:
            return []

        result = []
        for cat in self.uriCategories[uri]:
            result.append({
                'uri': cat,
                'label': self.catDictionary[cat]
            })
        return result

    def serialize(self, fileOut, baseClusters):
        self.prepareClustersToSerialise(baseClusters)

        data = {
            'termData': self.hpoIndex,
            'clusters': self.clusters
        }
        if self.catDictionary:
            data['catDictionary'] = self.catDictionary

        with open(fileOut, 'w') as fh:
            json.dump(data, fh, sort_keys=True, indent=4)

    def getClusterId(self, token):
        if token in self.invertedClusters:
            return self.invertedClusters[token]
        return NULL
