import os
import pkgutil
import time
from os.path import join

from FastHPOCR.cr.CRIndexKB import CRIndexKB
from FastHPOCR.index.IndexTerms import IndexTerms
from FastHPOCR.index.PreprocessSNOMEDTerms import PreprocessSNOMEDTerms
from FastHPOCR.index.SNOMEDParser import SNOMEDParser
from FastHPOCR.index.SynonymExpader import SynonymExpader
from FastHPOCR.util.CRConstants import BASE_CLUSTERS, BASE_SYNONYMS, SNOMED_INDEX_FILE


class IndexSNOMED:
    resFolder = None
    descFile = None
    relationsFile = None
    rootConcept = None
    outputFolder = None
    valid = False

    clusters = {}
    synClusters = {}
    crIndexKB = None

    def __init__(self, descFile: str, relationsFile: str, rootConcept: str, outputFolder: str):
        self.resFolder = 'resources'
        self.descFile = descFile
        self.relationsFile = relationsFile
        self.rootConcept = rootConcept
        self.outputFolder = outputFolder
        self.valid = False
        self.crIndexKB = CRIndexKB()

    def index(self):
        start = time.time()
        self.checkPrerequisites()
        if not self.valid:
            return

        self.loadPrerequisites()
        print(' - Preprocessing SNOMED ...')
        snomedParser = SNOMEDParser(self.descFile, self.relationsFile)
        snomedParser.trim(self.rootConcept)

        print(' - Preprocessing SNOMED terms ...')
        preprocessOntologyTerms = PreprocessSNOMEDTerms(snomedParser.getSubTree())
        processedTerms = preprocessOntologyTerms.getProcessedTerms()

        print(' - Indexing terms ...')
        indexTerms = IndexTerms(processedTerms, self.clusters, self.crIndexKB)
        termsToIndex = indexTerms.getTermsToIndex()
        voidTokens = indexTerms.getVoidTokens()

        synonymExpader = SynonymExpader(termsToIndex, voidTokens, self.synClusters)
        termsToIndex = synonymExpader.getTermsToIndex()

        print(' - Serializing index ...')
        self.crIndexKB.setHPOIndex(termsToIndex)
        self.crIndexKB.serialize(join(self.outputFolder, SNOMED_INDEX_FILE), self.clusters)
        end = time.time()
        print(' - SNOMED index created in {}s'.format(round(end - start, 2)))

    def loadPrerequisites(self):
        self.loadClusterData()
        self.loadSynClusters()

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

    def checkPrerequisites(self):
        if not os.path.isfile(self.descFile):
            print('ERROR: SNOMED descriptions file provided [{}] does not exist!'.format(self.descFile))
            self.valid = False
            return
        if not os.path.isfile(self.relationsFile):
            print('ERROR: SNOMED relations file provided [{}] does not exist!'.format(self.relationsFile))
            self.valid = False
            return
        self.rootConcept = self.rootConcept.lower().strip()
        self.rootConcept = self.rootConcept.replace('sctid', '')
        self.rootConcept = self.rootConcept.replace(':', '')
        self.rootConcept = self.rootConcept.strip()
        if not self.rootConcept.isnumeric():
            print('ERROR: SNOMED root concept provided [{}] is invalid.'.format(self.rootConcept))
            self.valid = False
            return

        if not os.path.isdir(self.outputFolder):
            print('ERROR: Output folder provided [{}] does not exist!'.format(self.outputFolder))
            self.valid = False
            return

        self.valid = True
