# -*- coding: utf-8 -*-
"""
Created on Sun Jan  2 18:43:36 2022

@author: turbo
"""
location="/Users/turbo/Documents/GitHub/Text_Analysis/Text_Analysis"
import os
import re
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from collections import Counter

import gensim

#nltk.download('wordnet')

stop_words = set(stopwords.words('english'))

def get_part_of_speech(word):
  probable_part_of_speech = wordnet.synsets(word)
  
  pos_counts = Counter()

  pos_counts["n"] = len(  [ item for item in probable_part_of_speech if item.pos()=="n"]  )
  pos_counts["v"] = len(  [ item for item in probable_part_of_speech if item.pos()=="v"]  )
  pos_counts["a"] = len(  [ item for item in probable_part_of_speech if item.pos()=="a"]  )
  pos_counts["r"] = len(  [ item for item in probable_part_of_speech if item.pos()=="r"]  )
  
  most_likely_part_of_speech = pos_counts.most_common(1)[0][0]
  return most_likely_part_of_speech

def read_file(file_name):
  with open(file_name, 'r') as file:
    file_text = file.read()
  return file_text

def get_sentences(document,name):
    name_sent=[]
    for line in document:
        if line.startswith(name.lower()) or name == "Any":
            test=word_tokenize(line)
            name_sent.append([word for word in test if word not in stop_words])
    return name_sent


def init_program():
    lemmatizer = WordNetLemmatizer()
    
    os.chdir(location)
    files = sorted([file for file in os.listdir(location) if file [-4:] == '.txt'])
    
    """ Text Preprocessing """
    
    texts = [read_file(file) for file in files]
    for i in range(len(texts)):
        texts[i] = texts[i].lower()
        texts[i] = re.sub("\!*\?*\.*\,*\:*","",texts[i])
        texts[i] = re.sub("\n\n",".",texts[i])
        texts[i] = re.sub("\n","",texts[i])
        texts[i] = re.sub("sarah s","sarah ",texts[i])
    
    tokenized_words= [word_tokenize(texts[i]) for i in range(len(texts))]
    tokenized_sent = [texts[i].split(".") for i in range(len(texts))]
    
    lemmatized_words =[]
    
    for i in range(len(tokenized_words)):
        lemmatized_words.append([lemmatizer.lemmatize(token,get_part_of_speech(token))
                            for token in tokenized_words[i]])
    return lemmatized_words, tokenized_sent

def reformat_words():
    lemmatized_words, tokenized_sent = init_program()
    
    all_sent = []
    
    for sent_group in tokenized_sent:
        all_sent = all_sent + sent_group
    
    all_words = []
    for words in lemmatized_words:
        all_words = all_words + words
    
    all_words = [word for word in all_words if word not in stop_words]
    return all_words, all_sent
 
def bag_words(words,most_common):
    bag_of_words = Counter(all_words)
    most_common = Counter.most_common(bag_of_words,40)
    return most_common

def similar_words_to(words,speaker,word):
    analysis_sent = get_sentences(words,speaker)
    embed_sent = gensim.models.Word2Vec(analysis_sent)
    similar_words = embed_sent.wv.most_similar(word,topn=20)
    return similar_words

all_words, all_sent = reformat_words()
print(bag_words(all_words,20))
print(similar_words_to(all_sent,"Any","friend")) #use any to sort by all speakers
