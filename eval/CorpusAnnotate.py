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
        print(' - Annotating ...')
        gsTextData = self.corpus.getGSText()
        count = 1
        for file in gsTextData:
            print(' - [{} of {}]: {}'.format(count, len(gsTextData), file))
            content = gsTextData[file]
            self.hpoAnnotator.serialize(self.hpoAnnotator.annotate(content),
                                        join(self.corpus.getTestDataFolder(), file))

            count += 1


def main():
#    hpoFile = '/Users/tudor/Work/Data/ontologies/hp_0224.obo'
    hpoFile = '/Users/tudor/Work/Data/ontologies/hp_0723.obo'
    crDataFile = '/Users/tudor/Work/Data/_experiments_new_hpo_cr_/hp.index'
    seqCacheFile = '/Users/tudor/Work/Development/code/hpo-cr/resources/sequence.list'

    corpusAnnotate = CorpusAnnotate(hpoFile, crDataFile, seqCacheFile, corpusHPO=True)
    corpusAnnotate.annotate()


if __name__ == '__main__':
    main()
