from checkm2.defaultValues import DefaultValues
import scipy
from scipy import sparse
from scipy.sparse import csr_matrix
import numpy as np
import logging
import sys
import os

class modelProcessor:

    def __init__(self, threads=1):
        #self.logger = logging.getLogger('timestamp')

        try:
            self.ref_data = scipy.sparse.load_npz(DefaultValues.REF_DATA_LOCATION)
        except:
            logging.error("Error: Reference data could not be loaded.")
            sys.exit(1)

        self.threads = threads
        self.similarity_cutoff = DefaultValues.COSINE_SIMILARITY_SPECIFIC_MODEL_CUTOFF

        #Returns cosine similarity matrix
    def __calculate_sparse_CSM(self, A, B):


        #Reshape is require to deal with scipy's deviation from numpy calculations
        num = np.dot(A, B.T)

        p1 = np.sqrt(np.sum(A.power(2), axis=1))[:, np.newaxis]
        p1 = p1.reshape(p1.shape[0], p1.shape[1])

        p2 = np.sqrt(np.sum(B.power(2), axis=1))[np.newaxis, :]
        p2 = p2.reshape(p2.shape[0], p2.shape[1])

        return np.array(num / (p1 * p2))



    def __calculate_cosine_similarity(self, feature_vector):
        #Todo - if input is big, we might need to chunk it so as not to overload RAM (depends on ref data size). Run some tests how much RAM is used/needed

        csm = self.__calculate_sparse_CSM(self.ref_data, csr_matrix(feature_vector))
        #return array of closest matches in ref database

        return np.amax(csm, axis=0)

    def calculate_general_specific_ratio(self, feature_vector, general_comp, general_cont, specific_comp, specific_cont):
        csm_array = self.__calculate_cosine_similarity(csr_matrix(feature_vector))
        specific_bool_mask = (csm_array > DefaultValues.COSINE_SIMILARITY_SPECIFIC_MODEL_CUTOFF)

        final_completeness = np.where(specific_bool_mask, specific_comp, general_comp)
        final_contamination = np.where(specific_bool_mask, specific_cont, general_cont)

        models_chosen = ['Specific (NeuralNetwork)' if specific else 'General (GradientBoost)' for specific in specific_bool_mask]

        return final_completeness, final_contamination, models_chosen, csm_array




