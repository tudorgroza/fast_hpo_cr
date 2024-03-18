class CandidateMatcher:
    crIndexKB = None
    matches = []

    def __init__(self, crIndexKB):
        self.crIndexKB = crIndexKB
        self.matches = []

    def matchCandidates(self, candidates):
        for candidateSig in candidates:
            terms = self.crIndexKB.getClusterBasedTerms(candidateSig)
            if not terms:
                continue

            candidateList = candidates[candidateSig]
            for candidate in candidateList:
                if not len(candidate) in terms:
                    continue
                self.matches.append({
                    'uris': terms[len(candidate)],
                    'candidate': candidate,
                    'candidateSig': candidateSig
                })

    def getMatches(self):
        return self.matches

    def printMatches(self):
        for match in self.matches:
            print(' - Candidate: ')
            for token in match['candidate']:
                print(token)
            print(' - URIS: {}'.format(match['uris']))
            print(' --- ')
