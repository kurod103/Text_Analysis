# -*- coding: utf-8 -*-
"""
Takes in a comment, converts estimation from the comment into a relative number
"""
import re

def get_price_at_time(time, hour_prices, minute_prices): #returns the investing.com price at X hours/minutes ago
    number = int(time[0])
    if time[1] == "hour" or time[1]=="hours":
        return hour_prices[-number]
    return minute_prices[-number]

def convert_estimation(time, estimation,conv_type, price_vectors): #find difference between est and real price at posting time
    hour_prices = price_vectors[0]
    minute_prices = price_vectors[1]
    price_stdev = price_vectors[2]
    
    current_price = get_price_at_time(time, hour_prices, minute_prices)
    
    if conv_type == "full":
        difference = estimation-current_price
    elif conv_type == "dec":
        difference1 = estimation-current_price%1
        difference2 = estimation - current_price%1 + 1
        if abs(difference1) > abs(difference2): 
            difference = difference2
        else:
            difference = difference1
    #return round(difference,4)
    return st_dev_estimation(difference,price_stdev)

def find_estimations(comment,time, price_vectors): #find estimation in a comment line
    for word in range(len(comment)):
        try:
            float(comment[word])
            if bool(re.search("\d\.\d*",comment[word])):
                comment[word]= convert_estimation(time, float(comment[word]),"full",price_vectors)
            elif bool(re.search("\.\d*",comment[word])) and float(comment[word])<1:
                comment[word]= convert_estimation(time,float(comment[word]),"dec",price_vectors)
            elif float(comment[word])>=1 and float(comment[word])<10:
                comment[word]=convert_estimation(time,float(comment[word]),"full",price_vectors)
        except ValueError:
            pass
    return comment

def st_dev_estimation(estimation_diff, stdev): #Further process estimation to enable tokenization
    stdev_change = int(estimation_diff/stdev)
    return "stdev_guess:"+str(stdev_change)