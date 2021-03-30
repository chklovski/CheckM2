import os
from pathlib import Path


class DefaultValues():
    """Default values for filenames and common constants."""
    DATA_PATH =  os.path.join(os.path.dirname(__file__), 'data')
    MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models')
    VERSION_PATH = os.path.join(os.path.dirname(__file__), 'version')
    TESTRUN_GENOMES = os.path.join(os.path.dirname(__file__), 'testrun')

    PRODIGAL_FOLDER_NAME = 'protein_files'

    #LOGNAME = 'log.txt'

    DIAMOND_QUERY_COVER = 80
    DIAMOND_SUBJECT_COVER = 80
    DIAMOND_PERCENT_ID = 30
    DIAMOND_EVALUE = 1e-05

    DIAMOND_DEFAULT_CHUNK_SIZE = 500

    DIAMOND_HEADER_SEPARATOR = 'Ω'


    DB_LOCATION_DEFINITION = os.path.join(VERSION_PATH, 'diamond_path.json')
    DB_VAR = "CHECKM2DB"
    try:
        DEFAULT_DB_INSTALL_LOCATION = os.path.join(str(Path.home()), 'databases')
    except:
        pass


    FEATURE_ORDER_LOCATION = os.path.join(DATA_PATH, 'feature_ordering.json')
    PATH_CATEGORY_MAPPING_LOCATION = os.path.join(DATA_PATH, 'kegg_path_category_mapping.json')
    MODULE_DEFINITION_LOCATION = os.path.join(DATA_PATH, 'module_definitions.json')

    GENERAL_MODEL_COMP_LOCATION = os.path.join(MODEL_PATH, 'general_model_COMP.MODEL')
    SPECIFIC_MODEL_COMP_LOCATION = os.path.join(MODEL_PATH, 'specific_model_COMP.hd5')

    GENERAL_MODEL_CONT_LOCATION = os.path.join(MODEL_PATH, 'general_model_CONT.MODEL')
    SPECIFIC_MODEL_CONT_LOCATION = os.path.join(MODEL_PATH, 'specific_model_CONT.hd5')

    SCALER_FILE_LOCATION = os.path.join(MODEL_PATH, 'scaler.sav')
    REF_DATA_LOCATION = os.path.join(DATA_PATH, 'min_ref_rsdata_v1.npz')

    EXTERNAL_FILES_TO_VERIFY = [FEATURE_ORDER_LOCATION, PATH_CATEGORY_MAPPING_LOCATION,
                                MODULE_DEFINITION_LOCATION, GENERAL_MODEL_COMP_LOCATION,
                                SPECIFIC_MODEL_COMP_LOCATION, GENERAL_MODEL_CONT_LOCATION,
                                SPECIFIC_MODEL_CONT_LOCATION, SCALER_FILE_LOCATION, REF_DATA_LOCATION]

    #Anything below this is general-model determined
    COSINE_SIMILARITY_SPECIFIC_MODEL_CUTOFF = 0.775
