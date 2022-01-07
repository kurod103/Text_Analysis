# -*- coding: utf-8 -*-
"""
Created on Thu Jan  6 18:02:28 2022

@author: turbo
"""

from bs4 import BeautifulSoup
import requests
import re
from nltk import word_tokenize
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
from collections import Counter
import investpy

def get_site(html): # Return a soup of the website requested
    html_get = requests.get(html)
    html_doc = html_get.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    return soup

def return_features_investing(site): #Returns the comment section in 3 lists
    text = site.get_text()
    
    #Get time of post
    text_times = re.findall("(\d*)( minutes?| hours?|\ days?)( ago)", text)
    
    #Get upvotes, downvotes
    text_values = re.findall("Reply\d*Report",text)
    text_values = [text_values[i].strip("Reply").strip("Report") for i in range(len(text_values))]
    text_values = [[text_values[i][0],text_values[i][1]] for i in range(len(text_values))]
    
    #Get comment
    text = re.split("\d* minutes? ago|\d* hours? ago|\d* days? ago",text) #get comments
    text = [text[i].strip() for i in range(1,len(text)-1)] #ignore header, footer, spaces
    text_words = [re.split(r'Reply\d*Report',text[i])[0] for i in range(len(text))] #remove reply, etc
    
    #text_words = [word_tokenize(text_words[i]) for i in range(len(text_words))]
    
    return text_times, text_values, text_words

def return_comment_vector(times,vote,comment): #returns a vector of comments, given 3 lists
    comment_vector = []
    for i in range(len(comment)):
        comment_vector.append([times[i],vote[i],comment[i]])
    return comment_vector

def get_part_of_speech(word): #for lemmatization
  probable_part_of_speech = wordnet.synsets(word)
  
  pos_counts = Counter()

  pos_counts["n"] = len(  [ item for item in probable_part_of_speech if item.pos()=="n"]  )
  pos_counts["v"] = len(  [ item for item in probable_part_of_speech if item.pos()=="v"]  )
  pos_counts["a"] = len(  [ item for item in probable_part_of_speech if item.pos()=="a"]  )
  pos_counts["r"] = len(  [ item for item in probable_part_of_speech if item.pos()=="r"]  )
  
  most_likely_part_of_speech = pos_counts.most_common(1)[0][0]
  return most_likely_part_of_speech

def lemmatize_vector(comments): #lemmatize a list of comments
    comments_token = [word_tokenize(comments[i]) for i in range(len(comments))]
    lemmatized_comments = []
    for i in range(len(comments)):
        lemmatized_comments.append([lemmatizer.lemmatize(token, get_part_of_speech(token)).lower()
                                    for token in comments_token[i]])
    return lemmatized_comments

def get_price_at_time(time,ticker): #returns the investing.com price at X hours/minutes ago
    price = 0
    return price

def convert_estimation(price_at_time, estimation):
    difference = estimation-price_at_time
    return difference

class Investing_Page():
    def __init__(self):
        self.times = []
        self.vote = []
        self.comment = []  

    def add_page(self, link):
        times,vote,comment = return_features_investing(get_site(link))
        self.times = self.times + times
        self.vote = self.vote + vote
        self.comment = self.comment + comment

    def lemmatize_comments(self):
        self.comment_lemmatized = lemmatize_vector(self.comment)


html = "https://www.investing.com/commodities/natural-gas-commentary"

Pages = Investing_Page()
for page in range(1,2):
    page_html = html + "/" + str(page)
    Pages.add_page(page_html)
Pages.lemmatize_comments()

comments = return_comment_vector(Pages.times,Pages.vote, Pages.comment_lemmatized)
for comment in comments:
    print(comment)
    print()