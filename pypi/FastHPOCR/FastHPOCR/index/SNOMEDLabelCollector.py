from FastHPOCR.util import ConfigConstants
from FastHPOCR.util.CRConstants import SCTID_PREFIX

SPECIAL_TOKENS = ['in situ', 'present']


class SNOMEDLabelCollector:
    terms = {}
    externalSynonyms = {}
    allow3LetterAcronyms = False

    def __init__(self, snomedData, externalSynonyms={}, indexConfig={}):
        self.terms = {}
        self.externalSynonyms = externalSynonyms

        if ConfigConstants.VAR_3LETTER_ACRONYMS in indexConfig:
            self.allow3LetterAcronyms = indexConfig[ConfigConstants.VAR_3LETTER_ACRONYMS]

        self.collectTerms(snomedData)

    def collectTerms(self, snomedData):
        for uri in snomedData:
            uriData = snomedData[uri]
            categories = []
            if 'categories' in uriData:
                categories = uriData['categories']

            label = ''
            for lbl in uriData['label']:
                if not '(' in lbl and not ',' in lbl:
                    label = lbl
                    break
            if not label:
                for lbl in uriData['label']:
                    if not '(' in lbl:
                        label = lbl
                        break
            if not label:
                continue

            syns = []
            if uri in self.externalSynonyms:
                syns.extend(self.externalSynonyms[uri])

            for lbl in uriData['label']:
                if lbl == label:
                    continue
                syn = self.processSpecial(lbl)
                size = 4
                if self.allow3LetterAcronyms:
                    size = 3

                if len(syn) < size and syn.isupper():
                    continue
                if syn == label:
                    continue
                if syn in syns:
                    continue
                syns.append(syn)

            entry = {
                'label': label,
                'syns': syns
            }
            if categories:
                entry['categories'] = categories

            self.terms[SCTID_PREFIX + uri] = entry

    def processSpecial(self, lbl):
        tmp = lbl
        if tmp.endswith(')'):
            idx = tmp.rfind('(')
            tmp = tmp[0: idx].strip()
        tmp = tmp.replace('{', '')
        tmp = tmp.replace('}', '')
        for token in SPECIAL_TOKENS:
            if tmp.endswith(token):
                tmp = tmp.replace(token, '').strip()
        return tmp

    def getTerms(self):
        return self.terms
