from FastHPOCR.util.CRConstants import SCTID_PREFIX

SPECIAL_TOKENS = ['in situ', 'present']


class SNOMEDLabelCollector:
    terms = {}

    def __init__(self, snomedData):
        self.terms = {}
        self.collectTerms(snomedData)

    def collectTerms(self, snomedData):
        for uri in snomedData:
            uriData = snomedData[uri]
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
            for lbl in uriData['label']:
                if lbl == label:
                    continue
                syn = self.processSpecial(lbl)
                if len(syn) < 4 and syn.isupper():
                    continue
                if syn == label:
                    continue
                if syn in syns:
                    continue
                syns.append(syn)

            self.terms[SCTID_PREFIX + uri] = {
                'label': label,
                'syns': syns
            }

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
