import os
import pkgutil
import time
from os.path import join

from FastHPOCR.cr.CRIndexKB import CRIndexKB
from FastHPOCR.index.IndexTerms import IndexTerms
from FastHPOCR.index.PreprocessSNOMEDTerms import PreprocessSNOMEDTerms
from FastHPOCR.index.SNOMEDParser import SNOMEDParser
from FastHPOCR.index.SynonymExpader import SynonymExpader
from FastHPOCR.util import ConfigConstants
from FastHPOCR.util.CRConstants import BASE_CLUSTERS, BASE_SYNONYMS, SNOMED_INDEX_FILE


class IndexSNOMED:
    resFolder = None
    descFile = None
    relationsFile = None
    outputFolder = None
    valid = False

    indexConfig = {}
    clusters = {}
    synClusters = {}
    externalSynonyms = {}
    rootConcepts = []
    crIndexKB = None

    def __init__(self, descFile: str, relationsFile: str, outputFolder: str, indexConfig={}):
        self.resFolder = 'resources'
        self.descFile = descFile
        self.relationsFile = relationsFile
        self.indexConfig = indexConfig
        self.outputFolder = outputFolder
        self.valid = False
        self.crIndexKB = CRIndexKB()

        self.externalSynonyms = {}
        self.rootConcepts = []

    def index(self):
        start = time.time()
        self.checkPrerequisites()
        if not self.valid:
            return

        self.loadPrerequisites()
        print(' - Preprocessing SNOMED ...')
        snomedParser = SNOMEDParser(self.descFile, self.relationsFile, indexConfig=self.indexConfig)
        snomedParser.trim(self.rootConcepts)
        catDictionary = snomedParser.getCategoriesDictionary()

        print(' - Preprocessing SNOMED terms ...')
        preprocessOntologyTerms = PreprocessSNOMEDTerms(snomedParser.getSubTree(),
                                                        externalSynonyms=self.externalSynonyms,
                                                        indexConfig=self.indexConfig)
        processedTerms = preprocessOntologyTerms.getProcessedTerms()

        print(' - Indexing terms ...')
        indexTerms = IndexTerms(processedTerms, self.clusters, self.crIndexKB)
        termsToIndex = indexTerms.getTermsToIndex()
        voidTokens = indexTerms.getVoidTokens()

        synonymExpader = SynonymExpader(termsToIndex, voidTokens, self.synClusters)
        termsToIndex = synonymExpader.getTermsToIndex()

        print(' - Serializing index ...')
        self.crIndexKB.setHPOIndex(termsToIndex)
        self.crIndexKB.setCatDictionary(catDictionary)
        self.crIndexKB.serialize(join(self.outputFolder, SNOMED_INDEX_FILE), self.clusters)
        end = time.time()
        print(' - SNOMED index created in {}s'.format(round(end - start, 2)))

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
        if not os.path.isfile(self.descFile):
            print('ERROR: SNOMED descriptions file provided [{}] does not exist!'.format(self.descFile))
            self.valid = False
            return
        if not os.path.isfile(self.relationsFile):
            print('ERROR: SNOMED relations file provided [{}] does not exist!'.format(self.relationsFile))
            self.valid = False
            return

        if not self.indexConfig:
            print('ERROR: SNOMED root concept(s) not provided!')
            self.valid = False
            return

        if not ConfigConstants.VAR_ROOT_CONCEPTS in self.indexConfig:
            print('ERROR: SNOMED root concept(s) not provided!')
            self.valid = False
            return

        for rootConcept in self.indexConfig[ConfigConstants.VAR_ROOT_CONCEPTS]:
            rootConcept = rootConcept.lower().strip()
            rootConcept = rootConcept.replace('sctid', '').strip()
            rootConcept = rootConcept.replace(':', '').strip()
            if not rootConcept.isnumeric():
                print('WARNING: Ignoring SNOMED root concept {} because it is invalid'.format(rootConcept))
                continue
            self.rootConcepts.append(rootConcept)
        if not self.rootConcepts:
            print('ERROR: No valid SNOMED root concept(s) found!')
            self.valid = False
            return

        if ConfigConstants.VAR_EXTENAL_SYNS in self.indexConfig:
            if not os.path.isfile(self.indexConfig[ConfigConstants.VAR_EXTENAL_SYNS]):
                print('WARNING: External synonyms file provided [{}] does not exist!'.format(
                    self.indexConfig[ConfigConstants.VAR_EXTENAL_SYNS]))

        if not os.path.isdir(self.outputFolder):
            print('ERROR: Output folder provided [{}] does not exist!'.format(self.outputFolder))
            self.valid = False
            return

        self.valid = True
