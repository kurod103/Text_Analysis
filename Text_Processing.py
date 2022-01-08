# -*- coding: utf-8 -*-
"""
Created on Fri Jan  7 09:05:18 2022

@author: turbo
"""
import nltk

#Preprocessing Assets
from collections import Counter
import re
from nltk import word_tokenize
from nltk import RegexpParser
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
from nltk.corpus import stopwords

#Get similar words
import gensim

#WordCloud Assets
import matplotlib.pyplot as plt
from wordcloud import WordCloud

#nltk.download('RegexParser')



stop_words = set(stopwords.words('english'))

def get_part_of_speech(word): #for lemmatization
  probable_part_of_speech = wordnet.synsets(word)
  
  pos_counts = Counter()

  pos_counts["n"] = len(  [ item for item in probable_part_of_speech if item.pos()=="n"]  )
  pos_counts["v"] = len(  [ item for item in probable_part_of_speech if item.pos()=="v"]  )
  pos_counts["a"] = len(  [ item for item in probable_part_of_speech if item.pos()=="a"]  )
  pos_counts["r"] = len(  [ item for item in probable_part_of_speech if item.pos()=="r"]  )
  
  most_likely_part_of_speech = pos_counts.most_common(1)[0][0]
  return most_likely_part_of_speech

def tokenize_vector(comments):
    return [word_tokenize(comments[i]) for i in range(len(comments))]

def lemmatize_vector(comments): #lemmatize a list of comments
    comments = [re.sub("\!*\?*\.*\,*\:*","",comments[i]) for i in range(len(comments))]
    comments_token = tokenize_vector(comments)
    lemmatized_comments = []
    for i in range(len(comments)):
        
        lemmatized_comment = [lemmatizer.lemmatize(token, get_part_of_speech(token)).lower()
                                    for token in comments_token[i]]
        lemmatized_comment = [word for word in lemmatized_comment if word not in stop_words] 
          
        lemmatized_comments.append(lemmatized_comment)
        
    return lemmatized_comments

def chunk_vector(comments,grammar): #lemmatize a list of comments
    tokenize_vector(comments)
    comments_token = tokenize_vector(comments)
    chunked_comments = []
    
    chunk_parser = RegexpParser(grammar)
    
    for i in range(len(comments)):
        lemmatized_sentence = []
        for word in comments_token[i]:
            part_of_speech= get_part_of_speech(word)
            lemmatized_word = lemmatizer.lemmatize(word,part_of_speech)
            lemmatized_sentence.append((lemmatized_word,part_of_speech))
        chunked_comments.append(chunk_parser.parse(lemmatized_sentence))
    return chunked_comments

def bag_words(sentences,num_most_common):
    sentences_aggregate =[]
    for sentence in sentences:
        sentences_aggregate = sentences_aggregate + sentence
    bag_of_words = Counter(sentences_aggregate)
    most_common = Counter.most_common(bag_of_words,num_most_common)
    
    return most_common

def word_cloud(bag_of_words): #Doesn't function on Windows 10
    words = ""
    for item in bag_of_words:
        for count in range(item[1]):
            words = words + str(item[0])
    wordcloud = WordCloud(words, background_color ="black").generate(words)
    plt.figure(figsize = (8, 8), facecolor = None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad = 0)
 
    plt.show()


def similar_words_to(words,word, num_most_common):
    embed_sent = gensim.models.Word2Vec(words)
    similar_words = embed_sent.wv.most_similar(word,topn = num_most_common)
    return similar_words
