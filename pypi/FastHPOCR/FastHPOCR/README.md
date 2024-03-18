# FastHPOCR

**FastHPOCR** is a phenotype concept recognition package using the Human Phenotype Ontology to extract concepts from free text. 
The solution relies on the fundamental pillars of concept recognition in order to cover its two underlying components - boundary detection and entity linking:
* Understanding the domain challenges - in the case of phenotypes, lexical variability
* Understanding the target ontology - and hence processing the ontology terms appropriately for text mining
More concretely, it uses a pre-built large collection of clusters of morphologically-equivalent tokens - to address lexical variability - and to reduce the boundary detection step to spans containing only tokens belonging to ontology concepts. Pre-processing the domain knowledge to create the collection of clusters was performed using OpenAI’s gpt-4.0 model and the resulting vocabulary contains 573,507 tokens, which leads to virtually no updates needed.

**FastHPOCR** was built for speed:
* Indexing a new ontology version takes ~3min
* Performing concept recognition on plain text: ~5s for 10,000 publication abstracts

## Usage

### Indexing step

Use `IndexHPO` to create an index from an existing HPO version:
```python
    from FastHPOCR.IndexHPO import IndexHPO

    indexHPO = IndexHPO(<hpoFileLocation>, <outputFolder>)
    indexHPO.index()
```
where
* `hpoFileLocation` is the path to the `hp.obo` file targeted for indexing
* `outputFolder` is the path where the resulting index will be deposited


### Concept recognition step

Use `HPOAnnotator`

```python
    from FastHPOCR.HPOAnnotator import HPOAnnotator

    hpoAnnotator = HPOAnnotator(<indexLocation>)

    # To annotate a piece of text and retrieve the resulting annotations
    annotations = hpoAnnotator.annotate(<text>)

    # To serialize the annotations on disk
    hpoAnnotator.serialize(annotations, <outFileName>)
```