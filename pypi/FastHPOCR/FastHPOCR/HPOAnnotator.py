from FastHPOCR.cr.CRIndexKB import CRIndexKB
from FastHPOCR.cr.CandidateMatcher import CandidateMatcher
from FastHPOCR.cr.FormatResults import FormatResults
from FastHPOCR.cr.TextProcessor import TextProcessor
from FastHPOCR.util import AnnotationObject


class HPOAnnotator:
    crIndexKB = None

    def __init__(self, crDataFile):
        self.crIndexKB = CRIndexKB()
        self.crIndexKB.load(crDataFile)

    def annotate(self, text) -> [AnnotationObject]:
        textProcessor = TextProcessor(self.crIndexKB)
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
