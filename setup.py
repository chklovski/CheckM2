from setuptools import setup, find_packages

setup(
    name='CheckM2',
    version='1.1.0',
    packages=find_packages(),
    data_files=[('data', ['checkm2/data/feature_ordering.json', 'checkm2/data/kegg_path_category_mapping.json',
                          'checkm2/data/min_ref_rsdata_v1.npz', 'checkm2/data/module_definitions.json']),
                ('models', ['checkm2/models/specific_model_COMP.keras', 'checkm2/models/cosine_table.pkl', 
                            'checkm2/models/model_CONT.gbm', 'checkm2/models/general_model_COMP.gbm', 'checkm2/models/scaler.sav']),
                ('version', ['checkm2/version/diamond_path.json', 'checkm2/version/version_hashes_1.1.0.json']),
                ('testrun', ['checkm2/testrun/TEST1.tst', 'checkm2/testrun/TEST2.tst', 'checkm2/testrun/TEST3.tst'])],
    include_package_data=True,
    url='https://github.com/chklovski/CheckM2',
    license='',
    install_requires=(),
    author='Alex Chklovski',
    scripts=['bin/checkm2'],
    author_email='chklovski@gmail.com',
    description='CheckM2 - Predicting the quality of metagenome-recovered bins'
)
