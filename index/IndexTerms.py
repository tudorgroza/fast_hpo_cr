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
                # TODO: If not in clusters - try to align it and add it to clusters
                # TODO: In the meantine - just create a new cluster

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
            'tokenSet': clusterSet
        }

    def getTermsToIndex(self):
        return self.termsToIndex

    def getNewClusterData(self):
        return self.newClusterData