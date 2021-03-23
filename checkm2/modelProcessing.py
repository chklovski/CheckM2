import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

from checkm2.defaultValues import DefaultValues
import xgboost as xgb
from tensorflow import keras
from sklearn.preprocessing import MinMaxScaler
import pickle
import logging
import sys
import os


class modelProcessor:

    def __init__(self, threads):


        self.nthreads = threads

        try:
            self.general_model_comp_xgb = xgb.Booster({'nthread': threads})  # init model
            self.general_model_comp_xgb.load_model(DefaultValues.GENERAL_MODEL_COMP_LOCATION)

            self.general_model_cont_xgb = xgb.Booster({'nthread': threads})  # init model
            self.general_model_cont_xgb.load_model(DefaultValues.GENERAL_MODEL_CONT_LOCATION)


            self.specific_model_comp_nn = keras.models.load_model(DefaultValues.SPECIFIC_MODEL_COMP_LOCATION)
            self.specific_model_cont_nn = keras.models.load_model(DefaultValues.SPECIFIC_MODEL_CONT_LOCATION)

            self.minmax_scaler = pickle.load(open(DefaultValues.SCALER_FILE_LOCATION, 'rb'))

            if logging.root.level == logging.DEBUG:
                self.verbosity = 1
            else:
                self.verbosity = 0

        except:
            logging.error("Saved models could not be loaded.")
            sys.exit(1)


    def run_prediction_general(self, vector_array):
        dtest = xgb.DMatrix(data=vector_array, nthread=self.nthreads)

        comp_predictions = self.general_model_comp_xgb.predict(dtest)
        comp_predictions[comp_predictions > 100] = 100

        cont_predictions = self.general_model_cont_xgb.predict(dtest)

        comp_predictions[comp_predictions < 0] = 0
        cont_predictions[cont_predictions < 0] = 0

        return comp_predictions.flatten(), cont_predictions.flatten()


    def run_prediction_specific(self, vector_array, specific_model_vector_len):

        scaled_vector = self.minmax_scaler.transform(vector_array)

        #re-shape into keras-cnn-appropriate array
        scaled_vector = scaled_vector.reshape(scaled_vector.shape[0], scaled_vector.shape[1], 1)

        #only using genes for specific predictions
        comp_predictions = self.specific_model_comp_nn.predict(scaled_vector[:, :specific_model_vector_len], verbose=self.verbosity)

        #as we're using sigmoid output for completeness model, convert to 100-scale
        comp_predictions = comp_predictions * 100

        cont_predictions = self.specific_model_cont_nn.predict(scaled_vector[:, :specific_model_vector_len], verbose=self.verbosity)

        comp_predictions[comp_predictions < 0] = 0
        cont_predictions[cont_predictions < 0] = 0

        return comp_predictions.flatten(), cont_predictions.flatten(), scaled_vector.reshape(scaled_vector.shape[0], scaled_vector.shape[1])

