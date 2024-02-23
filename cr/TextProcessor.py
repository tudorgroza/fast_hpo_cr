from cr import CRIndexKB, SequenceCache
from cr.TextSplitter import TextSplitter
from util import ContentUtil
from util.CRConstants import NULL


class TextProcessor:
    crIndexKB = None
    sequenceCache = None

    tokens = []
    candidates = {}

    def __init__(self, crIndexKB: CRIndexKB, sequenceCache: SequenceCache):
        self.crIndexKB = crIndexKB
        self.sequenceCache = sequenceCache

        self.tokens = []
        self.candidates = {}

    def process(self, text):
        self.tokens = TextSplitter(text).getTokens()
        self.enrichTokens()
        self.generateCandidates()

    def enrichTokens(self):
        for token in self.tokens:
            clusterId = self.crIndexKB.getClusterId(token.getToken())
            token.setClusterId(clusterId)

    def generateCandidates(self):
        current = []
        for token in self.tokens:
            if token.getClusterId() == NULL:
                if current:
                    candidateSig = self.toClusterSig(current)
                    lst = []
                    if candidateSig in self.candidates:
                        lst = self.candidates[candidateSig]
                    lst.append(current)
                    self.candidates[candidateSig] = lst

                    seqMap = self.sequenceCache.getSequences(len(current))

                    for size in seqMap:
                        if size != len(current):
                            seqOptions = seqMap[size]
                            for array in seqOptions:
                                self.expandCandidates(current, array)
                    current = []
            else:
                current.append(token)

        if current:
            candidateSig = self.toClusterSig(current)
            lst = []
            if candidateSig in self.candidates:
                lst = self.candidates[candidateSig]
            lst.append(current)
            self.candidates[candidateSig] = lst

    def toClusterSig(self, candidate):
        clusterSigLst = []
        for token in candidate:
            clusterSigLst.append(token.getClusterId())
        clusterSet = list(set(clusterSigLst))
        return ContentUtil.clusterSignature(clusterSet)

    def expandCandidates(self, candidate, array):
        newCandidate = []
        for el in array:
            newCandidate.append(candidate[el - 1])

        candidateSig = self.toClusterSig(newCandidate)
        lst = []
        if candidateSig in self.candidates:
            lst = self.candidates[candidateSig]
        lst.append(newCandidate)
        self.candidates[candidateSig] = lst

    def getCandidates(self):
        return self.candidates

    def printTokens(self):
        print(' -- TOKENS --')
        print(' ------------')
        for token in self.tokens:
            print(token)

    def printCandidates(self):
        print(' -- CANDIDATES --')
        print(' ----------------')
        for candidateSig in self.candidates:
            print(' >> {}'.format(candidateSig))
            for candidate in self.candidates[candidateSig]:
                for token in candidate:
                    print('  --- ' + str(token))
                print(' <<')
