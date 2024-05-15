import os
import time
from os.path import join

from cr.CRIndexKB import CRIndexKB
from index.IndexTerms import IndexTerms
from index.PreprocessORPHATerms import PreprocessORPHATerms
from index.SynonymExpader import SynonymExpader
from util.CRConstants import BASE_CLUSTERS, BASE_SYNONYMS, ORPHA_INDEX_FILE


class IndexORPHANET:
    resFolder = None
    orphaDataFile = None
    outputFolder = None
    valid = False

    clusters = {}
    synClusters = {}
    crIndexKB = None

    def __init__(self, orphaDataFile: str, outputFolder: str):
        self.resFolder = 'resources'
        self.orphaDataFile = orphaDataFile
        self.outputFolder = outputFolder
        self.valid = False
        self.crIndexKB = CRIndexKB()

    def index(self):
        start = time.time()
        self.checkPrerequisites()
        if not self.valid:
            return

        self.loadPrerequisites()
        print(' - Preprocessing ORPHA terms ...')
        preprocessOntologyTerms = PreprocessORPHATerms(self.orphaDataFile)
        processedTerms = preprocessOntologyTerms.getProcessedTerms()

        print(' - Indexing ORPHA terms ...')
        indexTerms = IndexTerms(processedTerms, self.clusters, self.crIndexKB)
        termsToIndex = indexTerms.getTermsToIndex()
        voidTokens = indexTerms.getVoidTokens()

        synonymExpader = SynonymExpader(termsToIndex, voidTokens, self.synClusters)
        termsToIndex = synonymExpader.getTermsToIndex()

        print(' - Serializing index ...')
        self.crIndexKB.setHPOIndex(termsToIndex)
        self.crIndexKB.serialize(join(self.outputFolder, ORPHA_INDEX_FILE), self.clusters)
        end = time.time()
        print(' - ORPHA index created in {}s'.format(round(end - start, 2)))

    def loadPrerequisites(self):
        self.loadClusterData()
        self.loadSynClusters()

    def loadClusterData(self):
        self.clusters = {}
        count = 1
        with open(join(self.resFolder, BASE_CLUSTERS), 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line:
                    tokens = line.split(',')
                    for token in tokens:
                        self.clusters[token] = 'C' + str(count)
                    count += 1

    def loadSynClusters(self):
        self.synClusters = {}
        with open(join(self.resFolder, BASE_SYNONYMS), 'r') as f:
            lines = f.readlines()
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

    def checkPrerequisites(self):
        if not os.path.isfile(self.orphaDataFile):
            print('ERROR: Orphanet JSON data file provided [{}] does not exist!'.format(self.orphaDataFile))
            self.valid = False
            return
        if not os.path.isdir(self.outputFolder):
            print('ERROR: Output folder provided [{}] does not exist!'.format(self.outputFolder))
            self.valid = False
            return

        self.valid = True
