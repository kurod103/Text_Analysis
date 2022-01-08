# -*- coding: utf-8 -*-
"""
Created on Thu Jan  6 18:02:28 2022

@author: turbo
"""

from bs4 import BeautifulSoup
import requests
import re

import yfinance as yf
#import pandas as pd
import Text_Processing
import Convert_Estimation
import statistics

#import SpaCy

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

def generate_prices(ticker): #create a vector of prices in times
    prices = yf.download(tickers=ticker, period="1d", interval="1m")
    minute_prices = [round(prices.get("Close")[i],2) for i in range(len(prices))]
    
    prices = yf.download(tickers=ticker, period="5d", interval="1h")
    hour_prices = [round(prices.get("Close")[i],2) for i in range(len(prices))]
    return [hour_prices,minute_prices,statistics.stdev(minute_prices)]

Price_Vector = generate_prices("NG=F")

def word_cloud(sentences):
    
    return word_cloud

"""Convert comment price targets into relative numbers"""
        
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
        self.comment_lemmatized = Text_Processing.lemmatize_vector(self.comment)
        
    def chunked_comments(self,chunk):
        self.comment_chunked = Text_Processing.chunk_vector(self.comment,chunk)
        
    def fix_estimations(self):
        comments=[]
        for i in range(len(self.comment_lemmatized)):
            relative_estimate = Convert_Estimation.find_estimations(self.comment_lemmatized[i],self.times[i],Price_Vector)
            comments.append(relative_estimate)
        self.comment_lemmatized = comments
html = "https://www.investing.com/commodities/natural-gas-commentary"

Pages = Investing_Page()
for page in range(1,10):
    page_html = html + "/" + str(page)
    Pages.add_page(page_html)
Pages.lemmatize_comments()
Pages.fix_estimations()

chunk= "NP: {<DT>?<JJ>*<NN>}"
print_comments = False
Pages.chunked_comments(chunk)

comments = return_comment_vector(Pages.times,Pages.vote, Pages.comment_lemmatized)

if print_comments:
    for comment in comments:
        print(comment)
        print()

bag_of_words = Text_Processing.bag_words(Pages.comment_lemmatized,40)

#Checking the difference in word choice between Longs and Shorts in Natural Gas
print("short")
print(Text_Processing.similar_words_to(Pages.comment_lemmatized,"short",40))
print("long")
print(Text_Processing.similar_words_to(Pages.comment_lemmatized,"long",40))
