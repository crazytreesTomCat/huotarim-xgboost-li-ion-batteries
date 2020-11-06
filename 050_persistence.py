# battery 023, naive prediction a.k.a persistance
#
# naive forecast strategies for the power usage dataset
from math import sqrt
from numpy import split
from numpy import array
from numpy import mean
from numpy import std
from pandas import read_csv
from pandas import to_datetime
from sklearn.metrics import mean_squared_error
from sklearn.metrics import explained_variance_score 
from sklearn.metrics import mean_absolute_error 
from sklearn.metrics import r2_score
#from matplotlib import pyplot

# Walk-forward validation for naive forecast a.k.a persistance as the baseline
#
# split a big dataset into train1/ test1 sets; use only train1 here for validation 
def train_test_split_all(data, n_testratio):
    n_test = int(len(data) * n_testratio)
    return data[:-n_test], data[-n_test:]

# load data
DIR = '../Logsn/ind_and_selBcol/v140/'
FILE = 'HPmth023.csv'
filename = DIR + FILE

# Use lables
names = ['SOH']
data = read_csv(filename, usecols=names)
data = data.values

# split all data to train and test; use train only for walk-forward validation
test_ratio= 0.4
train, test = train_test_split_all(data, test_ratio)

# walk-forward validation
history = [x for x in train]
predictions = list()
for i in range(len(test)):
    # predict
    yhat = history[-1]
    predictions.append(yhat)
    # observation
    obs = test[i]
    history.append(obs)
    print('Predicted=%.3f, Expected=%.3f' % (yhat, obs))

# Evaluate predictions
evc = explained_variance_score(test, predictions)
print("Explained variance: %.2f%%" % (evc * 100.0))
mae = mean_absolute_error(test, predictions)
print("Mean absolute error: %.2f" % (mae)) 
rmse = sqrt(mean_squared_error(test, predictions))
print("RMSE: %.2f" % (rmse)) 
r2 = r2_score(test, predictions)
print("R2: %.2f" % (r2)) 