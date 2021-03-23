# CheckM2
Rapid assessment of genome bins quality using machine learning. 

# Installation

The easiest way to install is using conda. In the future. 

Alternatively, retrieve the github files: 

```
git clone --recursive https://github.com/chklovski/checkm2.git && cd checkm2
```

Then create a conda environment using the `checkm2.yml` file:
```
conda env create -n checkm2 -f checkm2.yml
```

Finally, install CheckM2:
```
python setup.py build \ 
python setup.py install
```

# Database

You will also need to download and install the external DIAMOND database CheckM2 relies on for rapid annotation. 
Use `checkm2 database --download` to install it into your default /home/user/databases directory, 
or provide a custom location using `checkm2 database --download --path /custom/path/`

You can test that the CheckM2 installation was successfull using `checkm2 testrun`
