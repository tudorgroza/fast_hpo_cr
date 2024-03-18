from FastHPOCR.util import ContentUtil
from FastHPOCR.util.CRConstants import NULL


class AnnotationToken:
    word = None
    token = None
    wordIdx = -1
    startIndex = -1
    clusterId = NULL
    shape = None

    def __init__(self, word, wordIdx, startIndex):
        self.word = word
        self.token = word.lower()
        self.wordIdx = wordIdx
        self.startIndex = startIndex
        self.shape = ContentUtil.wordShape(self.token)

        self.clusterId = NULL

    def setClusterId(self, clusterId):
        self.clusterId = clusterId

    def getToken(self):
        return self.token

    def getClusterId(self):
        return self.clusterId

    def getWordIdx(self):
        return self.wordIdx

    def getStartIndex(self):
        return self.startIndex

    def getWord(self):
        return self.word

    def asDict(self):
        return {
            'word': self.word,
            'token': self.token,
            'wordIdx': self.wordIdx,
            'startIndex': self.startIndex,
            'clusterId': self.clusterId
        }

    def __str__(self):
        return str(self.asDict())
