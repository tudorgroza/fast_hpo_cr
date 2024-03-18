from FastHPOCR.util.AnnotationObject import AnnotationObject


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
            finalUri = match['uris'][0]
            finalLabel = None
            native = -1

            for uri in match['uris']:
                labels = self.crIndexKB.getLabelsForUri(uri, match['candidateSig'])
                for label in labels:
                    if label['length'] == len(match['candidate']):
                        if native == -1:
                            finalLabel = label
                            finalUri = uri
                            native = 0
                            continue
                        else:
                            if label['native']:
                                finalLabel = label
                                finalUri = uri
                                break

            self.result.append(AnnotationObject(compressedCandidate['textSpan'],
                                                finalUri,
                                                finalLabel['originalLabel'],
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
