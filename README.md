# CheckM2
Rapid assessment of genome bins quality using machine learning. 

# Usage

#### Bin quality prediction
The main use of CheckM2 is likely going to be the prediction of the completeness and contamination of genomic bins. 

You can give it a folder with fasta files using `--genome-fasta-directory` and direct its output with `--output-directory`:
```
checkm2 predict --genome-fasta-directory <folder_with_bins> --threads 30 --output-directory <output_folder> 
```

If you already have predicted protein files (ideally using prodigal), you can pass the folder checkm2 using `--genes` option and set the file extension using `--extension`.

By default, the output folder will have a tab-delimited file `quality_report.tsv` containing the completeness and contamination information for each bin. You can also print the results to stdout by passing the `--stdout` option to `checkm predict`.

#### Low memory mode
If you are running CheckM2 on a device with limited RAM, you can use the --lowmem option to reduce DIAMOND RAM use by half at the expense of longer runtime. 

# Run without installing

For simplicity, you can just download CheckM2 from GitHub and run it directly without installing. 

Retrieve the files: 
```
git clone --recursive https://github.com/chklovski/checkm2.git && cd checkm2
```

Create an appropriate conda environment with prerequisites using the `checkm2.yml` file:
```
conda env create -n checkm2 -f checkm2.yml
conda activate checkm2
```

Finally, run CheckM2:
```
bin/checkm2 -h
```

# Installation

The easiest way to install is using conda. In the future. 

Alternatively, retrieve the github files: 

```
git clone --recursive https://github.com/chklovski/checkm2.git && cd checkm2
```

Then create a conda environment using the `checkm2.yml` file:
```
conda env create -n checkm2 -f checkm2.yml
conda activate checkm2
```

Finally, install CheckM2:
```
python setup.py install
```

Installation is then complete. To run checkm2, then you can
```
conda activate checkm2
checkm2 -h
```

# Database

You will also need to download and install the external DIAMOND database CheckM2 relies on for rapid annotation. 
Use `checkm2 database --download` to install it into your default /home/user/databases directory, 
or provide a custom location using `checkm2 database --download --path /custom/path/`

You can test that the CheckM2 installation was successfull using `checkm2 testrun`
