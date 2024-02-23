from cr.CRIndexKB import CRIndexKB
from cr.CandidateMatcher import CandidateMatcher
from cr.FormatResults import FormatResults
from cr.SequenceCache import SequenceCache
from cr.TextProcessor import TextProcessor
from util import AnnotationObject


class HPOAnnotator:
    crIndexKB = None
    sequenceCache = None

    def __init__(self, crDataFile, sequenceCacheFile):
        self.crIndexKB = CRIndexKB()
        self.crIndexKB.load(crDataFile)
        self.sequenceCache = SequenceCache(sequenceCacheFile)

    def annotate(self, text) -> [AnnotationObject]:
        textProcessor = TextProcessor(self.crIndexKB, self.sequenceCache)
        textProcessor.process(text)

        candidateMatcher = CandidateMatcher(self.crIndexKB)
        candidateMatcher.matchCandidates(textProcessor.getCandidates())

        result = FormatResults(text, self.crIndexKB, candidateMatcher.getMatches()).getResult()
        return result

    def printResults(self, annotationList):
        lines = []
        for annotationObject in annotationList:
            lines.append(annotationObject.toString())
        print('\n'.join(lines))

    def serialize(self, annotationList, fileOut):
        lines = []
        for annotationObject in annotationList:
            lines.append(annotationObject.toString())
        with open(fileOut, 'w') as fh:
            fh.write('\n'.join(lines))


def main(crDataFile):
    text = 'Neurofibromatosis type 2 (NF2) is almost unique among inherited disorders in the frequency of mosaicism in the first affected generation. However, the implications of this on transmission risks have not been fully elucidated.\n\nThe expanded database of 460 families with NF2 and 704 affected individuals was analysed for mosaicism and transmission risks to offspring.\n\n64 mosaic patients, with a projected mosaicism rate of 33% for sporadic classical NF2 with bilateral vestibular schwannoma at presentation and 60% for those presenting unilaterally, were identified. Offspring risks can be radically reduced on the basis of a sensitive mutation analysis of blood DNA including multiple ligation-dependent probe amplification (MLPA, which detects 15% of all mutations), but even MLPA cannot detect high levels of mosaicism.\n\nThe chances of mosaicism in NF2 and the resultant risks of transmission of the mutation to offspring in a number of different clinical situations have been further delineated. The use of MLPA in this large NF2 series is also reported for the first time.'

    seqCacheFile = '/Users/tudor/Work/Development/code/hpo-cr/resources/sequence.list'
    hpoAnnotator = HPOAnnotator(crDataFile, seqCacheFile)
    hpoAnnotator.annotate(text)


if __name__ == '__main__':
    main('/Users/tudor/Work/Data/_experiments_new_hpo_cr_/hp.index')
