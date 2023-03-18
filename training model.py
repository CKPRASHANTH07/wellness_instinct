import random
import json
import pickle


import numpy as np
import numpy as pd
import nltk
import re

from nltk.stem.porter import PorterStemmer

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense,Activation,Dropout
from tensorflow.keras.optimizers import SGD
intents = json.loads(open('intentsss.json').read())
ps=PorterStemmer()

words = []
classes = []
documents = []
ignore=['.' , ',','/' ,'!','@','#','?']

for i in intents['intents']:
    for jerry in i['patterns']:
        # word = nltk.word_tokenize(jerry)
        word=re.findall(r'\w+', jerry)
        words.extend(word)
        documents.append((word,i['tag']))
        if i['tag'] not in classes:
            classes.append(i['tag'])
print(documents)
words=[ps.stem(word) for word in words if word not in ignore]
words=sorted(set(words))
classes=sorted(set(classes))
print(words)
with open('words.pkl', 'wb') as f:
    pickle.dump(words, f)
with open('classes.pkl', 'wb') as f:
    pickle.dump(classes, f)

training=[]
output_empty=[0]*len(classes)
for document in documents:
    bag=[]
    words_patterns=document[0]
    words_patterns = [ps.stem(word.lower()) for word in words_patterns]

    for word in words:
        bag.append(1) if word in words_patterns else bag.append(0)


    output_row=list(output_empty)
    output_row[classes.index(document[1])]=1
    training.append([bag , output_row])


random.shuffle(training)
training=np.array(training,dtype=object)

train_x=list(training[:,0])
train_y=list(training[:,1])

model=Sequential()
model.add(Dense(128,input_shape=(len(train_x[0]),),activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64,activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]),activation='softmax'))
sgd=SGD(lr=0.01,momentum=0.9,nesterov=True)
model.compile(loss='categorical_crossentropy',optimizer=sgd,metrics=['accuracy'])
model.fit(np.array(train_x),np.array(train_y),epochs=200,batch_size=5,verbose=1)
model.save('chabot_m.model')
print("done")


