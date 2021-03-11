# Longevity Research Screening

**A Simple Machine Learning Framework for Citation Screening of Aging and Longevity Research Studies**

<p align="center">
<img src="report/diagrams/general-overview/general-overview.png" alt="General overview of proposed framework" width="1500">
</p>

## Introduction

This repository contains the source code of a research project to develop a machine learning framework to semi-automate citation screening in systematic reviews and meta-analyses.

The framework was developed and evaluated in context of aging and longevity research studies and tested on a particular dataset related to "Dasatinib and Quercetin Senolytic Therapy Risk-Benefit Analysis" (D&Q Analysis) published by [Forever Healthy Foundation](https://brain.forever-healthy.org/display/EN/). The results are in 3 interactive tables of exported documents accessible [here](https://markolalovic.com/longevity-research-screening/).

You can find tech report [here](https://zenodo.org/record/4593957/files/zenodo.4593957.pdf) or check presentation [slides](https://zenodo.org/record/4594866/files/slides.pdf) for a quick overview.

---

## Results

Below are the results of 5-fold cross-validation we got on D&Q Analysis dataset.

| Fold | Precision | Recall | PR-AUC  | WSS@R |
| ---- |:---------:|:------:|:------:|:-----:|
| 1 | 0.13 | 0.94 | 0.54 | 0.53 |
| 2 | 0.16 | 0.90 | 0.33 | 0.61 |
| 3 | 0.14 | 1.00 | 0.48 | 0.63 |
| 4 | 0.19 | 0.94 | 0.54 | 0.67 |
| 5 | 0.20 | 0.97 | 0.43 | 0.71 |

Below are PR-Curves and WSS@R-Curves we got on D&Q Analysis dataset.

<p align="center">
<img src="report/figures/performance-evaluation/combined/performance-evaluation.png" alt="Performance Evaluation Curves" width="1500">
</p>


## Installation

The code is tested with Ubuntu 20.04.1 LTS. The framework is implemented in Python and uses JavaScript for the font-end. In './src' directory is a `Makefile` that creates Python virtual environment in `./src/longevity-research-screening-venv` and installs all the dependencies from `./src/requirements.txt`.

## Usage
Below is an overview of the proposed framework.

<p align="center">
<img src="report/diagrams/technical-overview/technical-overview.png" alt="Technical overview of proposed framework" width="1500">
</p>

### Running the Model
To reproduce the experimental results one can use the `Makefile` in `./src/`.

For the results of a simple model that uses only binary features, run:
```bash
cd src
make run
```

You should see the results and updated plots in `figures` directory.

The full model uses extracted features from LDA topic model constructed using Java-based package for statistical natural language processing called `Mallet`. To build `Mallet` you need to have Java and Apache `ant` build tool installed. On Debian based distro, run:
```bash
sudo apt-get install default-jdk
sudo apt-get install ant
```

Then simply run `make full` which also downloads `Mallet` to `./src`:
```bash
cd src
make full
```

### Pre-processing
The framework uses a local MySQL database. To re-run the pre-processing steps you need to have mysql server installed. On Debian based distro, run:
```bash
sudo apt install mysql-server
```

Then import the database dump (5.4 MB) of the dataset for D&Q Analysis: [longevity_research.sql](https://zenodo.org/record/4593916/files/longevity_research.sql) into the local MySQL database.

Then, to execute all the pre-processing steps, run:
```bash
python3 preprocess_articles.py
```


### Creating a Dataset
Besides mysql server you need to also have `chromedriver` tool for web-scraping. On Debian based distro you can download the latest release of `chromedriver` to `.src` directory by running `get_chromedriver.sh` script in `src` dir:
```bash
cd src
./get_chromedriver.sh
```

Then, to re-create the dataset for D&Q Analysis, run the Python script `create_database.py`:
```bash
python3 ./src/create_database.py
```

The script queries PubMed database with provided search terms devised by Forever Healthy foundation using `pymed` API. Additionally, it scrapes some data directly from websites of journals or clinical trials (Clinical-
Trials.gov) using `chromedriver`. The script creates a database called `longevity_research`. The retrieved data is saved into `longevity_research` database in `dasatinib_and_quercetin_senolytic_therapy` table.

It takes some time for the script to finish since it waits a certain time interval between calling get, to avoid to many requests in short time. The script prints the estimated time for scraping when started.

## Related Work
[1] Bannach-Brown, A., Przybyła, P., Thomas, J. et al. "Machine learning algorithms for systematic review: reducing workload in a preclinical review of animal studies and reducing human screening error.", Syst Rev 8, 23 (2019). [https://doi.org/10.1186/s13643-019-0942-7](https://doi.org/10.1186/s13643-019-0942-7)

[2] Howard BE, Phillips J, Miller K, et al. "SWIFT-Review: a text-mining workbench for systematic review.", Syst Rev. 2016;5:87. Published 2016 May 23. [https://doi:10.1186/s13643-016-0263-z](https://doi:10.1186/s13643-016-0263-z)

[3] O’Mara-Eves, A., Thomas, J., McNaught, J. et al. "Using text mining for study identification in systematic reviews: a systematic review of current approaches.", Syst Rev 4, 5 (2015). [https://doi.org/10.1186/2046-4053-4-5](https://doi.org/10.1186/2046-4053-4-5)

[4] Przybyła P, Brockmeier AJ, Kontonatsios G, et al. "Prioritising references for systematic reviews with RobotAnalyst: A user study.", Res Synth Methods. 2018;9(3):470-488. [https://doi.org/10.1002/jrsm.1311](https://doi.org/10.1002/jrsm.1311)

[5] Wallace, B.C., Trikalinos, T.A., Lau, J. et al. "Semi-automated screening of biomedical citations for systematic reviews.", BMC Bioinformatics 11, 55 (2010). [https://doi.org/10.1186/1471-2105-11-55](https://doi.org/10.1186/1471-2105-11-55)

## Citing this Work
If you find this work useful, please cite:
```
Lalović, Marko. (2021, March 10). A Simple Machine Learning Framework to Aid Citation Screening in Systematic Reviews and Meta-Analyses of Aging and Longevity Research Studies. Zenodo. http://doi.org/10.5281/zenodo.4593957
```
Or by using [bib entry](https://zenodo.org/record/4593957/export/hx#.YEk4RftKhH4).

## License
The code is released under MIT License. See the LICENSE file for more details.