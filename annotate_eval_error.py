import json

from eval.CorpusAnnotate import CorpusAnnotate
from eval.CorpusErrorAnalysis import CorpusErrorAnalysis
from eval.CorpusEval import CorpusEval
from experiments_util import HPO_FOLDER, HPO_VERSIONS, EXPERIMENTS_OUTPUT_FOLDER, RESOURCES_FOLDER
from index.IndexHPO import IndexHPO
from util import ContentUtil
from util.CRConstants import HP_INDEX_FILE


def main(hpoIdx, corpusHPO):
    print(' --> HPO: {}'.format(HPO_VERSIONS[hpoIdx]))
    hpoFile = HPO_FOLDER + HPO_VERSIONS[hpoIdx]

    indexHPO = IndexHPO(RESOURCES_FOLDER, hpoFile, EXPERIMENTS_OUTPUT_FOLDER)
    indexHPO.index()

    ### INDEX DATA FOR EASIER INSPECTION

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

    #####
    ### EVALUATION
    #####

    crDataFile = '/Users/tudor/Work/Data/_experiments_new_hpo_cr_/hp.index'
    seqCacheFile = '/Users/tudor/Work/Development/code/fast_hpo_cr/resources/sequence.list'

    corpusAnnotate = CorpusAnnotate(hpoFile, crDataFile, seqCacheFile, corpusHPO=corpusHPO)
    corpusAnnotate.annotate()

    corpusEval = CorpusEval(hpoFile, corpusHPO=corpusHPO)
    corpusEval.runFullEval()

    corpusErrorAnalysis = CorpusErrorAnalysis(hpoFile, corpusHPO=corpusHPO)
    corpusErrorAnalysis.compare(EXPERIMENTS_OUTPUT_FOLDER)


if __name__ == '__main__':
    corpusHPO = False
    main(3, corpusHPO)
#    for i in range(0, len(HPO_VERSIONS)):
#        main(i)
