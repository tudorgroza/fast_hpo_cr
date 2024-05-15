import os
import pkgutil
import time
from os.path import join

from FastHPOCR.cr.CRIndexKB import CRIndexKB
from FastHPOCR.index.IndexTerms import IndexTerms
from FastHPOCR.index.PreprocessHPOTerms import PreprocessHPOTerms
from FastHPOCR.index.SynonymExpader import SynonymExpader
from FastHPOCR.util.CRConstants import HP_INDEX_FILE, BASE_CLUSTERS, BASE_SYNONYMS


class IndexHPO:
    resFolder = None
    hpoLocation = None
    outputFolder = None
    externalSynFile = None
    valid = False
    allow3LetterAcronyms = False

    clusters = {}
    synClusters = {}
    externalSynonyms = {}
    crIndexKB = None

    def __init__(self, hpoLocation: str, outputFolder: str, externalSynFile=None, allow3LetterAcronyms=False):
        self.resFolder = 'resources'
        self.hpoLocation = hpoLocation
        self.outputFolder = outputFolder
        self.externalSynFile = externalSynFile
        self.valid = False
        self.allow3LetterAcronyms = allow3LetterAcronyms
        self.crIndexKB = CRIndexKB()
        self.externalSynonyms = {}

    def index(self):
        start = time.time()
        self.checkPrerequisites()
        if not self.valid:
            return

        self.loadPrerequisites()
        print(' - Preprocessing HPO terms ...')
        preprocessHPOTerms = PreprocessHPOTerms(self.hpoLocation, externalSynonyms=self.externalSynonyms,
                                                allow3LetterAcronyms=self.allow3LetterAcronyms)
        processedTerms = preprocessHPOTerms.getProcessedTerms()

        print(' - Indexing HPO terms ...')
        indexTerms = IndexTerms(processedTerms, self.clusters, self.crIndexKB)
        termsToIndex = indexTerms.getTermsToIndex()
        voidTokens = indexTerms.getVoidTokens()

        synonymExpader = SynonymExpader(termsToIndex, voidTokens, self.synClusters)
        termsToIndex = synonymExpader.getTermsToIndex()

        print(' - Serializing index ...')
        self.crIndexKB.setHPOIndex(termsToIndex)
        self.crIndexKB.serialize(join(self.outputFolder, HP_INDEX_FILE), self.clusters)
        end = time.time()
        print(' - HPO index created in {}s'.format(round(end - start, 2)))

    def loadPrerequisites(self):
        self.loadClusterData()
        self.loadSynClusters()
        self.loadExternalSynonyms()

    def loadClusterData(self):
        self.clusters = {}
        count = 1
        clusterContent = pkgutil.get_data(__name__, join(self.resFolder, BASE_CLUSTERS)).decode("utf-8")
        lines = clusterContent.split('\n')
        for line in lines:
            line = line.strip()
            if line:
                tokens = line.split(',')
                for token in tokens:
                    self.clusters[token] = 'C' + str(count)
                count += 1

    def loadSynClusters(self):
        self.synClusters = {}
        clusterContent = pkgutil.get_data(__name__, join(self.resFolder, BASE_SYNONYMS)).decode("utf-8")
        lines = clusterContent.split('\n')
        for line in lines:
            line = line.strip()
            if line:
                tokens = line.split(',')
                clusterSet = []
                for token in tokens:
                    token = token.strip()
                    clusterSet.append(self.clusters[token])
                for token in tokens:
                    token = token.strip()
                    self.synClusters[self.clusters[token]] = clusterSet

    def loadExternalSynonyms(self):
        if not self.externalSynFile:
            return
        with open(self.externalSynFile, 'r') as fh:
            lines = fh.readlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue
            segs = line.split('=')
            if len(segs) != 2:
                continue
            uri = segs[0].strip()
            if not uri.startswith('HP:'):
                continue
            syn = segs[1].strip()
            lst = []
            if uri in self.externalSynonyms:
                lst = self.externalSynonyms[uri]
            lst.append(syn)
            self.externalSynonyms[uri] = lst

    def checkPrerequisites(self):
        if not os.path.isfile(self.hpoLocation):
            print('ERROR: Ontology file provided [{}] does not exist!'.format(self.hpoLocation))
            self.valid = False
            return
        if not os.path.isdir(self.outputFolder):
            print('ERROR: Output folder provided [{}] does not exist!'.format(self.outputFolder))
            self.valid = False
            return

        if self.externalSynFile:
            if not os.path.isfile(self.externalSynFile):
                print('WARNING: External synonyms file provided [{}] does not exist!'.format(self.externalSynFile))
                self.externalSynFile = None

        self.valid = True