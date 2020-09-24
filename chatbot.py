
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

GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up","hey",)
GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]
def greeting(sentence):
 
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)


def response(user_response):
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

flag=True
order=[]
collection={}
words=[]
print("ROBO: My name is Robo. I will answer your queries about Chatbots. If you want to exit, type Bye!")
while(flag==True):
    user_response = input()
    user_response=user_response.lower()
    words=user_response.split()

    if(user_response!='bye'):
        if(user_response=='thanks' or user_response=='thank you' ):
            flag=False
            print("ROBO: You are welcome..")
        else:
            if(greeting(user_response)!=None):
                print("ROBO: "+greeting(user_response))
            else:
                print("ROBO: ",end="")
                if(user_response == 'order init'):
                  pizza=False
                  contact=False
                  flag1=True
                  types=False
                  size=False
                  count=False
                  name=False
                  number=False
                  location=False
                  while(flag1==True):
                    if(pizza==False):
                      if(types==False):
                        print("Please enter A or B for type of pizza is Veg or NonVeg")
                        user_response = input()
                        user_response=user_response.upper()
                        if(user_response=='A'):
                          collection["types"]="veg pizza"
                          types=True
                        elif(user_response=='B'):
                          collection["types"]="Non veg pizza"
                          types=True
                        else:
                          print("please enter corrrect option")
                          

                      elif(size==False):
                        print("Please enter A or B or C for size Eg:regular,medium,large")
                        user_response = input()
                        user_response=user_response.upper()
                        if(user_response=='A'):
                          collection["size"]="regular"
                          size=True
                        elif(user_response =='B'):
                          collection["size"]="medium"
                          size=True
                        elif(user_response == 'C'):
                          collection["size"]="large"
                          size=True
                        else:
                          print("Please enter correct option")

                      elif(count==False):
                        print("Please enter number of Pizza")
                        user_response = input()
                        user_response=user_response.lower()
                        if(int(user_response)):
                          collection["count"]=int(user_response)
                          count=True
                        else:
                          print("Please enter number only for count of a pizza")
                    
                    if(types==True and size==True and count==True):
                      pizza=True
                    else:
                      pizza=False
                    
                    if(pizza==True and contact==False):
                      if(name==False):
                        print("Please enter your name")
                        user_response = input()
                        collection["name"]=user_response
                        name=True
                       
                      elif(number==False):
                        print("please enter you mobile number")
                        user_response=input()
                        if(user_response.isdigit() and len(user_response)==10):
                          collection["number"]=user_response
                          number=True
                        else:
                          print("Please enter valid mobile number your number is less than or greater than 10 d")
                        
                      elif(location==False):
                        print("please enter you location NOTE:your entered can't be validated")
                        user_response=input()
                        collection["location"]=user_response
                        location=True

                    if(name==True and number==True and location==True ):
                      contact=True

                    if(pizza==True and contact==True):
                      flag1=False

                  collection["orderid"]=''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(5))
                  print(collection)
                  order.append(collection)
                  print(order)
                  records.insert_one(collection)
                  print("Order Placed")

                else:
                  for x in records.find({},{"_id":0,"id": 1 }):
                    dict1=x
                    p=dict1["id"]
                    if p in words:
                      print("your order has been placed")
                      mydoc = records.find({"id":p})
                      for x in mydoc:
                        print(x)

                  print(response(user_response))
                  sent_tokens.remove(user_response)
    else:
        flag=False
        print("ROBO: Bye! take care..")