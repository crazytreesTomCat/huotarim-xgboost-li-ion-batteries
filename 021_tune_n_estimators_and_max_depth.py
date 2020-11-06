# battery 023, parallel cross validation
from pandas import read_csv
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import TimeSeriesSplit
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot
import numpy

# Load data
DIR = '../Logsn/ind_and_selBcol/v140/'
FILE = 'HPmth023.csv'
filename = DIR + FILE

# Use column labels 
names = ['BatteryStateOfCharge_Percent','A_mean','Wh_sum','DV','t_1','SOH']
dataset = read_csv(filename, usecols=names) 
array = dataset.values
X = array[:,0:len(names)-1]
y = array[:,len(names)-1]

# Split-out validation dataset to test and validation sets; last is SOH
array = dataset.values
X = array[:,0:len(names)-1]
y = array[:,len(names)-1]

# Split-out validation dataset to test and validation sets
test_size = 0.4
# IMPORTANT: keep time series order by shuffle=False
X_train, X_test, y_train, y_test = train_test_split(X, y,
test_size=test_size, shuffle=False)

# Grid search model hyperparameters for train set
model = XGBRegressor(nthread=-1)
n_estimators = [50,100,150,200]
max_depth= [2,4,6,8]
param_grid = dict(max_depth=max_depth, n_estimators=n_estimators)
tscv = TimeSeriesSplit(n_splits=5) # 5 or 9 yields the same result (tscv splits look different, though)
#grid_search = GridSearchCV(model, param_grid, scoring="explained_variance"/"neg_root_mean_squared_error"
#cv=tscv n_jobs=-1)
grid_search = GridSearchCV(model, param_grid, scoring="explained_variance", cv=tscv,n_jobs=-1)
grid_result = grid_search.fit(X_train, y_train)

# summarize results
print("Best explained variance score: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
means = grid_result.cv_results_['mean_test_score']
stds = grid_result.cv_results_['std_test_score']
params = grid_result.cv_results_['params']
for mean, stdev, param in zip(means, stds, params):
    print("%f (%f) with: %r" % (mean, stdev, param))

# plot results
scores = numpy.array(means).reshape(len(max_depth), len(n_estimators))
for i, value in enumerate(max_depth):
    pyplot.plot(n_estimators, scores[i], label='depth: ' + str(value))
pyplot.legend()
pyplot.xlabel('n_estimators')
pyplot.ylabel('Explained variance')
pyplot.savefig('n_estimators_vs_max_depth.png')