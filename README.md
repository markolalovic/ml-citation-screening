<img src="report/diagrams/general-overview/general-overview.png" alt="General overview of proposed framework" width="1500">

## Longevity Research Screening

This repository contains the source code for machine learning framework to semi-automate citation screening in systematic reviews and meta-analyses and all the tex files and figures for report and presentation slides.

The framework is mostly implemented in python and uses the logistic regression model from scikit-learn library. The front-end is implemented in JavaScript. The result are 3 interactive tables of exported documents accessible from a browser.

The framework was developed and evaluated in context of aging and longevity research studies and tested on a particular dataset related to "Dasatinib and Quercetin Senolytic Therapy Risk-Benefit Analysis" (D&Q Analysis) published by [Forever Healthy Foundation](https://brain.forever-healthy.org/display/EN/).

## Links:
* Technical report: [TODO](link)
* Presentation slides: [TODO](link)
* Interactive tables of exported documents for D&Q Analysis: [https://markolalovic.com/longevity-research-screening/
](https://markolalovic.com/longevity-research-screening/)
* MySQL database dump of the dataset for D&Q Analysis: [TODO](link)

## How-to
The framework was developed and tested on Ubuntu 20.04.1 LTS. Technical overview of proposed framework is shown in figure bellow:

<img src="report/diagrams/technical-overview/technical-overview.png" alt="Technical overview of proposed framework" width="1500">

In `src` directory is a `Makefile` that creates python virtual environment in	`./src/longevity-research-screening-venv` and installs all the dependencies from `./src/requirements.txt`.

For the simple model results, run:
```bash
$ cd src
$ make run
```

The full model uses extracted features from LDA topic model constructed using Java-based package for statistical natural language processing called `Mallet`. To build `Mallet` you need to have Java and Apache `ant` build tool installed. On Debian based distro, run:
```bash
sudo apt-get install default-jdk
sudo apt-get install ant
```

Then simply run `make full` which also downloads `Mallet` to `./src`:
```bash
$ cd src
$ make full
```

The framework uses a local MySQL database. To re-run the pre-processing steps you need to have mysql server installed. On Debian based distro, run:
```bash
$ sudo apt install mysql-server
```

To re-create the dataset for D&Q Analysis, run python script `create_database.py`:
```bash
$ python3 ./src/create_database.py
```

The script queries PubMed database with provided search terms devised by Forever Healthy foundation using `pymed` API. Additionally, it scrapes some data directly from websites of journals or clinical trials (Clinical-
Trials.gov) using `chromedriver`. Running `make full` also downloads `chromedriver` for scraping. The script creates a database called `longevity_research`. The retrieved data is saved into `longevity_research` database in `dasatinib_and_quercetin_senolytic_therapy` table.

## Citing this work
If you find this work useful, please consider citing it using the [Zenodo](link) record:
```
TODO
```

BibTeX entry:
```
TODO
```

## References

[1] Bannach-Brown, A., Przybyła, P., Thomas, J. et al. "Machine learning algorithms for systematic review: reducing workload in a preclinical review of animal studies and reducing human screening error.", Syst Rev 8, 23 (2019). [https://doi.org/10.1186/s13643-019-0942-7](https://doi.org/10.1186/s13643-019-0942-7)

[2] Howard BE, Phillips J, Miller K, et al. "SWIFT-Review: a text-mining workbench for systematic review.", Syst Rev. 2016;5:87. Published 2016 May 23. [https://doi:10.1186/s13643-016-0263-z](https://doi:10.1186/s13643-016-0263-z)

[3] O’Mara-Eves, A., Thomas, J., McNaught, J. et al. "Using text mining for study identification in systematic reviews: a systematic review of current approaches.", Syst Rev 4, 5 (2015). [https://doi.org/10.1186/2046-4053-4-5](https://doi.org/10.1186/2046-4053-4-5)

[4] Przybyła P, Brockmeier AJ, Kontonatsios G, et al. "Prioritising references for systematic reviews with RobotAnalyst: A user study.", Res Synth Methods. 2018;9(3):470-488. [https://doi.org/10.1002/jrsm.1311](https://doi.org/10.1002/jrsm.1311)

[5] Wallace, B.C., Trikalinos, T.A., Lau, J. et al. "Semi-automated screening of biomedical citations for systematic reviews.", BMC Bioinformatics 11, 55 (2010). [https://doi.org/10.1186/1471-2105-11-55](https://doi.org/10.1186/1471-2105-11-55)