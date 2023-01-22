from setuptools import setup, find_packages

setup(
    name='CheckM2',
    version='1.0.1',
    packages=find_packages(),
    data_files=[('data', ['checkm2/data/feature_ordering.json', 'checkm2/data/kegg_path_category_mapping.json',
                          'checkm2/data/min_ref_rsdata_v1.npz', 'checkm2/data/module_definitions.json']),
                ('models', ['checkm2/models/specific_model_COMP.hd5', 'checkm2/models/cosine_table.pkl', 
                            'checkm2/models/model_CONT.gbm', 'checkm2/models/general_model_COMP.gbm', 'checkm2/models/scaler.sav']),
                ('version', ['checkm2/version/diamond_path.json', 'checkm2/version/version_hashes_1.0.1.json']),
                ('testrun', ['checkm2/testrun/TEST1.tst', 'checkm2/testrun/TEST2.tst', 'checkm2/testrun/TEST3.tst'])],
    include_package_data=True,
    url='https://github.com/chklovski/CheckM2',
    license='',
    install_requires=('python>=3.6, <3.9',
                      'h5py==2.10.0',
                      'scikit-learn==0.23.2',
                      'numpy==1.19.2',
                      'diamond==2.0.4',
                      'scipy',
                      'pandas<=1.4.0',
                      'tensorflow>=2.1.0, <2.6.0',
                      'lightgbm==3.2.1',
                      'requests',
                      'prodigal>=2.6.3',
                      'tqdm',
                      'packaging'
                      'requests',
                      'setuptools'
                      ),
        
    author='Alex Chklovski',
    scripts=['bin/checkm2'],
    author_email='chklovski@gmail.com',
    description='CheckM2 - Predicting the quality of metagenome-recovered bins'
)
