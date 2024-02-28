from os.path import join

from eval.BioCreativeCorpus import BioCreativeCorpus
from eval.HPOGSCorpus import HPOGSCorpus
from util.OntoReader import OntoReader


class CorpusErrorAnalysis:
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

    def serializeCorpus(self, outputFolder):
        lines = []
        for file in self.corpus.getGSEntries():
            lines.append(file + '\n' + '-------')

            for hpoId in self.corpus.getGSEntries()[file]:
                lst = self.corpus.getGSEntries()[file][hpoId]
                line = ''
                for entry in lst:
                    line += entry + ' ;; '
                lines.append(hpoId + ' >> ' + line)
        with open(join(outputFolder, 'gs.txt'), 'w') as fh:
            fh.write('\n'.join(lines))

    def compare(self, outputFolder):
        gsData = self.corpus.getGSData()
        testData = self.corpus.getTestData()

        notFoundFileLines = []
        incorrectFileLines = []

        for file in gsData:
            notFoundFileLines.append(file + '\n' + '-------')
            incorrectFileLines.append(file + '\n' + '-------')

            gsFileData = gsData[file]

            notFound = {}
            incorrect = {}

            if file in testData:
                testFileData = testData[file]

                for hpoId in gsFileData:
                    if not hpoId in testFileData:
                        notFound[hpoId] = self.corpus.getGSEntries()[file][hpoId]

                for hpoId in testFileData:
                    if not hpoId in gsFileData:
                        incorrect[hpoId] = self.corpus.getTestTextEntries()[file][hpoId]

            for hpoId in notFound:
                line = ''
                for entry in notFound[hpoId]:
                    line += entry + ' ;; '
                notFoundFileLines.append(hpoId + ' >> ' + line)

            for hpoId in incorrect:
                line = ''
                for entry in incorrect[hpoId]:
                    line += entry + ' ;; '
                incorrectFileLines.append(hpoId + ' >> ' + line)

        with open(join(outputFolder, 'not_found.txt'), 'w') as fh:
            fh.write('\n'.join(notFoundFileLines))
        with open(join(outputFolder, 'incorrect.txt'), 'w') as fh:
            fh.write('\n'.join(incorrectFileLines))
