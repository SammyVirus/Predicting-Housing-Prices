import quandl
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import style
import numpy as np
from statistics import mean
from sklearn import svm, preprocessing
from sklearn.model_selection import train_test_split
style.use('fivethirtyeight')

api_key = open('quandlapikey.txt', 'r').readline().rstrip('\n')

def create_labels(cur_hpi, fut_hpi):
    if fut_hpi > cur_hpi:
        return 1
    else:
        return 0

def moving_average(values):
    return mean(values)

housing_data = pd.read_pickle('Data/HPI.pickle')
housing_data =  housing_data.pct_change()

housing_data.replace([np.inf, -np.inf], np.nan, inplace=True)
housing_data.dropna(inplace=True)

housing_data['US_HPI_future'] = housing_data['USA'].shift(-1)
housing_data.dropna(inplace=True)

housing_data['label'] = list(map(create_labels, housing_data['USA'], housing_data['US_HPI_future']))
#print(housing_data.head())

x = np.array(housing_data.drop(['label', 'US_HPI_future'], 1))
x = preprocessing.scale(x)

y = np.array(housing_data['label'])

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3)
clf = svm.SVC(kernel='linear')
clf.fit(x_train, y_train)

print(clf.score(x_test, y_test))
