# FastHPOCR

**FastHPOCR** is a phenotype concept recognition package using the Human Phenotype Ontology to extract concepts from free text. 
The solution relies on the fundamental pillars of concept recognition in order to cover its two underlying components - boundary detection and entity linking:
* Understanding the domain challenges - in the case of phenotypes, lexical variability
* Understanding the target ontology - and hence processing the ontology terms appropriately for text mining
More concretely, it uses a pre-built large collection of clusters of morphologically-equivalent tokens - to address lexical variability - and to reduce the boundary detection step to spans containing only tokens belonging to ontology concepts. Pre-processing the domain knowledge to create the collection of clusters was performed using OpenAI’s gpt-4.0 model and the resulting vocabulary contains 573,507 tokens, which leads to virtually no updates needed.

**FastHPOCR** was built for speed:
* Indexing a new ontology version takes ~3min
* Performing concept recognition on plain text: ~5s for 10,000 publication abstracts

## v2.0

In v2.0, the library was expanded to include the ability to index SNOMED-CT branches and the ORPHANET terminology.
The accuracy of performing concept recognition using these two vocabularies has not been assessed yet.

## Usage

### Indexing HPO

Optional index configuration:
```python
indexConfig = {
    'rootConcepts': ['HP:0001574', 'HP:0000478', 'HP:0000598', 'HP:0000707', 'HP:0000119']
    'allow3LetterAcronyms': True | False,
    'includeTopLevelCategory': True | False,
    'allowDuplicateEntries': True | False
}
```
where:
* `rootConcepts` - will restrict indexing only to those classes subsumed under the list of top level HPO abnormalities provided; in the example above: `'HP:0001574', 'HP:0000478', 'HP:0000598', 'HP:0000707', 'HP:0000119'`
* `allow3LetterAcronyms` - 3 letter acronyms can lead to false positives due to their lexical ambiguity. This option enables their inclusion in the set of tokens associated with concepts. 
* `includeTopLevelCategory` - add extra information to all concepts indexed for text mining
* `allowDuplicateEntries` - allows for duplicated labels / synonyms to be indexed.

Use `IndexHPO` to create an index from an existing HPO version:
```python
    from FastHPOCR.IndexHPO import IndexHPO

    indexHPO = IndexHPO(<hpoFileLocation>, <outputFolder>, indexConfig=indexConfig)
    indexHPO.index()
```
where
* `hpoFileLocation` - path to the `hp.obo` file targeted for indexing
* `outputFolder` - path where the resulting index will be deposited

### Indexing SNOMED
Index configuration:
```python
indexConfig = {
    'rootConcepts': ['SCTID:64572001']
    'allow3LetterAcronyms': True | False,
    'includeTopLevelCategory': True | False,
    'allowDuplicateEntries': True | False
}
```
where:
* `rootConcepts` (**mandatory**) - will restrict indexing only to those classes subsumed under the list of top level HPO abnormalities provided; in the example above: `'SCTID:64572001'` or `'64572001'` (*Disease*)
* `allow3LetterAcronyms` (*optional*) - 3 letter acronyms can lead to false positives due to their lexical ambiguity. This option enables their inclusion in the set of tokens associated with concepts. 
* `includeTopLevelCategory` (*optional*) - add extra information to all concepts indexed for text mining
* `allowDuplicateEntries` (*optional*) - allows for duplicated labels / synonyms to be indexed.

Use `IndexSNOMED` to create an index from an existing SNOMED version using a given root concept:
```python
    from FastHPOCR.IndexSNOMED import IndexSNOMED

    indexSNOMED = IndexSNOMED(<descriptionFile>, <relationsFile>, <outputFolder>, indexConfig=indexConfig)
    indexSNOMED.index()
```
where
* `descriptionFile` - path to the SNOMED description file targeted for indexing - e.g., `sct2_Description_Full-en_INT_20230630.txt`
* `relationsFile` - path to the SNOMED relations file - e.g., `sct2_Relationship_Full_INT_20230630.txt`
* `outputFolder` - path where the resulting index will be deposited

**NOTE:** this functionality is intentionally targeting a particular branch of the terminology and not the terminology in its entirety. Hence, providing a `rootConcept` is mandatory.

### Indexing ORPHANET

Use `IndexORPHANET` to create an index from an existing HPO version:
```python
    from FastHPOCR.IndexORPHANET import IndexORPHANET

    indexORPHANET = IndexORPHANET(<orphaDataFile>, <outputFolder>)
    indexORPHANET.index()
```
where
* `orphaDataFile` - path to the unpacked JSON Orphanet data file (`en_product1.json`) containing the definitions of the disorders
* `outputFolder` - path where the resulting index will be deposited

### Concept recognition step

Use `HPOAnnotator`

```python
    from FastHPOCR.HPOAnnotator import HPOAnnotator

    hpoAnnotator = HPOAnnotator(<indexLocation>)

    # To annotate a piece of text and retrieve the resulting annotations
    annotations = hpoAnnotator.annotate(<text>)

    # To serialize the annotations on disk
    hpoAnnotator.serialize(annotations, <outFileName>, includeCategoriesIfPresent=True)
```
where:
* `includeCategoriesIfPresent` - can be set to `True | False` if additional information on the concepts should be provided (if this was originally included in the index via `includeTopLevelCategory` in `indexConfig`)