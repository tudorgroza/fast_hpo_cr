from FastHPOCR.index.LabelProcessor import LabelProcessor
from FastHPOCR.util import ContentUtil
from FastHPOCR.util.CRConstants import VB_BLACKLIST, POS_LIST
from FastHPOCR.util.OntoReader import OntoReader


class PreprocessOntologyTerms:
    ontoReader = None
    processedTerms = {}
    terms = {}

    def __init__(self, ontologyFile):
        self.ontoReader = OntoReader(ontologyFile)
        self.processedTerms = {}

        labelProcessor = LabelProcessor(self.ontoReader)
        self.terms = labelProcessor.getProcessedTerms()

        self.filterTerms()

    def filterTerms(self):
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
            result.append({
                'token': segment
            })
        return result

    def filter(self, tokenSet):
        result = []
        for token in tokenSet:
            if token['token'] in VB_BLACKLIST or token['token'] in POS_LIST:
                continue
            result.append(token)
        return result

    def getProcessedTerms(self):
        return self.processedTerms
