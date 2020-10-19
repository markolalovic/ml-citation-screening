# longevity-research-exploration
This repository contains a prototype of a simple tool to explore the latest research in aging, geroscience and longevity. As a start by keyword only. In the future also to help users evaluate and differentiate between articles with good methodology and promising results and articles not useful at all for the general public, especially those with unreproducible findings or findings that contradict other articles. 

More in this notebook:
https://observablehq.com/@markolalovic/exploring-research-papers-about-longevity

Data about the papers is from PubMed database using the API: pymed. As a start data consist of only the first 500 results when searching the database using the term: longevity. You can find the source code: here

TODO:

* Connect a larger database of data about papers or use a better API.
* Expand the search terms, e.g. "metformin".
* Rank the papers according to tf-idf.
* Calculate some indicators of trust, e.g. "suspicious funding".
* Calculate some measures, e.g. "reproducibility".
* Construct the ultimate measure of confidence using all of the above using machine learning model and help from the expert.

Ideas:
* Add evaluations, enable comments from users, e.g. about the "quality" of each paper, study or intervention.
* Create and visualize the citation network of the returned papers
* Plot the publication dates of the returned papers


