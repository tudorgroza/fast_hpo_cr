from util.CRConstants import PHENOTYPIC_ABNORMALITY


class HPOLabelCollector:
    terms = {}
    allow3LetterAcronyms = False
    externalSynonyms = {}
    rootConcepts = []

    def __init__(self, ontoReader, rootConcepts=[], externalSynonyms={}, allow3LetterAcronyms=False):
        self.terms = {}
        self.externalSynonyms = externalSynonyms
        self.allow3LetterAcronyms = allow3LetterAcronyms
        self.rootConcepts = rootConcepts
        self.collectTerms(ontoReader)

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

                        if len(syn) < size:
                            continue
                        syns.append(syn)
                self.terms[uri] = {
                    'label': label,
                    'syns': syns
                }

    def getTerms(self):
        return self.terms
