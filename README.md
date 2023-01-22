# CheckM2
Rapid assessment of genome bin quality using machine learning. 

Unlike CheckM1, CheckM2 has universally trained machine learning models it applies regardless of taxonomic lineage to predict the completeness and contamination of genomic bins. This allows it to incorporate many lineages in its training set that have few - or even just one - high-quality genomic representatives, by putting it in the context of all other organisms in the training set. As a result of this machine learning framework, CheckM2 is also highly accurate on organisms with reduced genomes or unusual biology, such as the Nanoarchaeota or Patescibacteria. 

CheckM2 uses two distinct machine learning models to predict genome completeness. The 'general' gradient boost model is able to generalize well and is intended to be used on  organisms not well represented in GenBank or RefSeq (roughly, when an organism is novel at the level of order, class or phylum). The 'specific' neural network model is more accurate when predicting completeness of organisms more closely related to the reference training set (roughly, when an organism belongs to a known species, genus or family). CheckM2 uses a cosine similarity calculation to automatically determine the appropriate completeness model for each input genome, but you can also force the use of a particular completeness model, or get the prediction outputs for both. There is only one contamination model (based on gradient boost) which is applied regardless of taxonomic novelty and works well across all cases. 

# Usage

#### Bin quality prediction
The main use of CheckM2 is to predict the completeness and contamination of metagenome-assembled genomes (MAGs) and single-amplified genomes (SAGs), although it can also be applied to isolate genomes. 

You can give it a folder with FASTA files using `--input` and direct its output with `--output-directory`:
```
checkm2 predict --threads 30 --input <folder_with_bins> --output-directory <output_folder> 
```

CheckM2 can also take a list of files in its `--input` parameter. It will work out automatically if it was given a folder or a list of files and process accordingly:
```
checkm2 predict --threads 30 --input ../bin1.fa ../../bin2.fna /some/other/directory/bin3.fasta --output-directory <output_folder> 
```
Checkm2 can also handle gzipped files. If passing a folder with gzip files, specify a *gz* --extension. If given a list of files, CheckM2 will work out automatically what to do and specifying an extension is **unnecesary**. It can also handle mixed lists of gzipped and non-gzipped files given to the --input command.   

If you already have predicted protein files (ideally using Prodigal), you can pass the files to Checkm2 with an additional `--genes` option to let it know to expect protein files.  

By default, the output folder will have a tab-delimited file `quality_report.tsv` containing the completeness and contamination information for each bin. You can also print the results to stdout by passing the `--stdout` option to `checkm predict`.

#### Low memory mode
If you are running CheckM2 on a device with limited RAM, you can use the --lowmem option to reduce DIAMOND RAM use by half at the expense of longer runtime. 

# Run without installing

For simplicity, you can just download CheckM2 from GitHub and run it directly without installing. 

Retrieve the files: 
```
git clone --recursive https://github.com/chklovski/checkm2.git && cd checkm2
```

Create an appropriate Conda environment with prerequisites using the `checkm2.yml` file:
```
conda env create -n checkm2 -f checkm2.yml
conda activate checkm2
```

Finally, run CheckM2:
```
bin/checkm2 -h
```

# Installation

The easiest way to install is using Conda. In the future. 

Alternatively, retrieve the Github files: 

```
git clone --recursive https://github.com/chklovski/checkm2.git && cd checkm2
```

Then create a Conda environment using the `checkm2.yml` file:
```
conda env create -n checkm2 -f checkm2.yml
conda activate checkm2
```

Finally, install CheckM2:
```
python setup.py install
```

This should take no longer than 5-10 mins on an average computer. Installation is then complete. To run Checkm2, then you can
```
conda activate checkm2
checkm2 -h
```

# Database

You will also need to download and install the external DIAMOND database CheckM2 relies on for rapid annotation. 
Use `checkm2 database --download` to install it into your default /home/user/databases directory, 
or provide a custom location using `checkm2 database --download --path /custom/path/`

The database path can also be set by setting the environmental variable CHECKM2DB using:
`export CHECKM2DB="path/to/database"`

# Test run

It is highly recommended to do a testrun with CheckM2 after installation and database download to ensure everything works successfully. 
You can test that the CheckM2 installation was successful using `checkm2 testrun`. This command should complete in < 5 mins on an average desktop computer. 

Testrun runs CheckM2's genome quality prediction models on three (complete, uncontaminated) test genomes from diverse lineages to ensure the process runs to completeness and the predictions within expected margins. These are: 


|Genome | GTDB taxonomy | CheckM1 Completeness  | CheckM1 Contamination|
|  :---:   |  :---:   |  :---:  |  :---:  |
|TEST1 | d__Bacteria;p__Proteobacteria;c__Gammaproteobacteria;o__Enterobacterales;f__Enterobacteriaceae;g__Escherichia;s__Escherichia coli |99.97| 0.04|
|TEST2 | d__Bacteria;p__Patescibacteria;c__Dojkabacteria;o__SC72;f__SC72;g__UBA5209;s__UBA5209 sp002840365 | 79.86 | 0.00|
|TEST3 | d__Archaea;p__Nanohaloarchaeota;c__Nanosalinia;o__Nanosalinales;f__Nanosalinaceae;g__Nanohalobium;s__Nanohalobium sp001761425 | 87.77 |0.00| 
