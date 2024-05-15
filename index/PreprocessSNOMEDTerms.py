from index.LabelProcessor import LabelProcessor
from index.SNOMEDLabelCollector import SNOMEDLabelCollector
from util import ContentUtil
from util.CRConstants import VB_BLACKLIST, POS_LIST


class PreprocessSNOMEDTerms:
    processedTerms = {}

    def __init__(self, jsonData):
        self.processedTerms = {}
        labelProcessor = LabelProcessor(SNOMEDLabelCollector(jsonData).getTerms())
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