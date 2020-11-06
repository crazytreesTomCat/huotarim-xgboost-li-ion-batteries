# spot check machine learning algorithms on a battery
from numpy import mean
from numpy import std
from pandas import read_csv
from matplotlib import pyplot
from sklearn import model_selection
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.model_selection import TimeSeriesSplit
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import AdaBoostRegressor
#from sklearn.ensemble import RandomForestRegressor
#from sklearn.ensemble import GradientBoostingRegressor
#from sklearn.ensemble import BaggingRegressor
from xgboost import XGBRegressor
from sklearn.linear_model import LinearRegression
#from sklearn.linear_model import SGDRegressor
#from sklearn.linear_model import HuberRegressor
#from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
#from lightgbm import LGBMRegressor
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt

# file
DIR = '../Logsn/ind_and_selBcol/v140/'
BASEFILE = 'HPmth023.csv'
FILE = DIR + BASEFILE

# load the dataset
def load_dataset(full_path):
	# Replace existing sting column labels with numbers as otherwise stings are passed to models
	dataframe = read_csv(full_path, header=0, names=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14])	
	# split into inputs and outputs
	last_ix = len(dataframe.columns) - 1
	# drop serial number and timedatet and constant dsoc from the inputs
	sn = 0
	date = 1
	dsoc = 5 # constant delta (5%)
	X, y = dataframe.drop([sn, date, dsoc, last_ix], axis='columns'), dataframe[last_ix]
	
	# split-out to intended test and validation sets to inihibt data leak at this stage
	test_size = 0.4
	train_size = None

	# IMPORTANT: keep time series order by shuffle=False
	X_train, X_test, y_train, y_test = train_test_split(X.values, y.values, test_size=test_size, train_size=train_size, shuffle=False)

	return X_train, y_train
 
# evaluate a model
def evaluate_model(X, y, model):
	# define evaluation procedure
	tscv = TimeSeriesSplit(n_splits=5)
	scoring = ('explained_variance')
	# evaluate model
	scores = cross_val_score(model, X, y, scoring=scoring, cv=tscv, n_jobs=-1)
	return scores
 
# define models to test
def get_models():
	models, names = list(), list()
	# CART -> away; compared in paper I
	models.append(DecisionTreeRegressor())
	names.append('CART')
	# AdaBoost
	models.append(AdaBoostRegressor(n_estimators=100))
	names.append('ADA')
	# Bagging
	#models.append(BaggingRegressor(n_estimators=100))
	#names.append('BAG')
	# RF -> away?; compared in paper I; can I ensure timeseries in this comparion?
	#models.append(RandomForestRegressor(n_estimators=100))
	#names.append('RF')
	# GBM -> away; looks like XGBM
	#models.append(GradientBoostingRegressor(n_estimators=100))
	#names.append('GBM')
	# XGB
	models.append(XGBRegressor(n_estimators=100))
	names.append('XGB')
	# LGBM (light gradinet boosting)  -> away; scoring values really off
	#models.append(LGBMRegressor(n_estimators=100))
	#names.append('LGBM')
	# LinR
	models.append(LinearRegression())
	names.append('LinR')
	# SGD -> away; scoring values by far off compared to others 
	#models.append(SGDRegressor())
	#names.append('SGD')
	# Huber -> away, but looks like LinR
	#models.append(HuberRegressor())
	#names.append('Huber')
	# KNN (Nearest neighbors)
	#models.append(KNeighborsRegressor())
	#names.append('KNN')
	# MLP (Perceptron) -> way off wiht this numbe of samples
	#models.append(MLPRegressor())
	#names.append('MLP')
	return models, names
 
# define the location of the dataset
full_path = FILE
# load the dataset
X, y = load_dataset(full_path)
# define models
models, names = get_models()
results = list()

# evaluate each model
for i in range(len(models)):
	# wrap the model i a pipeline
	pipeline = Pipeline(steps=[('m',models[i])])
	# evaluate the model and store results
	scores = evaluate_model(X, y, pipeline)
	results.append(scores)
	# summarize performance
	print('>%s %.3f (%.3f)' % (names[i], mean(scores), std(scores)))

# plot the results
pyplot.boxplot(results, labels=names, showmeans=True)
plt.savefig('Fig_algo_comp.pdf')
pyplot.show()

