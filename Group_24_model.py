from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.layers import Embedding
from keras.layers import LSTM
import pandas as pd

training_source = pd.read_csv("final_training_source_events.csv")
test_source = pd.read_csv("final_test_source_events.csv")
training_target = pd.read_csv("timeslot.csv")
col = pd.read_csv("col_name.csv")
training_source.drop(columns=['Unnamed: 0'])

#print(training_source)
#input()

# LSTM for international airline passengers problem with regression framing
import numpy as np
import matplotlib.pyplot as plt
import math
import random
from keras.models import Sequential,Model
from keras.layers import Dense, Input
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import Embedding,Flatten
from keras import backend as K
import statistics

col = list(col['0'])


training_source = training_source.values.tolist()
X = []
for i in training_source:
    X.append(i[4:])
X = pd.DataFrame(X)

test_source = test_source.values.tolist()
test = []
for i in test_source:
    test.append(i[3:])
test = pd.DataFrame(test)


#print(X)
#input()
#X = np.asarray(X).astype(np.float32).reshape((-1,1))
#X = X.astype('float32')
#scaler = MinMaxScaler(feature_range=(0, 1))
#X = scaler.fit_transform(X)
#print(X)
#input()
training_target = training_target.values
#y = np.asarray(training_target).astype(np.float32).reshape((-1,1))

#training_target = training_target.astype('float32')
#scaler = MinMaxScaler(feature_range=(0, 1))
#training_target = scaler.fit_transform(training_target)
y = training_target
#print(y)
#input()
test_size = 0.2
#X = X.reshape((X.shape[0], 1, X.shape[1]))
#print(X)
#input()
#y = y.reshape((y.shape[0], 1, y.shape[1]))

X_train,X_test = train_test_split(X,test_size = test_size,random_state=5)
y_train,y_test = train_test_split(y,test_size = test_size,random_state=5)

X_train = np.asarray(X_train).astype(np.float32)
y_train = np.asarray(y_train).astype(np.float32)
X_test = np.asarray(X_test).astype(np.float32)
test = np.asarray(test).astype(np.float32)

#print(X_train)
#print(y_train)
#input()
#y_train = np.asarray(training_target).astype(np.float32).reshape((-1,1))
#y_test= np.asarray(training_target).astype(np.float32).reshape((-1,1))
#print(X_train.shape)
#print(y_train.shape)
#input()

model = Sequential()
#model.add(LSTM(48,return_sequences=True,input_shape=(X_train.shape[1],1)))
model.add(Flatten())
#model.add(Embedding(1000,32,input_length=100))
#model.add(LSTM(48))
#model.add(Dropout(0.375))

model.add(Dense(38, input_shape=(X_train.shape[1],),activation='relu'))
#model.add(Dense(38, activation='softmax'))
model.add(Dense(38,activation='relu'))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

#X_train1 = K.cast_to_floatx(X_train)
#y_train1 = K.cast_to_floatx(y_train)

model.fit(X_train, y_train, batch_size=8, epochs=3, validation_split=0.2)

#print(y_test)
### = model.evaluate(X_test, y_test, batch_size=16)
#model.summary()
Pred = model.predict(test)
Pred = pd.DataFrame(Pred)
Pred = list(Pred.iloc[:,0])

#plot
import seaborn as sns
sns.distplot(Pred)
plt.show()


pd.DataFrame(Pred).describe()
user_len = int(len(Pred)/28)
Pred_trans = Pred
for i in range(len(Pred_trans)):
    if Pred_trans[i] >= 0.04:
        Pred_trans[i] = 1
    else:
        Pred_trans[i] = 0
    
df_Prediction = []
for i in range(0,len(Pred_trans),28):
    df_Prediction.append(Pred_trans[i:i+28])
df_Prediction = pd.DataFrame(df_Prediction)
df_Prediction.columns = col
row = list(range(32000,32000 + user_len))
df_Prediction['user_id'] = row
df_Prediction = df_Prediction.set_index('user_id')
df_Prediction.to_csv("Prediction.csv")

#predictions = model.predict(samples_to_predict)
#print(predictions)