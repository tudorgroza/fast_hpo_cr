from FastHPOCR.util.AnnotationObject import AnnotationObject


class FormatResults:
    crIndexKB = None
    text = None
    result = []
    longestMatch = False

    def __init__(self, text, crIndexKB, matches, longestMatch):
        self.text = text
        self.crIndexKB = crIndexKB
        self.result = []
        self.longestMatch = longestMatch

        self.format(matches)

    def format(self, matches):
        tempResults = {}

        for match in matches:
            compressedCandidate = self.compressCandidate(match['candidate'])
            finalUri = match['uris'][0]
            finalLabel = None
            native = -1

            position = str(compressedCandidate['startOffset']) + '-' + str(
                compressedCandidate['endOffset']) + '-' + finalUri
            if position in tempResults:
                continue
            if self.longestMatch:
                found = False
                toRemove = []
                for entry in tempResults:
                    splt = entry.split('-')
                    if compressedCandidate['startOffset'] == int(splt[0]) and compressedCandidate['endOffset'] == int(
                            splt[1]):
                        continue
                    if compressedCandidate['startOffset'] >= int(splt[0]) and compressedCandidate['endOffset'] <= int(
                            splt[1]):
                        found = True
                        break
                    if compressedCandidate['startOffset'] <= int(splt[0]) and compressedCandidate['endOffset'] >= int(
                            splt[1]):
                        toRemove.append(entry)
                if found:
                    continue
                for entry in toRemove:
                    tempResults.pop(entry)

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

            categoryInfo = self.crIndexKB.getCategoriesForUri(finalUri)
            tempResults[position] = AnnotationObject(compressedCandidate['textSpan'],
                                                     finalUri,
                                                     finalLabel['originalLabel'],
                                                     compressedCandidate['startOffset'],
                                                     compressedCandidate['endOffset'],
                                                     categories=categoryInfo)

        for entry in tempResults:
            self.result.append(tempResults[entry])

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
