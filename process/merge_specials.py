def main():
    clusters = {}
    count = 1
    reverseClusters = {}

    with open('/Users/tudor/Work/Development/code/fast_hpo_cr/resources/special_clusters.list', 'r') as fh:
        lines = fh.readlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue

        segs = line.split(',')
        clusterId = 'C' + str(count)
        for el in segs:
            if el in clusters:
                clusterId = clusters[el]
            clusters[el] = clusterId
        count += 1

    with open('/Users/tudor/Work/Development/code/fast_hpo_cr/resources/base-clusters', 'r') as fh:
        lines = fh.readlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue

        segs = line.split(',')
        clusterId = 'C' + str(count)
        for el in segs:
            if el in clusters:
                clusterId = clusters[el]
            clusters[el] = clusterId
        count += 1

    with open('/Users/tudor/Work/Development/code/fast_hpo_cr/resources/base-synonyms', 'r') as fh:
        lines = fh.readlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue

        segs = line.split(',')
        for el in segs:
            el = el.strip()
            if not el in clusters:
                print(el)

    firstWords = []
    for token in clusters:
        clusterId = clusters[token]
        lst = []
        if clusterId in reverseClusters:
            lst = reverseClusters[clusterId]
        if not token in lst:
            lst.append(token)
        lst.sort()
        firstWords.append(lst[0])
        reverseClusters[clusterId] = lst

    firstWords.sort()
    lines = []
    clustersDone = {}
    for word in firstWords:
        for clusterId in reverseClusters:
            if clusterId in clustersDone:
                continue
            lst = reverseClusters[clusterId]
            if word in lst:
                lines.append(','.join(lst))
                clustersDone[clusterId] = ''
                break
    with open('/Users/tudor/Work/Development/code/fast_hpo_cr/resources/merged_clusters.list', 'w') as fh:
        fh.write('\n'.join(lines))


if __name__ == '__main__':
    main()
