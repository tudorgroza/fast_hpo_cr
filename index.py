import json

from experiments_util import HPO_FOLDER, HPO_VERSIONS, RESOURCES_FOLDER, EXPERIMENTS_OUTPUT_FOLDER
from index.IndexHPO import IndexHPO
from util import ContentUtil
from util.CRConstants import HP_INDEX_FILE


def main(resFolder, hpoLocation, outputFolder):
    indexHPO = IndexHPO(resFolder, hpoLocation, outputFolder)
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


if __name__ == '__main__':
    hpoLocation = HPO_FOLDER + HPO_VERSIONS[0]
    main(RESOURCES_FOLDER, hpoLocation, EXPERIMENTS_OUTPUT_FOLDER)
