import os
from os.path import join

from eval.EvalConstants import BIOGS_TEST_FOLDER

GS_FOLDER = '/Users/tudor/Work/Data/BioCreative_GS/dev/annotations'
GS_TEXT_FOLDER = '/Users/tudor/Work/Data/BioCreative_GS/dev/text'


class BioCreativeCorpus:
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
        for file in os.listdir(GS_TEXT_FOLDER):
            self.loadTextFile(file, join(GS_TEXT_FOLDER, file))
        for file in os.listdir(GS_FOLDER):
            self.loadGSFile(file, join(GS_FOLDER, file))

    def loadGSFile(self, file, filePath):
        data = {}
        textEntries = {}
        fileText = self.gsText[file]

        with open(filePath, 'r') as fh:
            lines = fh.readlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue
            segs = line.split('\t')
            hpoId = segs[0]
            instances = segs[1]
            if hpoId == 'NA':
                continue

            alignedHPOId = self.ontoReader.consolidate(hpoId)
            if not alignedHPOId:
                continue

            data[alignedHPOId] = len(instances.split(','))

            lst = []
            for inst in instances.split(','):
                inst = inst.strip()
                if inst:
                    offsets = inst.split('-')
                    textSpan = fileText[int(offsets[0]): int(offsets[1])]
                    lst.append('[' + inst + '] | ' + textSpan)
            textEntries[alignedHPOId] = lst
        self.gsData[file] = data
        self.gsEntries[file] = textEntries

    def loadTextFile(self, file, filePath):
        with open(filePath, 'r') as fh:
            content = fh.read().strip()
        self.gsText[file] = content

    def loadTestData(self):
        for file in os.listdir(BIOGS_TEST_FOLDER):
            self.loadTestFile(file, join(BIOGS_TEST_FOLDER, file))

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
        return BIOGS_TEST_FOLDER
