from cr.CRIndexKB import CRIndexKB
from cr.CandidateMatcher import CandidateMatcher
from cr.FormatResults import FormatResults
from cr.TextProcessor import TextProcessor
from util import AnnotationObject


class HPOAnnotator:
    crIndexKB = None

    def __init__(self, crDataFile):
        self.crIndexKB = CRIndexKB()
        self.crIndexKB.load(crDataFile)

    def annotate(self, text: str, longestMatch=False) -> [AnnotationObject]:
        textProcessor = TextProcessor(self.crIndexKB)
        textProcessor.process(text)

        candidateMatcher = CandidateMatcher(self.crIndexKB)
        candidateMatcher.matchCandidates(textProcessor.getCandidates())

        result = FormatResults(text, self.crIndexKB, candidateMatcher.getMatches(), longestMatch).getResult()
        return result

    def printResults(self, annotationList, includeCategoriesIfPresent=False):
        lines = []
        for annotationObject in annotationList:
            if includeCategoriesIfPresent:
                lines.append(annotationObject.toStringWithCategories())
            else:
                lines.append(annotationObject.toString())
        print('\n'.join(lines))

    def serialize(self, annotationList, fileOut, includeCategoriesIfPresent=False):
        lines = []
        for annotationObject in annotationList:
            if includeCategoriesIfPresent:
                lines.append(annotationObject.toStringWithCategories())
            else:
                lines.append(annotationObject.toString())
        with open(fileOut, 'w') as fh:
            fh.write('\n'.join(lines))
