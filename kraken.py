import krakenex
import os 
import time 
import logging 
from _config.settings import *


def buy_coin(logger, volume = '0.01', retry_in_sec = 5):
    kraken = krakenex.API()
    kraken.load_key(settings['api_key'])
 
    isExecuted = False
    while(isExecuted == False):
        try:
            response = kraken.query_private('AddOrder',
                                            {'pair': 'XXBTZUSD',
                                             'type': 'buy',
                                             'ordertype': 'market',
                                             'volume': volume})
        except:
            logger.info('Error execute query')
            time.sleep(retry_in_sec)
        else:
            for status, response_text in response.items():
                if status != 'error':
                    logger.info(response_text[0])
            logger.info(response_text[0])             
    
def sell_coin(logger, volume = '0.01', retry_in_sec = 5):
    kraken = krakenex.API()
    kraken.load_key(settings['api_key'])    
    isExecuted = False
    while(isExecuted == False):
        try:
            response = kraken.query_private('AddOrder',
                                            {'pair': 'XXBTZUSD',
                                             'type': 'sell',
                                             'ordertype': 'market',
                                             'volume': volume})
        except:
            logger.info('Error execute query')
            time.sleep(retry_in_sec)
        else:
            for status, response_text in response.items():
                if status != 'error':
                    os.remove(settings['buying_hist_file'])
                    
            logger.info(response_text[0])     

def get_balance(logger, retry_in_sec = 5):
    kraken = krakenex.API()
    kraken.load_key(settings['api_key'])
    isExecuted = False
    while(isExecuted == False):
        try:
            response = kraken.query_private('Balance')
        except:
            logger.info('Error execute query')
            time.sleep(retry_in_sec)
        else:
            isExecuted = True
            for status, response_text in response.items():
                print(status, response_text)
                if status == 'result':
                    logger.info(response_text)
                       

    