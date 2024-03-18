from FastHPOCR.util.AnnotationToken import AnnotationToken
from FastHPOCR.util import ContentUtil

class TextSplitter:
    tokens = []

    def __init__(self, text):
        self.tokens = []
        self.splitIntoTokens(text)

    def splitIntoTokens(self, text):
        wordIdx = 0
        word = ''
        startIndex = 0
        for idx, char in enumerate(text):
            if char == ' ' or char == '\n':
                splitCleanWord = self.splitClean(word)
                if len(splitCleanWord) == 1:
                    if not word:
                        startIndex = idx + 1
                        continue

                    splitSpecialWord = self.splitSpecial(word)
                    if len(splitSpecialWord) == 1:
                        self.tokens.append(AnnotationToken(word, wordIdx, startIndex))
                        wordIdx += 1
                    else:
                        prev = startIndex
                        for wd in splitSpecialWord:
                            self.tokens.append(AnnotationToken(wd, wordIdx, prev))
                            prev += len(wd)
                            wordIdx += 1
                    word = ''
                    startIndex = idx + 1
                else:
                    prev = startIndex
                    for wd in splitCleanWord:
                        splitSpecialWord = self.splitSpecial(wd)
                        if len(splitSpecialWord) == 1:
                            self.tokens.append(AnnotationToken(wd, wordIdx, prev))
                            wordIdx += 1
                        else:
                            pprev = prev
                            for wwd in splitSpecialWord:
                                self.tokens.append(AnnotationToken(wwd, wordIdx, pprev))
                                pprev += len(wd)
                                wordIdx += 1
                        prev += len(wd) + 1
                    word = ''
                    startIndex = idx + 1
            else:
                word += char
        if word:
            splitCleanWord = self.splitClean(word)
            if len(splitCleanWord) == 1:
                splitSpecialWord = self.splitSpecial(word)
                if len(splitSpecialWord) == 1:
                    self.tokens.append(AnnotationToken(word, wordIdx, startIndex))
                else:
                    prev = startIndex
                    for wd in splitSpecialWord:
                        self.tokens.append(AnnotationToken(wd, wordIdx, prev))
                        prev += len(wd)
                        wordIdx += 1
            else:
                prev = startIndex
                for wd in splitCleanWord:
                    splitSpecialWord = self.splitSpecial(wd)
                    if len(splitSpecialWord) == 1:
                        self.tokens.append(AnnotationToken(wd, wordIdx, prev))
                        wordIdx += 1
                    else:
                        pprev = prev
                        for wwd in splitSpecialWord:
                            self.tokens.append(AnnotationToken(wwd, wordIdx, pprev))
                            pprev += len(wd)
                            wordIdx += 1
                    prev += len(wd) + 1

    def splitClean(self, word):
        clean = ContentUtil.spaceReplace(word)
        splitClean = clean.split(' ')
        return splitClean

    def splitSpecial(self, word):
        splitWord = []
        current = ''
        for el in word:
            if el.isalnum():
                current += el
            else:
                if current:
                    splitWord.append(current)
                current = ''
                splitWord.append(el)
        if current:
            splitWord.append(current)
        return splitWord

    def getTokens(self) -> [AnnotationToken]:
        return self.tokens
