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
import yfinance as yf
#import pandas as pd

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
        #lemmatized_comments[i] = re.sub("\!*\?*\.*\,*\:*","",lemmatized_comments[i])
    return lemmatized_comments
        
def return_comment_vector(times,vote,comment): #returns a vector of comments, given 3 lists
    comment_vector = []
    for i in range(len(comment)):
        comment_vector.append([times[i],vote[i],comment[i]])
    return comment_vector

def generate_prices(): #create a vector of prices in times
    prices = yf.download(tickers="NG=F", period="1d", interval="1m")
    minute_prices = [round(prices.get("Close")[i],2) for i in range(len(prices))]
    
    prices = yf.download(tickers="NG=F", period="1d", interval="1h")
    hour_prices = [round(prices.get("Close")[i],2) for i in range(len(prices))]
    return minute_prices, hour_prices

Minute_Prices, Hour_Prices = generate_prices()

"""Convert comment price targets into relative numbers"""

def get_price_at_time(time): #returns the investing.com price at X hours/minutes ago
    number = int(time[0])
    if time[1] == "hour" or time[1]=="hours":
        return Hour_Prices[-number]
    return Minute_Prices[-number]

def convert_estimation(time, estimation,conv_type): #find difference between est and real price at posting time
    current_price = get_price_at_time(time)
    
    if conv_type == "full":
        difference = estimation-current_price
    elif conv_type == "dec":
        difference1 = estimation-current_price%1
        difference2 = estimation - current_price%1 + 1
        if abs(difference1) > abs(difference2): 
            difference = difference2
        else:
            difference = difference1
    return round(difference,4)

def find_estimations(comment,time): #find estimation in a comment line
    for word in range(len(comment)):
        try:
            float(comment[word])
            if bool(re.search("\d\.\d*",comment[word])):
                comment[word]= convert_estimation(time, float(comment[word]),"full")
            elif bool(re.search("\.\d*",comment[word])) and float(comment[word])<1:
                comment[word]= convert_estimation(time,float(comment[word]),"dec")
            elif float(comment[word])>=1 and float(comment[word])<10:
                comment[word]=convert_estimation(time,float(comment[word]),"full")
        except ValueError:
            pass
    return comment
        
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
        
    def fix_estimations(self):
        comments=[]
        for i in range(len(self.comment_lemmatized)):
            comments.append(find_estimations(self.comment_lemmatized[i],self.times[i]))
        self.comment_lemmatized = comments

html = "https://www.investing.com/commodities/natural-gas-commentary"

Pages = Investing_Page()
for page in range(1,2):
    page_html = html + "/" + str(page)
    Pages.add_page(page_html)
Pages.lemmatize_comments()
Pages.fix_estimations()

comments = return_comment_vector(Pages.times,Pages.vote, Pages.comment_lemmatized)


for comment in comments:
    print(comment)
    print()
