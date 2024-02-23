import os
from os.path import join

from eval.EvalConstants import HPOGS_TEST_FOLDER
from util.CRConstants import PHENOTYPIC_ABNORMALITY

GS_FOLDER = '/Users/tudor/Work/Data/hpo_gs/GSC+/Annotations'
GS_TEXT_FOLDER = '/Users/tudor/Work/Data/hpo_gs/GSC+/Text'


class HPOGSCorpus:
    ontoReader = None
    gsData = {}
    gsText = {}
    gsEntries = {}

    testData = {}
    testTextEntries = {}

    def __init__(self, ontoReader):
        self.gsData = {}
        self.gsText = {}
        self.gsEntries = {}
        self.testData = {}
        self.testTextEntries = {}
        self.ontoReader = ontoReader

        self.loadGS()

    def loadGS(self):
        for file in os.listdir(GS_FOLDER):
            self.loadGSFile(file, join(GS_FOLDER, file))
        for file in os.listdir(GS_TEXT_FOLDER):
            self.loadTextFile(file, join(GS_TEXT_FOLDER, file))

    def loadGSFile(self, file, filePath):
        data = {}
        textEntries = {}
        with open(filePath, 'r') as fh:
            lines = fh.readlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue
            segs = line.split('\t')
            hpoInfo = segs[1].strip().split('|')
            hpoId = hpoInfo[0].strip().replace('_', ':')
            textEntry = hpoInfo[1].strip()

            alignedHPOId = self.ontoReader.consolidate(hpoId)
            if not alignedHPOId:
                print(' -> VERY ODD: {}'.format(hpoId))
                continue

            superClasses = self.ontoReader.allSuperClasses[alignedHPOId]
            if not PHENOTYPIC_ABNORMALITY in superClasses:
                continue

            count = 0
            if alignedHPOId in data:
                count = data[alignedHPOId]
            count += 1
            data[alignedHPOId] = count

            lst = []
            if alignedHPOId in textEntries:
                lst = textEntries[alignedHPOId]
            lst.append(segs[0].strip() + ' | ' + textEntry)
            textEntries[alignedHPOId] = lst

        self.gsData[file] = data
        self.gsEntries[file] = textEntries

    def loadTextFile(self, file, filePath):
        with open(filePath, 'r') as fh:
            content = fh.read().strip()
        self.gsText[file] = content

    def loadTestData(self):
        for file in os.listdir(HPOGS_TEST_FOLDER):
            if file == '.DS_Store':
                continue
            self.loadTestFile(file, join(HPOGS_TEST_FOLDER, file))

    def loadTestFile(self, file, filePath):
        data = {}
        textEntries = {}
        with open(filePath, 'r') as fh:
            lines = fh.readlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue

            segs = line.split('\t')
            uri = segs[1]
            count = 0
            if uri in data:
                count = data[uri]
            count += 1
            data[uri] = count

            lst = []
            if uri in textEntries:
                lst = textEntries[uri]
            lst.append(segs[0] + ' | ' + segs[3])
            textEntries[uri] = lst

        self.testData[file] = data
        self.testTextEntries[file] = textEntries

    def getGSData(self):
        return self.gsData

    def getGSText(self):
        return self.gsText

    def getGSEntries(self):
        return self.gsEntries

    def getTestTextEntries(self):
        return self.testTextEntries

    def getTestData(self):
        return self.testData

    def getTestDataFolder(self):
        return HPOGS_TEST_FOLDER
