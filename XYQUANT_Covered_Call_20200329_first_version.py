#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import datetime
import glob
import calendar
import math
import codecs
import os
import sys
import statsmodels.api as sm
from matplotlib import rc
from datetime import timedelta


# # 导入数据

# In[4]:


path = 'E:\\信息传递——数据、代码和论文\\50ETF-option-20170103-20190918\\50etf_日'
os.chdir(path)
datalist = []
for i in os.listdir(path):
    if os.path.splitext(i)[1] == '.txt':#选取后缀为txt的文件加入datalist
        datalist.append(i)
        
trading_date = pd.read_csv('date_170103_190918.csv')
data_etf = pd.read_csv('data_etf_day.csv')
data_etf.columns = ['date','open','close','high','low','volume','money']
data_index = pd.read_csv('data_index.csv')


# # 函数1：计算每天本月期权到期日和移仓日以及下月期权到期日

# In[5]:


## weekday和week参数表示第几周的第几天进行移仓或者期权到期
def special_date(year,month,week,weekday):
    d_option = 1
    while(calendar.weekday(year,month,d_option)!= (weekday-1)):
        d_option = d_option + 1
    temp = datetime.datetime.strftime(datetime.date(year,month,d_option + (week-1)*7),"%Y-%m-%d")
    
    return temp


# # 函数2：计算每天期权收益

# In[11]:


def option_retun_function(expire_date,moneyness):
    ## 如果现在还没有到换仓的时候，只需要近月、虚值、看涨期权
    ## 如果到了换仓日且还没有进入下一个月时，就需要次近月、虚值、看涨期权
    ## 如果到了新的一个月，此时还是只需要近月、虚值、看涨期权
    
    # 找到昨天交易的认购期权
    temp_option = yesterday_option_data[(yesterday_option_data['到期日'] == expire_date)]
    # 找到在值程度最接近1.05的虚值认购期权的行权价
    temp_strike = min(temp_option['行权价格'], key = lambda x: (abs(x / data_etf['close'][i-1] - moneyness), x))
    # 找到近月虚值期权的今日结算价
    yesterday_option_price = float(temp_option[(temp_option['行权价格'] == temp_strike)]['收盘价'].tolist()[0])
    # 找到近月虚值期权的今日结算价
    today_option_price = float(today_option_data[(today_option_data['到期日'] == expire_date) & (today_option_data['行权价格'] == temp_strike) & (today_option_data['合约类型'] == 'CO')]['收盘价'].tolist()[0])
    # 计算期权收益率
    option_ret = ( yesterday_option_price - today_option_price) / data_etf['close'][i-1]
    
    return option_ret


# # 获取日期数据以及期权到期、展期的数据并计算现货和期权的收益率

# In[13]:


initial_money = 1 
money = [initial_money]

for i in range(1,len(trading_date)):
    yesterday = trading_date['date'].tolist()[i-1]
    today = trading_date['date'].tolist()[i]
    yesterday_year = datetime.datetime.strptime(yesterday,'%Y-%m-%d').year
    yesterday_month = datetime.datetime.strptime(yesterday,'%Y-%m-%d').month

    if yesterday_month == 12:
        next_year = yesterday_year + 1
        next_month = 1
    else:
        next_year = yesterday_year
        next_month = yesterday_month + 1
    
    option_end = special_date(yesterday_year,yesterday_month,4,3)
    option_roll = special_date(yesterday_year,yesterday_month,3,4)
    next_option_end = special_date(next_year,next_month,4,3)
    
    # 计算从昨天到今天的现货收益率
    etf_return = (data_etf['close'][i]/data_etf['close'][i-1]) 
    # 找到昨天和今天交易的期权列表
    yesterday_option_data = pd.read_table(yesterday + '.txt',sep="\t")
    today_option_data =  pd.read_table(today + '.txt',sep="\t")

    if yesterday < option_roll:
        option_retun = option_retun_function(option_end,1.05)
    else:
        option_retun = option_retun_function(next_option_end,1.05)
    
    money.append(money[i-1]*(0.85*etf_return + 0.15*(1 + 0.85/0.15*option_retun)))


# In[14]:


money


# In[7]:


i = 50
# 在计算今天的收益时，需要依赖的是昨天的数据
yesterday = trading_date['date'].tolist()[i-1]
today = trading_date['date'].tolist()[i]
yesterday_year = datetime.datetime.strptime(yesterday,'%Y-%m-%d').year
yesterday_month = datetime.datetime.strptime(yesterday,'%Y-%m-%d').month

if yesterday_month == 12:
    next_year = yesterday_year + 1
    next_month = 1
else:
    next_year = yesterday_year
    next_month = yesterday_month + 1
    
option_end = special_date(yesterday_year,yesterday_month,4,3)
option_roll = special_date(yesterday_year,yesterday_month,3,4)
next_option_end = special_date(next_year,next_month,4,3)


# In[8]:


# 计算从昨天到今天的现货收益率
today_etf_return = (data_etf['close'][i] - data_etf['close'][i-1]) / data_etf['close'][i-1]
# 找到昨天和今天交易的期权列表
yesterday_option_data = pd.read_table(yesterday + '.txt',sep="\t")
today_option_data =  pd.read_table(today + '.txt',sep="\t")

if yesterday < option_roll:
    option_retun = -option_retun_function(option_end,1.05)
else:
    option_retun = -option_retun_function(next_option_end,1.05)


# In[ ]:




