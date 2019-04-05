# coding: utf-8

# In[3]:


from pandas import read_csv
from datetime import datetime

# load data
dataset = read_csv('C:/Users/hp/Desktop/lstm_dynamic/ATO_CD3.csv', header=0, index_col=0, squeeze=True, error_bad_lines=False)
# manually specify column names
dataset.columns = ['analog_output', 'slope', 'traction_brake', 'speed']
dataset.index.name = 'seq_no'
# summarize first 5 rows
print(dataset.head(5))
# save to file
dataset.to_csv('C:/Users/hp/Desktop/lstm_dynamic/tailored.csv')

# In[4]:


from matplotlib import pyplot

# load dataset
dataset = read_csv('C:/Users/hp/Desktop/lstm_dynamic/tailored.csv', header=0, index_col=0)
values = dataset.values
# specify columns to plot
groups = [0, 1, 2, 3]
i = 1
# plot each column
pyplot.figure()
for group in groups:
    pyplot.subplot(len(groups), 1, i)
    pyplot.plot(values[:, group])
    pyplot.title(dataset.columns[group], y=0.5, loc='right')
    i += 1
pyplot.show()


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


# In[6]:


from pandas import DataFrame
from pandas import concat
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error

# load dataset
dataset = read_csv('C:/Users/hp/Desktop/lstm_dynamic/tailored.csv', header=0, index_col=0)
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

# In[8]:


from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM

# design network
model = Sequential()
model.add(LSTM(50, input_shape=(train_X.shape[1], train_X.shape[2])))
model.add(Dense(1))
model.compile(loss='mae', optimizer='adam')
# fit network
history = model.fit(train_X, train_y, epochs=50, batch_size=72, validation_data=(test_X, test_y), verbose=2,
                    shuffle=False)
# plot history
pyplot.plot(history.history['loss'], label='train')
pyplot.plot(history.history['val_loss'], label='test')
pyplot.legend()
pyplot.show()

# In[10]:


from numpy import concatenate
from math import sqrt

# make a prediction
yhat = model.predict(test_X)
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

# In[11]:


import matplotlib.pyplot as plt

plt.plot(inv_y)
plt.plot(inv_yhat)
plt.show()

# In[12]:


import pickle

# In[13]:


# Save the trained model as a pickle string.
saved_model = pickle.dumps(model)

# Load the pickled model
lstm_from_pickle = pickle.loads(saved_model)

# Use the loaded pickled model to make predictions 
lstm_from_pickle.predict(test_X) 

