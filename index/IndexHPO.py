import json
import os
from os.path import join

from cr.CRIndexKB import CRIndexKB
from index.IndexTerms import IndexTerms
from index.PreprocessOntologyTerms import PreprocessOntologyTerms
from util import ContentUtil
from util.CRConstants import HP_INDEX_FILE, BASE_CLUSTERS, KB_FILE_POS_KB, BASE_SYNONYMS


class IndexHPO:
    indexConfigFile = None
    indexConfig = None
    valid = False

    clusters = {}
    posKB = {}
    crIndexKB = None

    def __init__(self, indexConfigFile: str):
        self.indexConfigFile = indexConfigFile
        self.valid = False
        self.crIndexKB = CRIndexKB()

    def index(self):
        self.checkPrerequisites()
        if not self.valid:
            return

        self.loadPrerequisites()
        print(' - Preprocessing ontology terms ...')
        preprocessOntologyTerms = PreprocessOntologyTerms(self.indexConfig['ontology'], self.posKB)
        processedTerms = preprocessOntologyTerms.getProcessedTerms()

        print(' - Indexing ontology terms ...')
        indexTerms = IndexTerms(processedTerms, self.clusters, self.crIndexKB)
        termsToIndex = indexTerms.getTermsToIndex()

        print(' - Serializing index ...')
        self.crIndexKB.setHPOIndex(termsToIndex)
        self.crIndexKB.serialize(join(self.indexConfig['output'], HP_INDEX_FILE), self.clusters)

        # TODO:
        # Include synonyms, etc
        # Write syn file

    def loadPrerequisites(self):
        self.loadClusterData()
        self.loadPOSKB()

    def loadClusterData(self):
        self.clusters = {}
        print(' - Loading cluster data ...')
        count = 1
        with open(join(self.indexConfig['resources'], BASE_CLUSTERS), 'r') as f:
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
        with open(join(self.indexConfig['resources'], KB_FILE_POS_KB), 'r') as fileHandler:
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

    def checkPrerequisites(self):
        if not os.path.isfile(self.indexConfigFile):
            print('ERROR: Index config file [{}} not found!'.format(self.indexConfigFile))
            self.valid = False
            return
        with open(self.indexConfigFile, 'r') as filehandle:
            self.indexConfig = json.load(filehandle)

        if not 'resources' in self.indexConfig:
            print('ERROR: Resources configuration missing!')
            self.valid = False
            return
        if not os.path.isdir(self.indexConfig['resources']):
            print(
                'ERROR: Resources folder provided [{}] does not exist!'.format(self.indexConfig['resources']))
            self.valid = False
            return
        if not os.path.isfile(join(self.indexConfig['resources'], BASE_SYNONYMS)):
            print(
                'ERROR: Synonyms file [{}] does not exist!'.format(join(self.indexConfig['resources'], BASE_SYNONYMS)))
            self.valid = False
            return
        if not os.path.isfile(join(self.indexConfig['resources'], KB_FILE_POS_KB)):
            print('ERROR: POS KB [{}] does not exist!'.format(join(self.indexConfig['resources'], KB_FILE_POS_KB)))
            self.valid = False
            return
        if not os.path.isfile(join(self.indexConfig['resources'], BASE_CLUSTERS)):
            print('ERROR: Base clusters file [{}] does not exist!'.format(
                join(self.indexConfig['resources'], BASE_CLUSTERS)))
            self.valid = False
            return
        if not 'ontology' in self.indexConfig:
            print('ERROR: Ontology file missing!')
            self.valid = False
            return
        if not os.path.isfile(self.indexConfig['ontology']):
            print('ERROR: Ontology file provided [{}] does not exist!'.format(self.indexConfig['ontology']))
            self.valid = False
            return
        if not 'output' in self.indexConfig:
            print('ERROR: Output folder missing!')
            self.valid = False
            return
        if not os.path.isdir(self.indexConfig['output']):
            print('ERROR: Output folder provided [{}] does not exist!'.format(self.indexConfig['output']))
            self.valid = False
            return

        self.valid = True


def main(indexConfig):
    indexHPO = IndexHPO(indexConfig)
    indexHPO.index()

    with open('/Users/tudor/Work/Data/_experiments_new_hpo_cr_/' + HP_INDEX_FILE, 'r') as filehandle:
        hpIndexData = json.load(filehandle)

    hpoIndex = hpIndexData['termData']

    lines = []
    for entry in hpoIndex:
        lines.append(entry['uri'] + '\n' + '-------')

        for label in entry['labels']:
            lines.append(label['originalLabel'] + ' >> ' + ContentUtil.clusterSignature(label['tokenSet']))

    with open('/Users/tudor/Work/Data/_experiments_new_hpo_cr_/hp_index', 'w') as fh:
        fh.write('\n'.join(lines))

if __name__ == '__main__':
    main('/Users/tudor/Work/Development/code/hpo-cr/resources/index_config.json')
