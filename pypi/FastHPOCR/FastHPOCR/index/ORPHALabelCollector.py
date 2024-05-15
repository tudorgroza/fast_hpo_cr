import json

from FastHPOCR.util.CRConstants import ORPHA_PREFIX


class ORPHALabelCollector:
    terms = {}

    def __init__(self, orphaDataFile):
        self.terms = {}
        with open(orphaDataFile, 'r') as fh:
            jsonData = json.load(fh)

        self.collectTerms(jsonData['JDBOR'][0]['DisorderList'][0]['Disorder'])

    def collectTerms(self, orphaData):
        for entry in orphaData:
            orphaCode = ORPHA_PREFIX + entry['OrphaCode']

            syns = []
            if entry['SynonymList']:
                if entry['SynonymList'][0]:
                    if 'Synonym' in entry['SynonymList'][0]:
                        for syn in entry['SynonymList'][0]['Synonym']:
                            if len(syn['label']) < 4 and syn['label'].isupper():
                                continue
                            syns.append(syn['label'])

            self.terms[orphaCode] = {
                'label': entry['Name'][0]['label'],
                'syns': syns
            }

    def getTerms(self):
        return self.terms
