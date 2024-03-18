from FastHPOCR.util.CRConstants import PHENOTYPIC_ABNORMALITY


class LabelProcessor:
    ontoReader = None
    terms = {}
    labels = {}
    dupLabels = {}

    def __init__(self, ontoReader):
        self.ontoReader = ontoReader
        self.terms = {}
        self.labels = {}
        self.dupLabels = {}

        print(' - Processing labels ...')
        self.collectTerms()
        self.processBracketsInLabels()
        print(' - Collected {} terms.'.format(len(self.terms)))
        print(' - Found {} duplicated labels.'.format(len(self.dupLabels)))
        for label in self.dupLabels:
            print(' -- {} -> {}'.format(label, self.dupLabels[label]))
        self.processDuplicates()

    def collectTerms(self):
        for uri in self.ontoReader.terms:
            if PHENOTYPIC_ABNORMALITY in self.ontoReader.allSuperClasses[uri]:
                label = self.ontoReader.terms[uri]
                syns = []
                if uri in self.ontoReader.synonyms:
                    for syn in self.ontoReader.synonyms[uri]:
                        if len(syn) < 4 and syn.isupper():
                            continue
                        syns.append(syn)
                self.terms[uri] = {
                    'label': label,
                    'syns': syns
                }

    def processBracketsInLabels(self):
        for uri in self.terms:
            label = self.terms[uri]['label']
            syns = self.terms[uri]['syns']

            newSyns = []
            if '(' in label:
                label = self.processBrackets(label)
            for syn in syns:
                procced = self.processBrackets(syn, isSyn=True)
                if procced:
                    if len(syn) < 4 and syn.isupper():
                        continue
                    newSyns.append(syn)

            self.terms[uri] = {
                'label': label,
                'syns': newSyns
            }

            if not label in self.labels:
                self.labels[label] = uri
            else:
                existUri = self.labels[label]
                self.labels.pop(label)

                lst = []
                if label in self.dupLabels:
                    lst = self.dupLabels[label]
                if not existUri in lst:
                    lst.append(existUri)
                if not uri in lst:
                    lst.append(uri)
                self.dupLabels[label] = lst

    def processBrackets(self, label, isSyn=False):
        woB = label
        idx = woB.find('(')
        while idx != -1:
            idx2 = woB.find(')')
            inside = woB[idx + 1: idx2]
            if inside.isupper():
                if len(inside) == 1:
                    woB = woB[0: idx] + inside + woB[idx2 + 1:]
                else:
                    woB = woB[0: idx] + woB[idx2 + 1:].strip()
            else:
                if isSyn:
                    return None
                woB = woB[0: idx] + inside + woB[idx2 + 1:]
            idx = woB.find('(')
        return woB

    def processDuplicates(self):
        for uri in self.terms:
            label = self.terms[uri]['label']
            syns = self.terms[uri]['syns']

            newSyns = []
            for syn in syns:
                if not syn in self.labels:
                    newSyns.append(syn)

            self.terms[uri] = {
                'label': label,
                'syns': newSyns
            }

        for label in self.dupLabels:
            uris = self.dupLabels[label]
            toRemove = []
            for uri in uris:
                syns = self.terms[uri]['syns']
                if syns:
                    newSyns = syns.copy()
                    newLabel = syns[0]
                    newSyns.remove(newLabel)
                    self.terms[uri] = {
                        'label': newLabel,
                        'syns': newSyns
                    }
                else:
                    toRemove.append(uri)
            for uri in toRemove:
                self.terms.pop(uri)

    def getProcessedTerms(self):
        return self.terms
