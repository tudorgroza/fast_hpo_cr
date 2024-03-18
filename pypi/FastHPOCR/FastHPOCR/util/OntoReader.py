from pronto import Ontology

from FastHPOCR.util.CRConstants import PHENOTYPIC_ABNORMALITY

SYN_SCOPE_EXACT = 'EXACT'
SYN_SCOPE_RELATED = 'RELATED'
SYN_TYPE_LAYPERSON = 'layperson'


class OntoReader:
    ontology = None

    terms = {}
    alt_ids = {}
    reverse_alt_ids = {}
    abn_classes = []
    top_level = {}
    cross_refs = {}
    synonyms = {}

    subClasses = {}
    allSubClasses = {}
    superClasses = {}
    allSuperClasses = {}

    def __init__(self, ontoFile):
        self.ontology = Ontology(ontoFile)
        self.parseOntology()

    def formatURI(self, termId):
        if '_' in termId:
            idx = termId.rfind('/')
            return termId[idx + 1:].replace('_', ':')

        if ':' in termId:
            return termId

        return None

    def parseOntology(self):
        count = 0

        for el in self.ontology.terms():
            if not el.name:
                continue
            if el.obsolete:
                replacementId = el.id
                for idd in el.replaced_by:
                    replacementId = idd.id
                    break
                self.reverse_alt_ids[el.id] = replacementId
                synList = []
                if replacementId in self.synonyms:
                    synList = self.synonyms[replacementId]
                if not el.name in synList:
                    synList.append(el.name.replace('obsolete', '').strip())
                    self.synonyms[replacementId] = synList
                continue

            self.terms[el.id] = el.name
            if el.alternate_ids:
                alt_id_list = []
                for alt_id in el.alternate_ids:
                    if not alt_id in alt_id_list:
                        alt_id_list.append(alt_id)
                    self.reverse_alt_ids[alt_id] = el.id
                self.alt_ids[el.id] = alt_id_list

            syns = []
            if el.id in self.synonyms:
                syns = self.synonyms[el.id]
            for syn in el.synonyms:
                if syn.scope == SYN_SCOPE_EXACT:
                    if not syn.description in syns:
                        syns.append(syn.description)
                if syn.scope == SYN_SCOPE_RELATED:
                    if not syn.description in syns:
                        syns.append(syn.description)

            if el.xrefs:
                for xref in el.xrefs:
                    if xref.description:
                        if not xref.description in syns:
                            syns.append(xref.description)

            self.synonyms[el.id] = syns

            if el.xrefs:
                dictSet = list(el.xrefs)
                refs = []
                for xref in dictSet:
                    refs.append(xref.id)
                self.cross_refs[el.id] = refs

            for superCls in el.superclasses(distance=1, with_self=False).to_set():
                superClsUri = self.formatURI(superCls.id)
                if superClsUri == PHENOTYPIC_ABNORMALITY:
                    self.abn_classes.append(el.id)

            subClsList = []
            for subCls in el.subclasses(distance=1, with_self=False).to_set():
                subClsUri = self.formatURI(subCls.id)
                subClsList.append(subClsUri)
            self.subClasses[el.id] = subClsList

            allSubClsList = []
            for subCls in el.subclasses(with_self=False).to_set():
                subClsUri = self.formatURI(subCls.id)
                allSubClsList.append(subClsUri)
            self.allSubClasses[el.id] = allSubClsList

            superClsList = []
            for superCls in el.superclasses(distance=1, with_self=False).to_set():
                superClsUri = self.formatURI(superCls.id)
                superClsList.append(superClsUri)
            self.superClasses[el.id] = superClsList

            allSuperClsList = []
            for superCls in el.superclasses(with_self=False).to_set():
                superClsUri = self.formatURI(superCls.id)
                allSuperClsList.append(superClsUri)
            self.allSuperClasses[el.id] = allSuperClsList

        for el in self.ontology.terms():
            top_list = []
            for superCls in el.superclasses(with_self=False).to_set():
                superClsUri = self.formatURI(superCls.id)
                if superClsUri == el.id:
                    continue
                if superClsUri in self.abn_classes:
                    top_list.append(superClsUri)
            self.top_level[el.id] = top_list

            count += 1

    def consolidate(self, hpoId):
        if hpoId in self.terms:
            return hpoId
        if hpoId in self.reverse_alt_ids:
            return self.reverse_alt_ids[hpoId]
        return None
