from util.AnnotationObject import AnnotationObject

class FormatResults:
    crIndexKB = None
    text = None
    result = []

    def __init__(self, text, crIndexKB, matches):
        self.text = text
        self.crIndexKB = crIndexKB
        self.result = []

        self.format(matches)

    def format(self, matches):
        for match in matches:
            compressedCandidate = self.compressCandidate(match['candidate'])
            uri = match['uris'][0]

            labels = self.crIndexKB.getLabelsForUri(uri, match['candidateSig'])
            found = labels[0]
            for label in labels:
                if label['length'] == len(match['candidate']):
                    found = label
                    break

            self.result.append(AnnotationObject(compressedCandidate['textSpan'],
                                                uri,
                                                found['originalLabel'],
                                                compressedCandidate['startOffset'],
                                                compressedCandidate['endOffset']
                                                ))

    def compressCandidate(self, candidate):
        min = 10000
        max = 0

        startIndex = -1
        endIndex = -1
        for token in candidate:
            if token.getWordIdx() <= min:
                min = token.getWordIdx()
                startIndex = token.getStartIndex()
            if token.getWordIdx() >= max:
                max = token.getWordIdx()
                endIndex = token.getStartIndex() + len(token.getWord())

        return {
            'textSpan': self.text[startIndex: endIndex],
            'startOffset': startIndex,
            'endOffset': endIndex
        }

    def getResult(self):
        return self.result
