# -*- coding: utf-8 -*-
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import re

def sentence_string (lists_sentences):
    sentences_as_strings = []
    for sentence in lists_sentences:
        sentences_as_strings.append(" ".join(sentence))
        
    return sentences_as_strings

def string_list(string_sentence):
    list_sentence = []
    list_sentence = re.split('\s+',str(string_sentence))
    
    return list_sentence

def Vectorize(sentences):
    sentences = sentence_string(sentences)
    vectorizer = CountVectorizer()
    vectorizer.fit(sentences)
    vector = vectorizer.transform(sentences)
    
    return vector

def Train_Test(file_name):
    df = pd.read_csv (file_name)
    df = df.drop(['Raw_Text'], axis=1)
    df['Processed_Text'] = df['Processed_Text'].apply(string_list)
    train=df.sample(frac=0.8,random_state=200) #random state is a seed value
    test=df.drop(train.index)
    
    return train, test

train, test = Train_Test('Training_Set.csv')

#(Vectorize(df["Processed_Text"].tolist()))


print(test)


"""
df = pd.DataFrame(sentence_string(comments),columns=["Comment"])
print(df)
df.to_csv('Training_Data.csv')

df = pd.DataFrame(sentence_string(comments_unlemmatized),columns=["Comment"])
print(df)
df.to_csv('Training_Data_2.csv')
"""
