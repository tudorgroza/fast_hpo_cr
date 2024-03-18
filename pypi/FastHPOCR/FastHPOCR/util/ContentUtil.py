from typing import List

def spaceReplace(text):
    text = text.replace('-', ' ')
    text = text.replace('/', ' ')
    text = text.replace('\'', ' ')
    text = text.replace(':', ' ')
    text = text.replace(';', ' ')
    text = text.replace('_', ' ')
    text = text.replace('+', ' ')
    return text


def cleanToken(token):
    token = token.lower()
    token = token.replace('"', '')
    token = token.replace('\'', '')
    token = token.replace(',', '')
    token = token.replace('.', '')
    token = token.replace('>', '')
    token = token.replace('<', '')
    token = token.replace('%', '')
    token = token.replace(')', '')
    token = token.replace('(', '')
    token = token.replace(']', '')
    token = token.replace('[', '')
    token = token.replace('}', '')
    token = token.replace('{', '')
    return token


def wordShape(word):
    shape = 'x'
    if word.isalnum():
        shape = 'm'
        if word.isalpha():
            shape = 'a'
        if word.isnumeric():
            shape = 'd'
    return shape


def clusterSignature(clusterIds: List[str]) -> str:
    clone = clusterIds.copy()
    clone.sort()
    return '-'.join(clone)
