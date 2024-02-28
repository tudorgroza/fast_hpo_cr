from os.path import join

from cr.HPOAnnotator import HPOAnnotator
from eval.BioCreativeCorpus import BioCreativeCorpus
from eval.HPOGSCorpus import HPOGSCorpus
from util.OntoReader import OntoReader


class CorpusAnnotate:
    ontoReader = None
    corpus = None
    hpoAnnotator = None

    def __init__(self, hpoFile, crDataFile, seqCacheFile, corpusHPO=True):
        self.gsData = {}
        self.ontoReader = OntoReader(hpoFile)
        if corpusHPO:
            self.corpus = HPOGSCorpus(self.ontoReader)
        else:
            self.corpus = BioCreativeCorpus(self.ontoReader)

        self.hpoAnnotator = HPOAnnotator(crDataFile, seqCacheFile)

    def annotate(self):
        gsTextData = self.corpus.getGSText()
        count = 1
        for file in gsTextData:
            content = gsTextData[file]
            self.hpoAnnotator.serialize(self.hpoAnnotator.annotate(content),
                                        join(self.corpus.getTestDataFolder(), file))

            count += 1
