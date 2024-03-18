import setuptools

setuptools.setup(
	name="FastHPOCR",
	version="0.0.1",
	author="Tudor Groza",
	description="FastHPOCR is a phenotype concept recognition package using the Human Phenotype Ontology to extract concepts from free text.",
	package_data={'': ['license.txt','README.md','resources/base-synonyms','resources/vocab.clusters.list']},
	include_package_data=True,
	packages=["FastHPOCR","FastHPOCR.cr","FastHPOCR.index","FastHPOCR.util"]
)