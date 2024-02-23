from index.LabelProcessor import LabelProcessor
from util import ContentUtil
from util.CRConstants import NULL, POS_CD, POS_NN, WHITE_LIST, VB_BLACKLIST, POS_FILTER
from util.OntoReader import OntoReader


class PreprocessOntologyTerms:
    ontoReader = None
    processedTerms = {}
    posKB = {}
    terms = {}

    def __init__(self, ontologyFile, posKB):
        self.ontoReader = OntoReader(ontologyFile)
        self.processedTerms = {}
        self.posKB = posKB

        # TODO: Do proper processing of the terms

        labelProcessor = LabelProcessor(self.ontoReader)
        self.terms = labelProcessor.getProcessedTerms()

        self.filterByPOS()

    def filterByPOS(self):
        for uri in self.terms:
            label = self.terms[uri]['label']
            syns = self.terms[uri]['syns']
            termLst = []

            tokenSet = self.processTerm(self.processLabel(label))
            filteredTokenSet = self.filter(tokenSet)
            termLst.append({
                'originalLabel': label,
                'preferredLabel': True,
                'tokens': filteredTokenSet
            })

            for syn in syns:
                tokenSet = self.processTerm(self.processLabel(syn))
                filteredTokenSet = self.filter(tokenSet)
                termLst.append({
                    'originalLabel': syn,
                    'preferredLabel': False,
                    'tokens': filteredTokenSet
                })
            self.processedTerms[uri] = termLst

    def processLabel(self, label) -> str:
        label = label.lower()
        label = ContentUtil.spaceReplace(label)
        label = ContentUtil.cleanToken(label)
        label = label.replace('  ', ' ')
        return label.strip()

    def processTerm(self, label):
        segments = label.split(' ')
        result = []
        for segment in segments:
            shape = ContentUtil.wordShape(segment)
            pos = NULL
            if shape == 'd':
                pos = POS_CD
            if shape == 'm':
                pos = POS_NN
            if shape == 'a':
                if segment in self.posKB:
                    pos = self.posKB[segment]
                else:
                    pos = POS_NN
            result.append({
                'token': segment,
                'pos': pos
            })

        return result

    def filter(self, tokenSet):
        result = []
        for token in tokenSet:
            if token['token'] in WHITE_LIST:
                result.append(token)
                continue
            if token['token'] in VB_BLACKLIST:
                continue
            tokenPos = token['pos']
            if tokenPos in POS_FILTER:
                continue
            result.append(token)
        return result

    def getProcessedTerms(self):
        return self.processedTerms
