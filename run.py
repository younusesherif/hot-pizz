import io
import random
import string # to process standard python strings
import warnings
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')
from pymongo import MongoClient
import json


client = MongoClient("mongodb+srv://younuse:sherif@cluster0-umi9i.mongodb.net/test?retryWrites=true&w=majority")


db = client.get_database('new')

records = db.orders

import nltk
from nltk.stem import WordNetLemmatizer
nltk.download('popular', quiet=True) # for downloading packages
#nltk.download('punkt') # first-time use only
#nltk.download('wordnet') # first-time use only

f=open('chatbot.txt','r',errors = 'ignore')
raw=f.read()
raw = raw.lower()# converts to lowercase


sent_tokens = nltk.sent_tokenize(raw)# converts to list of sentences 
word_tokens = nltk.word_tokenize(raw)# converts to list of words

lemmer = nltk.stem.WordNetLemmatizer()
#WordNet is a semantically-oriented dictionary of English included in NLTK.
def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]
remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)

def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))

GREETING_INPUTS = ("hello", "hi","hai","greetings", "sup","how are you","what's up","hey",)
GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]
def greeting(sentence):
 
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)


def responsing(user_response):
    robo_response=''
    sent_tokens.append(user_response)
    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)
    idx=vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]
    if(req_tfidf==0):
        robo_response=robo_response+"I am sorry! I don't understand you"
        return robo_response
    else:
        robo_response = robo_response+sent_tokens[idx]
        return robo_response


from flask import Flask, render_template, request   

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/order',methods=['get'])
def orderplaced():
  collection=request.args.get('msg')
  py_obj = json.loads(collection)
  records.insert_one(py_obj)
  response="ROBO: your order has been placed please check with orderID for status of order"
  return response
@app.route('/get', methods = ['get'])
def signup():
    words=[]
    user_response = request.args.get('msg')
    words=user_response.split()
    user_response=user_response.lower()
    if(user_response!='bye'):
      if(user_response=='thanks' or user_response=='thank you' ):
        response="ROBO: You are welcome.."
      else:
        if(greeting(user_response)!=None):
          response="ROBO: "+greeting(user_response)
        else:
          for x in records.find({},{"_id":0,"orderid": 1 }):
            x=dict(x)
            p=(x.get('orderid'))
            if p in words:
              print("your order has been placed")
              print(p)
              mydoc = records.find({"orderid":p})
              for x in mydoc:
                print(x)
                response="ROBO: you ordered "+str(x["count"])+" "+x["size"]+" "+x["type"]+" pizza we are reaching you at "+x["address"]
            else:
              response=("ROBO: "+responsing(user_response))
              sent_tokens.remove(user_response)
    
    else:
      response=("ROBO: Bye! take care..")
    
    
    return response

if __name__ == "__main__":
    app.run()