from FastHPOCR.util.CRConstants import VOID_TOKENS


class IndexTerms:
    termsToIndex = {}
    processedTerms = {}
    baseClusters = {}

    finalClusterElements = {}
    finalClusters = {}
    crIndexKB = None

    newClusterCount = 1000000
    newClusterData = {}

    def __init__(self, processedTerms, baseClusters, crIndexKB):
        self.baseClusters = baseClusters
        self.processedTerms = processedTerms
        self.crIndexKB = crIndexKB

        self.finalClusterElements = {}
        self.finalClusters = {}
        self.termsToIndex = {}
        self.newClusterData = {}

        self.indexTerms()

    def indexTerms(self):
        for uri in self.processedTerms:
            labelSet = self.processedTerms[uri]

            readyLabels = []
            for label in labelSet:
                readyLabels.append(self.prepareLabel(label))
            self.termsToIndex[uri] = readyLabels

    def prepareLabel(self, label):
        clusterIds = []

        for el in label['tokens']:
            if el['token'] in self.baseClusters:
                clusterId = self.baseClusters[el['token']]
            else:
                if el['token'] in self.newClusterData:
                    clusterId = self.newClusterData[el['token']]
                else:
                    clusterId = 'C' + str(self.newClusterCount)
                    self.newClusterCount += 1
                    self.newClusterData[el['token']] = clusterId

            clusterIds.append(clusterId)
            self.crIndexKB.addToInvertedClusters(el['token'], clusterId)

        clusterSet = list(set(clusterIds))
        return {
            'originalLabel': label['originalLabel'],
            'length': len(clusterIds),
            'setLength': len(clusterSet),
            'tokens': clusterIds,
            'tokenSet': clusterSet,
            'native': True
        }

    def getTermsToIndex(self):
        return self.termsToIndex

    def getVoidTokens(self):
        voidTokens = []
        for token in VOID_TOKENS:
            if token in self.baseClusters:
                voidTokens.append(self.baseClusters[token])
            if token in self.newClusterData:
                voidTokens.append(self.newClusterData[token])
        return voidTokens

    def getNewClusterData(self):
        return self.newClusterData
