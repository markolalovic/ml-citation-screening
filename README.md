# longevity-research-exploration
Building a prototype of a simple tool to explore the latest research in aging, geroscience and longevity. As a start by keyword only.

The idea is to build a tool to help users evaluate and differentiate between anti-aging interventions with promising results and those with questionable results, e.g. based on unreproducible findings or contradicting other findings.

Data is a small subset of [PubMed](https://pubmed.ncbi.nlm.nih.gov/) database using [pymed](https://pypi.org/project/pymed/) API. You can find the demo: [here](https://observablehq.com/@markolalovic/exploring-research-papers-about-longevity).


Ideas:

* Expand the search terms to:
    * interventions (e.g.: "calorie restriction")
    * medications (e.g.: "metformin")
    * biomarkers (e.g.: "DHEA-S")
* Build a search query from questions (e.g.: "Does protein restriction slow aging?")
* Build a list of interventions and try to evaluate each one using the database of papers
