class SequenceCache:
    cache = {}

    def __init__(self, sequenceCacheFile):
        self.cache = {}
        self.load(sequenceCacheFile)

    def load(self, seqFile):
        with open(seqFile, 'r') as fh:
            lines = fh.readlines()

        current = None
        iLines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('I='):
                thisI = line.split('=')[1]
                if current:
                    self.addToCache(current, iLines)
                    current = thisI
                    iLines = []
                else:
                    current = thisI
                continue
            else:
                iLines.append(line)
        self.addToCache(current, iLines)

    def addToCache(self, i, lines):
        iData = {}
        current = None
        idx = []

        for line in lines:
            if line.startswith('-L='):
                thisL = line.split('=')[1]
                if current:
                    iData[int(current)] = idx
                    current = thisL
                    idx = []
                else:
                    current = thisL
                continue
            else:
                segData = []
                segs = line.split(',')
                for seg in segs:
                    seg = seg.strip()
                    if not seg:
                        continue
                    segData.append(int(seg))
                idx.append(segData)
        iData[int(current)] = idx
        sortedIData = dict(sorted(iData.items()))
        self.cache[int(i)] = sortedIData

    def getSequences(self, length):
        return self.cache[length]
