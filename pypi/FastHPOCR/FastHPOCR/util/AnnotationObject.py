class AnnotationObject:
    textSpan = ''
    hpoUri = ''
    hpoLabel = ''
    startOffset = -1
    endOffset = -1
    categories = []

    def __init__(self, textSpan, hpoUri, hpoLabel, startOffset, endOffset, categories=[]):
        self.textSpan = textSpan
        self.hpoUri = hpoUri
        self.hpoLabel = hpoLabel
        self.startOffset = startOffset
        self.endOffset = endOffset
        self.categories = categories

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

    def getCategories(self):
        return self.categories

    def toString(self):
        return '[' + str(self.startOffset) + ':' + str(
            self.endOffset) + ']\t' + self.hpoUri + '\t' + self.hpoLabel + '\t' + self.textSpan

    def toStringWithCategories(self):
        catString = ''
        if self.categories:
            catString = '['
            for cat in self.categories:
                catString += cat['uri'] + ' (' + cat['label'] + ') | '
            catString = catString.strip()
            if catString.endswith('|'):
                catString = catString[:-1].strip()
            catString += ']'

        toReturn = '[' + str(self.startOffset) + ':' + str(
            self.endOffset) + ']\t' + self.hpoUri + '\t' + self.hpoLabel + '\t' + self.textSpan
        if catString:
            toReturn += '\t' + catString
        return toReturn
