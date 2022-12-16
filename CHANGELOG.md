# CHANGELOG.md

## 1.0.0 (2022-12-16)

First official release of CheckM2!

This release uses models built on [**GTDB release 202**]. 

This release uses the DIAMOND database version 2, available at DOI [**10.5281/zenodo.5571251**]. 

New features in this release:

  - CheckM2 now has tagged releases and a changelog summary. This addresses (https://github.com/chklovski/CheckM2/issues/25, https://github.com/chklovski/CheckM2/issues/22), as well as allows submission to PyPI and Bioconda (https://github.com/chklovski/CheckM2/issues/29, https://github.com/chklovski/CheckM2/issues/7)
  - CheckM2 now has logging enabled. Logs will be saved in the output folder in the file 'checkm2.log' (Resolves https://github.com/chklovski/CheckM2/issues/2)
  - You can now optionally remove intermediate files (protein files and diamond output) using the `--remove_intermediates` option (Resolves https://github.com/chklovski/CheckM2/issues/3)
  - CheckM2 now checks for diamond database and loads machine learning models before proceeding with main workflow (Resolves https://github.com/chklovski/CheckM2/issues/4)
  - CheckM2 now reports coding density for bins, as well as contig N50, average gene length, genome length and GC content. This gives the user more information and can help identify issues such as e.g. frameshift-dominated genomes
  - Processing feature vectors and predicting completeness and contamination is now chunked by groups of genomes (default 250) instead of holding all feature vectors in memory. This drastically reduces RAM usage by CheckM2. 
  - You can now specify a specific coding table that Prodigal should use for your bins using the `--ttable` flag. By default, CheckM2 chooses between 4 or 11 based on coding density information. 
  - CheckM2 now forces tensorflow models to run using CPU (this should address https://github.com/chklovski/CheckM2/issues/26, https://github.com/chklovski/CheckM2/issues/12). For better compatibility, it is strongly suggested to initially install the CheckM2 conda environment on a computer without a GPU
  - CheckM2 should now use tensorflow release < 2.6.0 (this should address https://github.com/chklovski/CheckM2/issues/16)
  - CheckM2 can reuse prodigal and diamond output using the `--resume` flag (addresses https://github.com/chklovski/CheckM2/issues/13, thanks to JeanMainguy for implementation)


## 0.1.3 (2022-07-18)

Features:

  - More informative error handling
  - Add low confidence warning if completeness models substantially disagree

## 0.1.2 (2022-07-6)

Bugfixes:

  - Fix incorrect cosine similarity calculations and use novelty ratio for simpler calculations and model selection.