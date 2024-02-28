import collections
import os
from os.path import join

from util.OntoReader import OntoReader


def extractFileDate(file):
    segs = file.split('_')
    parts = segs[1].split('.')
    fileDate = parts[0].split('-')
    return int(fileDate[1]), int(fileDate[0])


def analyse(prevData, terms):
    print(' -- {} vs {}'.format(len(prevData), len(terms)))

    prevCount = 0
    currCount = 0
    for uri in prevData:
        if not uri in terms:
            prevCount += 1
    for uri in terms:
        if not uri in prevData:
            currCount += 1
    print(' -- {} vs {}'.format(prevCount, currCount))


def main():
    hpoFolder = '/Users/tudor/Work/Data/ontologies/hpo_timeline_2023'
    data = {}

    for file in os.listdir(hpoFolder):
        if file == '.DS_Store':
            continue
        month, year = extractFileDate(file)

        months = {}
        if year in data:
            months = data[year]
        months[month] = {}
        data[year] = months

    for year in data:
        temp = data[year].copy()
        data[year] = collections.OrderedDict(sorted(temp.items()))

    sortedData = collections.OrderedDict(sorted(data.items()))

    prevData = {}
    prevDate = ''

    for year in sortedData:
        months = sortedData[year]
        for month in months:
            monthS = str(month)
            if len(monthS) == 1:
                monthS = '0' + monthS

            ontoFile = 'hp_' + str(year) + '-' + monthS + '.obo'
            ontoReader = OntoReader(join(hpoFolder, ontoFile))
            if not prevData:
                prevData = ontoReader.terms.copy()
                prevDate = monthS + '-' + str(year)
            else:
                currentDate = monthS + '-' + str(year)
                print(' - {} vs {} ::'.format(prevDate, currentDate))
                analyse(prevData, ontoReader.terms)
                prevData = ontoReader.terms.copy()
                prevDate = currentDate


if __name__ == '__main__':
    main()
