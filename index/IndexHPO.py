import os
import time
from os.path import join

from cr.CRIndexKB import CRIndexKB
from index.IndexTerms import IndexTerms
from index.PreprocessOntologyTerms import PreprocessOntologyTerms
from index.SynonymExpader import SynonymExpader
from util.CRConstants import HP_INDEX_FILE, BASE_CLUSTERS, KB_FILE_POS_KB, BASE_SYNONYMS


class IndexHPO:
    resFolder = None
    hpoLocation = None
    outputFolder = None
    valid = False

    clusters = {}
    synClusters = {}
    posKB = {}
    crIndexKB = None

    def __init__(self, resFolder: str, hpoLocation: str, outputFolder: str):
        self.resFolder = resFolder
        self.hpoLocation = hpoLocation
        self.outputFolder = outputFolder
        self.valid = False
        self.crIndexKB = CRIndexKB()

    def index(self):
        start = time.time()
        self.checkPrerequisites()
        if not self.valid:
            return

        self.loadPrerequisites()
        print(' - Preprocessing ontology terms ...')
        preprocessOntologyTerms = PreprocessOntologyTerms(self.hpoLocation, self.posKB)
        processedTerms = preprocessOntologyTerms.getProcessedTerms()

        print(' - Indexing ontology terms ...')
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
        self.loadPOSKB()
        self.loadSynClusters()

    def loadClusterData(self):
        self.clusters = {}
        print(' - Loading cluster data ...')
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
        print(' - {} clusters loaded ...'.format(len(self.clusters)))

    def loadPOSKB(self):
        self.posKB = {}
        print(' - Loading POS KB ...')
        with open(join(self.resFolder, KB_FILE_POS_KB), 'r') as fileHandler:
            content = fileHandler.read()
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line:
                    parts = line.split('|%|')
                    token = parts[0].strip()
                    tag = parts[1].strip()
                    self.posKB[token] = tag
        print(' - POS KB loaded ...')

    def loadSynClusters(self):
        self.synClusters = {}
        print(' - Loading synonym clusters ...')
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
        print(' - {} synonym clusters loaded ...'.format(len(self.synClusters)))

    def checkPrerequisites(self):
        if not os.path.isdir(self.resFolder):
            print(
                'ERROR: Resources folder provided [{}] does not exist!'.format(self.resFolder))
            self.valid = False
            return
        if not os.path.isfile(join(self.resFolder, BASE_SYNONYMS)):
            print(
                'ERROR: Synonyms file [{}] does not exist!'.format(join(self.resFolder, BASE_SYNONYMS)))
            self.valid = False
            return
        if not os.path.isfile(join(self.resFolder, KB_FILE_POS_KB)):
            print('ERROR: POS KB [{}] does not exist!'.format(join(self.resFolder, KB_FILE_POS_KB)))
            self.valid = False
            return
        if not os.path.isfile(join(self.resFolder, BASE_CLUSTERS)):
            print('ERROR: Base clusters file [{}] does not exist!'.format(
                join(self.resFolder, BASE_CLUSTERS)))
            self.valid = False
            return
        if not os.path.isfile(self.hpoLocation):
            print('ERROR: Ontology file provided [{}] does not exist!'.format(self.hpoLocation))
            self.valid = False
            return
        if not os.path.isdir(self.outputFolder):
            print('ERROR: Output folder provided [{}] does not exist!'.format(self.outputFolder))
            self.valid = False
            return

        self.valid = True
