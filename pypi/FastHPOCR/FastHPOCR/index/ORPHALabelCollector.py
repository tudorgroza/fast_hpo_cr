import json

from FastHPOCR.util import ConfigConstants
from FastHPOCR.util.CRConstants import ORPHA_PREFIX


class ORPHALabelCollector:
    terms = {}
    externalSynonyms = {}
    allow3LetterAcronyms = False

    def __init__(self, orphaDataFile, externalSynonyms={}, indexConfig={}):
        self.terms = {}
        self.externalSynonyms = externalSynonyms
        with open(orphaDataFile, 'r') as fh:
            jsonData = json.load(fh)

        if ConfigConstants.VAR_3LETTER_ACRONYMS in indexConfig:
            self.allow3LetterAcronyms = indexConfig[ConfigConstants.VAR_3LETTER_ACRONYMS]

        self.collectTerms(jsonData['JDBOR'][0]['DisorderList'][0]['Disorder'])

    def collectTerms(self, orphaData):
        for entry in orphaData:
            orphaCode = ORPHA_PREFIX + entry['OrphaCode']

            syns = []
            if orphaCode in self.externalSynonyms:
                syns.extend(self.externalSynonyms[orphaCode])

            if entry['SynonymList']:
                if entry['SynonymList'][0]:
                    if 'Synonym' in entry['SynonymList'][0]:
                        for syn in entry['SynonymList'][0]['Synonym']:
                            size = 4
                            if self.allow3LetterAcronyms:
                                size = 3

                            if len(syn['label']) < size and syn['label'].isupper():
                                continue
                            syns.append(syn['label'])

            self.terms[orphaCode] = {
                'label': entry['Name'][0]['label'],
                'syns': syns
            }

    def getTerms(self):
        return self.terms
