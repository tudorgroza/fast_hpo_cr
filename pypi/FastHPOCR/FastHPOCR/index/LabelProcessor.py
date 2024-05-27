from FastHPOCR.util import ConfigConstants


class LabelProcessor:
    terms = {}
    labels = {}
    dupLabels = {}
    allow3LetterAcronyms = False
    allowDuplicateEntries = False

    def __init__(self, terms, indexConfig={}):
        self.terms = terms
        self.labels = {}
        self.dupLabels = {}
        self.processConfig(indexConfig)

        print(' - Processing labels ...')
        self.processBracketsInLabels()
        print(' - Collected {} terms.'.format(len(self.terms)))
        print(' - Found {} duplicated labels.'.format(len(self.dupLabels)))
        for label in self.dupLabels:
            print(' -- {} -> {}'.format(label, self.dupLabels[label]))
        if not self.allowDuplicateEntries:
            self.processDuplicates()

    def processConfig(self, indexConfig):
        if not indexConfig:
            self.allow3LetterAcronyms = False
            self.allowDuplicateEntries = False
            return

        if ConfigConstants.VAR_3LETTER_ACRONYMS in indexConfig:
            self.allow3LetterAcronyms = indexConfig[ConfigConstants.VAR_3LETTER_ACRONYMS]
        if ConfigConstants.VAR_ALLOW_DUPLICATE_ENTRIES in indexConfig:
            self.allowDuplicateEntries = indexConfig[ConfigConstants.VAR_ALLOW_DUPLICATE_ENTRIES]

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
                    size = 4
                    if self.allow3LetterAcronyms:
                        size = 3

                    if len(syn) < size and syn.isupper():
                        continue
                    newSyns.append(syn)

            entry = {
                'label': label,
                'syns': newSyns
            }
            if 'categories' in self.terms[uri]:
                entry['categories'] = self.terms[uri]['categories']
            self.terms[uri] = entry

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
            entry = {
                'label': label,
                'syns': newSyns
            }
            if 'categories' in self.terms[uri]:
                entry['categories'] = self.terms[uri]['categories']
            self.terms[uri] = entry

        for label in self.dupLabels:
            uris = self.dupLabels[label]
            toRemove = []
            for uri in uris:
                syns = self.terms[uri]['syns']
                if syns:
                    newSyns = syns.copy()
                    newLabel = syns[0]
                    newSyns.remove(newLabel)
                    entry = {
                        'label': newLabel,
                        'syns': newSyns
                    }
                    if 'categories' in self.terms[uri]:
                        entry['categories'] = self.terms[uri]['categories']
                    self.terms[uri] = entry
                else:
                    toRemove.append(uri)
            for uri in toRemove:
                self.terms.pop(uri)

    def getProcessedTerms(self):
        return self.terms
