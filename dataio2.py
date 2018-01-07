
from blockchain import statistics
import pandas as pd
import numpy as np
import os as os
from sklearn.linear_model import LinearRegression 


def dl_blockchain_data():    
    stat_names = ['market-price', 'avg-block-size', 'n-transactions'
                  ,'total-bitcoins', 'market-cap', 'trade-volume'
                   ,'blocks-size'
                   , 'n-orphaned-blocks'
                   , 'n-transactions-per-block'
                   ,'median-confirmation-time'
                   #, 'nya-support'
                   ,'hash-rate', 'difficulty', 'miners-revenue'
                   ,'n-unique-addresses', 'n-transactions-total'
                   #, 'transactions-per-second','mempool-count', 'mempool-growth', 'mempool-size','utxo-count'
                   , 'n-transactions-excluding-popular', 'n-transactions-excluding-chains-longer-than-100', 'output-volume'
                   ,'estimated-transaction-volume', 'estimated-transaction-volume-usd'
                   #, 'my-wallet-n-users'    
    
                  ]
    i = 0
    all_data = pd.DataFrame()
    for stat_name in stat_names:
        raw = statistics.get_chart(stat_name, 
                             time_span = '5years',
                             rolling_average = '24hours'
                             )
        date = []
        val = []
        for value in raw.values:
            date.append(value.x)
            val.append(value.y)
        data = pd.DataFrame({'date' : date,
                             stat_name : val})
        data['date'] = pd.to_datetime(data['date'], unit='s')
        if(i==0):
            all_data = data
        else:
            all_data = pd.merge(all_data, data, on = 'date', how = 'left')
        i += 1
    all_data.to_csv('data/blockchain_stat.csv', index = False)

def get_blockchain_data(isFresh):
    if isFresh:
        dl_blockchain_data()
    else:
        if os.path.isfile('data/blockchain_stat.csv'):
            return(pd.read_csv('data/blockchain_stat.csv'))
        else:
            dl_blockchain_data()
    return(pd.read_csv('data/blockchain_stat.csv'))

def create_xy_dataset(isFresh = False):
    data = get_blockchain_data(isFresh)    
    y = data.loc[1:, 'market-price']
    X = data[:-1]
    y = data.loc[1:, 'market-price'].values > X['market-price'].values 
             
       
    # generate lag features
    lag = 3
    X = transforming_X(X, lag)
    y = y[lag:]

    return X, y    

def get_predict_value():
    data = get_blockchain_data(True)    
    return transforming_X(data, lag = 3)

def transforming_X(X_input, lag):
    X = fix_na_trade_vol(X_input)
    X = feature_engineering(X)
    
    # Transform some feature into log data
    X['market-price'] = np.log(X['market-price'])
    X['avg-block-size'] = np.log(X['avg-block-size'])
    #X['n-transactions'] = np.log(X['n-transactions'])
    X['market-cap'] = np.log(X['market-cap'])
    #X['blocks-size'] = np.log(X['blocks-size'])
    #X['median-confirmation-time'] = np.log(X['median-confirmation-time'])
    #X['hash-rate'] = np.log(X['hash-rate'])
    X['difficulty'] = np.log(X['difficulty'])
    #X['miners-revenue'] = np.log(X['miners-revenue'])
    X['n-unique-addresses'] = np.sqrt(X['n-unique-addresses'])
    #X['n-transactions-excluding-popular'] = np.log(X['n-transactions-excluding-popular'])
    X['n-transactions-excluding-chains-longer-than-100'] = np.log(X['n-transactions-excluding-chains-longer-than-100'])
    X['estimated-transaction-volume-usd'] = np.log(X['estimated-transaction-volume-usd'])
    X['cost-per-transaction-percent'] = np.log(X['cost-per-transaction-percent'])
    #==============================================================================
    #X['trade-volume'] = np.sqrt(X['trade-volume'])
    feature_names  = ['market-price', 'median-confirmation-time']
    for i in range(lag):
        for feature_name in feature_names:
            X = gen_lag_dif_ratio_feature(X, feature_name, i + 1)    
    
    X = X.iloc[lag:,]
    X = X.reset_index()
    
        # Remove unusing features
    X = X.drop(['date','index'
             , 'n-transactions-per-block'
             , 'output-volume'
             #,'estimated-transaction-volume' 
             , 'n-transactions-total'
             , 'output-volume'
             , 'blocks-size'
             , 'total-bitcoins'
             , 'difficulty'
             
             ], 1)
    return X
    

def feature_engineering(data):
    data['cost-per-transaction-percent'] = data['miners-revenue'].values / data['n-transactions'].values 
    #data['n-transactions-excluding-popular-ratio'] = data['n-transactions-excluding-popular'].values / data['n-transactions'].values 
    data['n-transactions-excluding-chains-longer-than-100-ratio'] = data['n-transactions-excluding-chains-longer-than-100'].values / data['n-transactions'].values 
    data['transaction-to-trade-ratio'] = data['estimated-transaction-volume'].values / data['trade-volume'].values 
 
    return data

def fix_na_trade_vol(data):
    reg = LinearRegression()
    x = data['estimated-transaction-volume-usd'].values
    y = data['trade-volume'].values
    nan_loc = np.isnan(y)        
    # remove nan value
    x_rmna = x[np.logical_not(nan_loc)]
    y_rmna = y[np.logical_not(nan_loc)]
    reg.fit(x_rmna.reshape(len(x_rmna), 1), y_rmna)    
    y_prd = reg.predict(x.reshape(len(x), 1))
    
    data.loc[nan_loc, 'trade-volume'] = y_prd[nan_loc]
    
    return data

def gen_lag_dif_ratio_feature(data, feature_name, lag = 1):
    lag_val = data[feature_name].shift(lag)
    data[feature_name + '-lag' + str(lag) + '-dif'] = (data[feature_name] - lag_val) / data[feature_name] 
    return data
    
#data = gen_lag_feature(X, 'trade-volume')

    