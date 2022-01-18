# -*- coding: utf-8 -*-
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import re

def sentence_string (lists_sentences): #Return a list of lists as list of strings
    sentences_as_strings = []
    for sentence in lists_sentences:
        sentences_as_strings.append(" ".join(sentence))
        
    return sentences_as_strings

def string_list(string_sentence): #Return a string as a list
    list_sentence = []
    list_sentence = re.split('\s+',str(string_sentence))
    
    return list_sentence

def Vectorize(sentences, comments = []): #Vectorize from both the training data, and input comments
    sentences = sentence_string(sentences)
    comments = sentence_string(comments)
    
    sentences = sentences + comments
    
    vectorizer = CountVectorizer()
    vectorizer.fit(sentences)
    vector = vectorizer.transform(sentences)
    
    return vector

def Train_Test(file_name, bullish, comments =[]):
    df = pd.read_csv (file_name)
    df = df.drop(['Raw_Text'], axis=1)
    if bullish == "Bearish": df["Label"]= 1-df["Label"] #Only tags bearish comments
    
    df["Label"] = df["Label"].astype(int) #Fixes format for machine learning
    
    df['Processed_Text'] = df['Processed_Text'].apply(string_list)
    
    #word_vector = Vectorize(df['Processed_Text'], comments)
    
    train=df.sample(frac=0.8,random_state=200) #random state is a seed value
    test=df.drop(train.index)
    
    return train, test, df

train, test, data = Train_Test('Training_Set.csv', "Bullish")

X_train = Vectorize(data["Processed_Text"]).toarray()

from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from scipy.sparse import csr_matrix
import numpy as np

def train_and_show_scores(X: csr_matrix, y: np.array, title: str) -> None:
    X_train, X_valid, y_train, y_valid = train_test_split(
        X, y, train_size=0.75, stratify=y
    )
    
    clf = SGDClassifier()
    clf.fit(X_train, y_train)
    train_score = clf.score(X_train, y_train)
    valid_score = clf.score(X_valid, y_valid)
    print(f'{title}\nTrain score: {round(train_score, 2)} ; Validation score: {round(valid_score, 2)}\n')

y_train = data['Label'].values

train_and_show_scores(X_train, y_train, 'Unigram Counts')

#PRINT OUT RESULTS OF MODEL
#RUN MODEL ON NEW COMMENTS

#FIND WORD CLOUDS OF COMMENTS TAGGED AS BULLISH, VS BEARISH
#RUN A MOVING AVERAGE OF BULLISH vs BEARISH COMMENTS