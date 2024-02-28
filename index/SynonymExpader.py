class SynonymExpader:
    expandedTerms = None
    synClusters = None

    def __init__(self, termsToIndex, voidTokens, synClusters):
        self.expandedTerms = {}
        self.synClusters = synClusters

        for uri in termsToIndex:
            newLabelList = self.augment(termsToIndex[uri], voidTokens)
            self.expand(uri, newLabelList)

    def augment(self, labelList, voidTokens):
        newList = []
        for label in labelList:
            newList.append(label)
            clusterSet = label['tokenSet']
            for clusterId in clusterSet:
                if clusterId in voidTokens:
                    clusterIdsCopy = label['tokens'].copy()
                    clusterIdsCopy.remove(clusterId)
                    clusterSet = list(set(clusterIdsCopy))
                    newList.append({
                        'originalLabel': label['originalLabel'],
                        'length': len(clusterIdsCopy),
                        'setLength': len(clusterSet),
                        'tokens': clusterIdsCopy,
                        'tokenSet': clusterSet,
                        'native': False
                    })

        return newList

    def expand(self, uri, labelList):
        newLabelList = []
        for label in labelList:
            newLabelList.append(label)
            clusterSet = label['tokenSet']
            for clusterId in clusterSet:
                if clusterId in self.synClusters:
                    newLabels = self.generate(label, clusterId, self.synClusters[clusterId])
                    newLabelList.extend(newLabels)
        self.expandedTerms[uri] = newLabelList

    def generate(self, label, clusterId, synClusterSet):
        labelSet = []

        for syn in synClusterSet:
            if syn == clusterId:
                continue
            clusterIdsCopy = label['tokens'].copy()
            idxList = []
            for i in range(0, len(clusterIdsCopy)):
                if clusterIdsCopy[i] == clusterId:
                    idxList.append(i)
            for i in idxList:
                clusterIdsCopy[i] = syn

            clusterSet = list(set(clusterIdsCopy))
            labelSet.append({
                'originalLabel': label['originalLabel'],
                'length': len(clusterIdsCopy),
                'setLength': len(clusterSet),
                'tokens': clusterIdsCopy,
                'tokenSet': clusterSet,
                'native': False
            })
        return labelSet

    def getTermsToIndex(self):
        return self.expandedTerms
