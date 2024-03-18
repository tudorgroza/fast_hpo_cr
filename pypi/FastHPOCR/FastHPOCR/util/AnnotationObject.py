class AnnotationObject:
    textSpan = ''
    hpoUri = ''
    hpoLabel = ''
    startOffset = -1
    endOffset = -1

    def __init__(self, textSpan, hpoUri, hpoLabel, startOffset, endOffset):
        self.textSpan = textSpan
        self.hpoUri = hpoUri
        self.hpoLabel = hpoLabel
        self.startOffset = startOffset
        self.endOffset = endOffset

    def getTextSpan(self):
        return self.textSpan

    def getHPOUri(self):
        return self.hpoUri

    def getHPOLabel(self):
        return self.hpoLabel

    def getStartOffset(self):
        return self.startOffset

    def getEndOffset(self):
        return self.endOffset

    def toString(self):
        return '[' + str(self.startOffset) + ':' + str(
            self.endOffset) + ']\t' + self.hpoUri + '\t' + self.hpoLabel + '\t' + self.textSpan
