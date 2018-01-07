import os
#os.chdir('/home/duytruong/Working Folder/home project')
from dataio2 import *
from kraken import * 
from _config.settings import *


import time
import pickle
import logging
from xgboost import XGBClassifier

def train_model():
    X, y = create_xy_dataset(True)
    cmodel = XGBClassifier()
    cmodel.fit(X, y)
    pickle.dump(cmodel, open("models/xgboost.pickle.dat", "wb"))

def load_model():
    cmodel = pickle.load(open("models/xgboost.pickle.dat", "rb"))
    return cmodel
    
def retrain_model(logger):
    if time.strftime("%d") == '01' or time.strftime("%d") == '15':
        logger.info('Retraining model')
        train_model()
    else:
        logger.info('Keep old model')

def is_bought():
    return os.path.isfile(settings['buying_hist_file']) 

                    
def predict_next_day_sign():
    X = get_predict_value()
    model = load_model()
    sign = model.predict(X)
     
    return sign[-1]

def action(logger, predicted_sign):
    if predicted_sign:
        logger.info('Predict price go up')
        if is_bought():
            logger.info('Already bought!!')
        else:
            logger.info('Buying coin initiated')
            buy_coin(logger)
    else:
        logging.info('Predict price go down')
        if is_bought():
            logger.info('Selling coin initiated')
            sell_coin(logger)
        else:
            logger.info('Do not have coin to sell!!')
    get_balance(logger)
    
def main():
    logging.basicConfig(filename = settings['log'], format='%(asctime)s %(message)s', level=logging.INFO, datefmt='%d-%m-%Y:%H:%M:%S')
    logger = logging.getLogger('stackoverflow_rocks')

    # Retrain model 2 times per month, on the 1st and 15th day of the month 
    retrain_model(logger)
    # Load model &Predict tomorrow sign
    predicted_sign = predict_next_day_sign()
    # Action
    action(logger, predicted_sign)
