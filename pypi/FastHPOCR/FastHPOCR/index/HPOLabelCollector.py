from FastHPOCR.util import ConfigConstants
from FastHPOCR.util.CRConstants import PHENOTYPIC_ABNORMALITY


class HPOLabelCollector:
    terms = {}
    rootConcepts = []
    externalSynonyms = {}
    allow3LetterAcronyms = False
    includeTopLevelCategory = False

    def __init__(self, ontoReader, externalSynonyms={}, indexConfig={}):
        self.terms = {}
        self.externalSynonyms = externalSynonyms
        self.processConfig(indexConfig)
        self.collectTerms(ontoReader)

    def processConfig(self, indexConfig):
        if not indexConfig:
            self.rootConcepts = []
            self.allow3LetterAcronyms = False
            self.includeTopLevelCategory = False
            return

        if ConfigConstants.VAR_ROOT_CONCEPTS in indexConfig:
            self.rootConcepts = indexConfig[ConfigConstants.VAR_ROOT_CONCEPTS]
        if ConfigConstants.VAR_3LETTER_ACRONYMS in indexConfig:
            self.allow3LetterAcronyms = indexConfig[ConfigConstants.VAR_3LETTER_ACRONYMS]
        if ConfigConstants.VAR_INCLUDE_CATEGORY in indexConfig:
            self.includeTopLevelCategory = indexConfig[ConfigConstants.VAR_INCLUDE_CATEGORY]

    def collectTerms(self, ontoReader):
        for uri in ontoReader.terms:
            if PHENOTYPIC_ABNORMALITY in ontoReader.allSuperClasses[uri]:
                if self.rootConcepts:
                    found = False
                    for ancestor in self.rootConcepts:
                        if ancestor in ontoReader.allSuperClasses[uri]:
                            found = True
                            break
                    if not found:
                        continue

                label = ontoReader.terms[uri]
                syns = []
                if uri in self.externalSynonyms:
                    syns.extend(self.externalSynonyms[uri])

                if uri in ontoReader.synonyms:
                    for syn in ontoReader.synonyms[uri]:
                        if syn in syns:
                            continue
                        size = 4
                        if self.allow3LetterAcronyms:
                            size = 3

                        if len(syn) < size and syn.isupper():
                            continue
                        syns.append(syn)
                entry = {
                    'label': label,
                    'syns': syns
                }
                if self.includeTopLevelCategory:
                    entry['categories'] = self.findCategories(uri, ontoReader)
                self.terms[uri] = entry

    def findCategories(self, uri, ontoReader):
        categories = []
        for cat in ontoReader.abn_classes:
            if cat in ontoReader.allSuperClasses[uri] or cat == uri:
                categories.append(cat)
        return categories

    def getTerms(self):
        return self.terms
