import os
import time
from os.path import join

from cr.CRIndexKB import CRIndexKB
from index.IndexTerms import IndexTerms
from index.PreprocessHPOTerms import PreprocessHPOTerms
from index.SynonymExpader import SynonymExpader
from util import ConfigConstants
from util.CRConstants import HP_INDEX_FILE, BASE_CLUSTERS, BASE_SYNONYMS


class IndexHPO:
    resFolder = None
    hpoLocation = None
    outputFolder = None
    indexConfig = {}
    valid = False

    clusters = {}
    synClusters = {}
    externalSynonyms = {}
    crIndexKB = None

    def __init__(self, hpoLocation: str, outputFolder: str, indexConfig={}):
        self.resFolder = 'resources'
        self.hpoLocation = hpoLocation
        self.outputFolder = outputFolder
        self.indexConfig = indexConfig
        self.valid = False
        self.crIndexKB = CRIndexKB()
        self.externalSynonyms = {}

    def index(self):
        start = time.time()
        self.checkPrerequisites()
        if not self.valid:
            return

        self.loadPrerequisites()
        print(' - Preprocessing HPO terms ...')
        preprocessHPOTerms = PreprocessHPOTerms(self.hpoLocation,
                                                externalSynonyms=self.externalSynonyms,
                                                indexConfig=self.indexConfig)
        processedTerms = preprocessHPOTerms.getProcessedTerms()
        catDictionary = preprocessHPOTerms.getCategoriesDictionary()

        print(' - Indexing HPO terms ...')
        indexTerms = IndexTerms(processedTerms, self.clusters, self.crIndexKB)
        termsToIndex = indexTerms.getTermsToIndex()
        voidTokens = indexTerms.getVoidTokens()

        synonymExpader = SynonymExpader(termsToIndex, voidTokens, self.synClusters)
        termsToIndex = synonymExpader.getTermsToIndex()

        print(' - Serializing index ...')
        self.crIndexKB.setHPOIndex(termsToIndex)
        self.crIndexKB.setCatDictionary(catDictionary)
        
        compress = bool(self.indexConfig.get(ConfigConstants.VAR_COMPRESS_INDEX, False))
        filename = HP_INDEX_FILE + ('.gz' if compress else '')
        file_path = join(self.outputFolder, filename)
            
        self.crIndexKB.serialize(file_path, self.clusters, compress=compress)
        end = time.time()
        print(' - HPO index created in {}s'.format(round(end - start, 2)))

    def loadPrerequisites(self):
        self.loadClusterData()
        self.loadSynClusters()
        self.loadExternalSynonyms()

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

    def loadExternalSynonyms(self):
        if not self.indexConfig:
            return

        if self.indexConfig:
            if not ConfigConstants.VAR_EXTENAL_SYNS in self.indexConfig:
                return

        with open(self.indexConfig[ConfigConstants.VAR_EXTENAL_SYNS], 'r') as fh:
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

        if self.indexConfig:
            if ConfigConstants.VAR_EXTENAL_SYNS in self.indexConfig:
                if not os.path.isfile(self.indexConfig[ConfigConstants.VAR_EXTENAL_SYNS]):
                    print('WARNING: External synonyms file provided [{}] does not exist!'.format(
                        self.indexConfig[ConfigConstants.VAR_EXTENAL_SYNS]))

        self.valid = True
