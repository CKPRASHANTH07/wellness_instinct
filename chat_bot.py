import random
import json
import pickle
import numpy as np
import nltk
import re
from nltk.stem.porter import PorterStemmer
import tensorflow as tf



ps=PorterStemmer()
intents = json.loads(open('intentsss.json').read())
words=pickle.load(open('words.pkl','rb'))
classes=pickle.load(open('classes.pkl','rb'))
model_path='chabot_m.model'
model = tf.keras.models.load_model(model_path)
def clean_sentence(sentences):
    sentence=re.findall(r'\w+', sentences)
    sentence=[ps.stem(hell) for hell in sentence]
    return sentence
def bagofwords(sentences):
    sentence=clean_sentence(sentences)
    bag=[0]*len(words)
    for i in sentence:
        for j,word in enumerate(words):
            if word==i:
                bag[j]=1
    return np.array(bag)
def predict(sentences):
    bow=bagofwords(sentences)
    res=model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD=0.25
    results=[[i,r] for i,r in enumerate(res)if r>ERROR_THRESHOLD]
    results.sort(key=lambda x:x[1],reverse=True)
    return_list=[]
    for r in results:
        return_list.append({'intent':classes[r[0]],'probability': str(r[1])})
    return return_list

def respone(intents_list,intents_json):
    result="hi"

    tag=intents_list[0]['intent']
    list_of_intents=intents_json['intents']
    for i in list_of_intents:
        if i['tag']==tag:
            result=random.choice(i['responses'])
            break
    # except:
    #     result="I cannot understand this statement. Perhaps rephrase it or type it differently?"
    return result

print("Bot is running")
while True:
    try:
        message=input("")
        ints=predict(message)
        res=respone(ints,intents)
        print(res)
    except:
        print( "I cannot understand this statement. Perhaps rephrase it or type it differently?")


