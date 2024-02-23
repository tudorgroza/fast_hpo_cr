from eval.BioCreativeCorpus import BioCreativeCorpus
from eval.HPOGSCorpus import HPOGSCorpus
from util.OntoReader import OntoReader


class CorpusEval:
    ontoReader = None
    gsData = {}
    corpus = None

    def __init__(self, hpoFile, corpusHPO=True):
        self.gsData = {}
        self.ontoReader = OntoReader(hpoFile)
        if corpusHPO:
            self.corpus = HPOGSCorpus(self.ontoReader)
        else:
            self.corpus = BioCreativeCorpus(self.ontoReader)
        self.corpus.loadTestData()

    def compareSimple(self):
        total = 0
        found = 0
        correct = 0

        gsData = self.corpus.getGSData()
        testData = self.corpus.getTestData()

        for file in gsData:
            gsFileData = gsData[file]

            total += len(gsFileData)
            if file in testData:
                testFileData = testData[file]
                found += len(testFileData)

                for hpoId in gsFileData:
                    if hpoId in testFileData:
                        correct += 1
        p = 0.0
        if found > 0:
            p = round(float(correct) / found, 2)
        r = round(float(correct) / total, 2)
        if p == 0.0 and r == 0.0:
            f1 = 0.0
        else:
            f1 = round((2 * p * r) / (p + r), 2)
        return p, r, f1

    def compareComplete(self):
        total = 0
        found = 0
        correct = 0

        gsData = self.corpus.getGSData()
        testData = self.corpus.getTestData()

        for file in gsData:
            gsFileData = gsData[file]
            for hpoId in gsFileData:
                total += gsFileData[hpoId]

            if file in testData:
                testFileData = testData[file]
                for hpoId in testFileData:
                    found += testFileData[hpoId]

                for hpoId in gsFileData:
                    if hpoId in testFileData:
                        correctHPO = gsFileData[hpoId]
                        foundHPO = testFileData[hpoId]
                        if foundHPO >= correctHPO:
                            correct += correctHPO
                        else:
                            correct += foundHPO

        p = 0.0
        if found > 0:
            p = round(float(correct) / found, 2)
        r = round(float(correct) / total, 2)
        if p == 0.0 and r == 0.0:
            f1 = 0.0
        else:
            f1 = round((2 * p * r) / (p + r), 2)

        return p, r, f1

    def runFullEval(self):
        lines = []
        p, r, f1 = self.compareSimple()
        lines.append(self.toLine('MACRO', p, r, f1))
        p, r, f1 = self.compareComplete()
        lines.append(self.toLine('MICRO', p, r, f1))
        print('\n'.join(lines))

    def toLine(self, type, p, r, f1):
        return type + ',' + str(p) + ',' + str(r) + ',' + str(f1)


def main():
#    hpoFile = '/Users/tudor/Work/Data/ontologies/hp_0224.obo'
    hpoFile = '/Users/tudor/Work/Data/ontologies/hp_0723.obo'

    corpusEval = CorpusEval(hpoFile, corpusHPO=True)
    corpusEval.runFullEval()


if __name__ == '__main__':
    main()
