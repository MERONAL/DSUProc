from pandas import read_csv
from pandas import DataFrame
from pandas import concat
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
import pickle
from numpy import concatenate
import numpy as np
from math import sqrt
import matplotlib.pyplot as plt


# load dataset
dataset = read_csv('C:/Users/a8047/Desktop/lstm_dynamic/tailored.csv', header=0, index_col=0)
values = dataset.values
# specify columns to plot
groups = [0, 1, 2, 3]
i = 1
# plot each column
# pyplot.figure()
# for group in groups:
#     pyplot.subplot(len(groups), 1, i)
#     pyplot.plot(values[:, group])
#     pyplot.title(dataset.columns[group], y=0.5, loc='right')
#     i += 1
# pyplot.show()


# In[5]:


# convert series to supervised learning
def series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
    n_vars = 1 if type(data) is list else data.shape[1]
    df = DataFrame(data)
    cols, names = list(), list()
    # input sequence (t-n, ... t-1)
    for i in range(n_in, 0, -1):
        cols.append(df.shift(i))
        names += [('var%d(t-%d)' % (j + 1, i)) for j in range(n_vars)]
    # forecast sequence (t, t+1, ... t+n)
    for i in range(0, n_out):
        cols.append(df.shift(-i))
        if i == 0:
            names += [('var%d(t)' % (j + 1)) for j in range(n_vars)]
        else:
            names += [('var%d(t+%d)' % (j + 1, i)) for j in range(n_vars)]
    # put it all together
    agg = concat(cols, axis=1)
    agg.columns = names
    # drop rows with NaN values
    if dropnan:
        agg.dropna(inplace=True)
    return agg


# load dataset
dataset = read_csv('C:/Users/a8047/Desktop/lstm_dynamic/tailored.csv', header=0, index_col=0)
values = dataset.values
# integer encode direction
# encoder = preprocessing.LabelEncoder()
# values[:,4] = encoder.fit_transform(values[:,4])
# ensure all data is float
values = values.astype('float32')
# normalize features
scaler = MinMaxScaler(feature_range=(0, 1))
scaled = scaler.fit_transform(values)
# specify the number of lag hours
# n_hours = 3
# n_features = 8
# frame as supervised learning
# reframed = series_to_supervised(scaled, n_hours, 1)
reframed = series_to_supervised(scaled, 1, 1)
# drop columns we don't want to predict
reframed.drop(reframed.columns[[4, 5, 6]], axis=1, inplace=True)
print(reframed.head())

# In[7]:


# split into train and test sets
values = reframed.values

# split into train and test sets
train_size = int(len(values) * 0.67)
test_size = len(values) - train_size
train, test = values[:train_size, :], values[train_size:, :]

# split into input and outputs
train_X, train_y = train[:, :-1], train[:, -1]
test_X, test_y = test[:, :-1], test[:, -1]
# reshape input to be 3D [samples, timesteps, features]
train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))
print(train_X.shape, train_y.shape, test_X.shape, test_y.shape)

f = open('model1.pkl', 'rb')
lstm_from_pickle = pickle.load(f)
f.close()


# make a prediction
my_test = np.array([25, -22, 2, 1222],dtype=float)
my_test[0] = (my_test[0] - 25) / 149
my_test[1] = (my_test[1] + 37) / 72
my_test[2] = my_test[2] / 3
my_test[3] = my_test[3] / 2230
my_test = my_test.reshape(1,1,4)
yhat_test = lstm_from_pickle.predict(my_test)


yhat = lstm_from_pickle.predict(test_X)
test_X = test_X.reshape((test_X.shape[0], test_X.shape[2]))
# invert scaling for forecast
inv_yhat = concatenate((yhat, test_X[:, 1:]), axis=1)
inv_yhat = scaler.inverse_transform(inv_yhat)
inv_yhat = inv_yhat[:, 0]
# invert scaling for actual
test_y = test_y.reshape((len(test_y), 1))
inv_y = concatenate((test_y, test_X[:, 1:]), axis=1)
inv_y = scaler.inverse_transform(inv_y)
inv_y = inv_y[:, 0]
# calculate RMSE
rmse = sqrt(mean_squared_error(inv_y, inv_yhat))
print('Test RMSE: %.3f' % rmse)

# plot history
plt.plot(inv_y)
plt.plot(inv_yhat)
plt.show()