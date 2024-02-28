import time

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

#        textProcessor.printTokens()
#        print(' ========= ')
#        textProcessor.printCandidates()

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
    text = 'We analyzed 61 Angelman syndrome (AS) patients by cytogenetic and molecular techniques. On the basis of molecular findings, the patients were classified into the following 4 groups: familial cases without deletion, familial cases with submicroscopic deletion, sporadic cases with deletion, and sporadic cases without deletion. Among 53 sporadic cases, 37 (70%) had molecular deletion, which commonly extended from D15S9 to D15S12, although not all deletions were identical. Of 8 familial cases, 3 sibs from one family had a molecular deletion involving only 2 loci, D15S10 and GABRB3, which define the critical region for AS phenotypes. The parental origin of deletion, both in sporadic and familial cases, was exclusively maternal and consistent with a genomic imprinting hypothesis. Among sporadic and familial cases without deletion, no uniparental disomy was found and most of them were shown to inherit chromosomes 15 from both parents (biparental inheritance). A discrepancy between cytogenetic and molecular deletion was observed in 14 (26%) of 53 patients in whom cytogenetic analysis could be performed. Ten (43%) of 23 patients with a normal karyotype showed a molecular deletion, and 4 (13%) of 30 patients with cytogenetic deletion, del(15) (q11q13), showed no molecular deletion. Most clinical manifestations, including neurological signs and facial characteristics, were not distinct in each group except for hypopigmentation of skin or hair. Familial cases with submicroscopic deletion were not associated with hypopigmentation. These findings suggested that a gene for hypopigmentation is located outside the critical region of AS and is not imprinted.'

    seqCacheFile = '/Users/tudor/Work/Development/code/hpo-cr/resources/sequence.list'
    hpoAnnotator = HPOAnnotator(crDataFile, seqCacheFile)
    hpoAnnotator.printResults(hpoAnnotator.annotate(text))

if __name__ == '__main__':
    main('/Users/tudor/Work/Data/_experiments_new_hpo_cr_/hp.index')