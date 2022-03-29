#!/usr/bin/env python
# coding: utf-8

# In[46]:


from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import re
from urllib.parse import urljoin, ParseResult, parse_qs, urlparse, parse_qsl, urlencode, urlunparse
from urllib import parse
import requests
import pandas as pd
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time
from datetime import datetime, timedelta


# In[47]:


# 파싱 데이터에 대한 데이터 처리(줄바꿈 등)
def No_space(text):
    text1 = re.sub('&nbsp; | &nbsp;| \n|\t|\r|\n', '', text)
    text2 = re.sub('\n\n|,', '', text1)
    text3 = text2.rstrip(' ')
    text4 = text3.lstrip(' ')
    return text4


# In[54]:


# 데이터 스크래핑
def Scrap_data(url, bid_code, seq, project):
    df_tmp = pd.DataFrame(columns = ['번호', '공고명', '순위', '사업자등록번호', '업체명',
                                     '대표자명', '입찰금액(원)', '투찰률(%)', '추첨번호', '입찰일시', '비고'])
    res = requests.get(url)
    time.sleep(0.2)
    bs_obj = BeautifulSoup(res.content, 'html.parser')
    try:
        table = bs_obj.find("table",{"class":"table_list table_list_serviceBidResultTbl1"})
        trs = table.findAll('tr')
    except:
        return df_tmp
    for i in range(1,len(trs)):
        tds = trs[i].findAll('td')
        d_list = []
        d_list = ['-'.join([bid_code, seq]), project]
        for j in tds:
            if j.text == '검색된 데이터가 없습니다.':
                break
            tmp = No_space(j.text)
            d_list.append(tmp)
        dfs = pd.Series(d_list, index = df_tmp.columns)
        df_tmp = df_tmp.append(dfs, ignore_index = True)
    return df_tmp      


# In[55]:


#URL unparsing을 위한 쿼리 세팅
scheme='https'
netloc='www.g2b.go.kr:8101'
path='/ep/result/serviceBidResultDtl.do'
params=''
qs=[('bidno', '20220209048'),
    ('bidseq', '01'),
    ('releaseYn', 'Y'),
    ('taskClCd', '5')]
fragment=''
query = urlencode(qs, quote_via=parse.quote)
parts = ParseResult(scheme, netloc, path, params, query, fragment)
url = urlunparse(parts)


# In[56]:


# 메인 스크립트
df = pd.DataFrame(columns = ['번호', '공고명', '순위', '사업자등록번호', '업체명',
                             '대표자명', '입찰금액(원)', '투찰률(%)', '추첨번호', '입찰일시', '비고'])

filename = r'C:\Users\1907043\Documents\py\bid_code.csv'
try:
    codes = pd.read_csv(filename, dtype=str, encoding='utf-8')
except:
    print("입력 파일이 존재하지 않습니다.")

for idx, c in codes.iterrows():
    bid_code, seq = c[2].split('-')
    qs[0] = ('bidno', bid_code)
    qs[1] = ('bidseq', seq)
    project = c[4]
    query=urlencode(qs, quote_via=parse.quote)
    parts = ParseResult(scheme, netloc, path, params, query, fragment)
    url = urlunparse(parts)
    df = Scrap_data(url, bid_code, seq, project)
    df.to_csv(str('C:/Users/1907043/Documents/' + 'nara_bidder_specific' + '.csv'), header=False, mode='a', encoding='utf-8')
    df = pd.DataFrame(columns = ['번호', '공고명', '순위', '사업자등록번호', '업체명',
                                 '대표자명', '입찰금액(원)', '투찰률(%)', '추첨번호', '입찰일시', '비고'])
print('All Done!')


# -----------------------

# ## 테스트/디버깅 영역

# In[30]:


df


# In[76]:


Scrap_data(url, bid_code, seq, project)


# In[ ]:





# In[11]:



a = 'https://www.g2b.go.kr:8101/ep/result/serviceBidResultDtl.do?bidno=20190100210&bidseq=00&releaseYn=Y&taskClCd=5'
b = 'https://www.g2b.go.kr:8101/ep/result/serviceBidResultDtl.do?bidno=20220209048&bidseq=01&releaseYn=Y&taskClCd=5'
b


# In[53]:


url = parse.urlparse('https://www.g2b.go.kr:8101/ep/result/serviceBidResultDtl.do?bidno=20220209048&bidseq=01&releaseYn=Y&taskClCd=5')


# In[54]:


parse_qsl(url.query)


# In[9]:


#URL unparsing을 위한 쿼리 세팅
scheme='https'
netloc='www.g2b.go.kr:8101'
path='/ep/result/serviceBidResultDtl.do'
params=''
query=[('bidno', '20220209048'),
     ('bidseq', '01'),
     ('releaseYn', 'Y'),
     ('taskClCd', '5')]
fragment=''
query = urlencode(qs, quote_via=parse.quote)
parts = ParseResult(scheme, netloc, path, params, query, fragment)
url = urlunparse(parts)


# In[10]:


parts = ParseResult(scheme, netloc, path, params, query, fragment)


# In[11]:


url = urlunparse(parts)


# In[12]:


res = requests.get(url)


# In[14]:


bs_obj = BeautifulSoup(res.content, 'html.parser')


# In[31]:


def No_space(text):
    text1 = re.sub('&nbsp; | &nbsp;| \n|\t|\r|\n', '', text)
    text2 = re.sub('\n\n|,', '', text1)
    text3 = text2.rstrip(' ')
    text4 = text3.lstrip(' ')
    return text4


# In[44]:


df_tmp = pd.DataFrame(columns = ['번호', '공고명', '순위', '사업자등록번호', '업체명', '대표자명', '입찰금액(원)', '투찰률(%)', '추첨번호', '입찰일시', '비고'])
table = bs_obj.find("table",{"class":"table_list table_list_serviceBidResultTbl1"})
trs = table.findAll('tr')
for i in range(1,len(trs)):
    tds = trs[i].findAll('td')
    d_list = []
    d_list = ['no', '공고명']
    for j in tds:
        if j.text == '검색된 데이터가 없습니다.':
            break
        tmp = No_space(j.text)
        d_list.append(tmp)
    dfs = pd.Series(d_list, index = df_tmp.columns)
    df_tmp = df_tmp.append(dfs, ignore_index = True)


# In[45]:


df_tmp


# In[ ]:




df_tmp = pd.DataFrame(columns = {'업무', '공고번호', '분류', '공고명', '공고기관',
                                     '수요기관', '계약방법', '입력일시(입찰마감일시)', '공동수급', '투찰', '링크'})
res = requests.get(url)
time.sleep(0.5)
bs_obj = BeautifulSoup(res.content, 'html.parser')
table = bs_obj.find("table",{"class":"table_list_tbidTbl table_list"})
trs = table.findAll('tr')
for i in range(1, len(trs)):
    tds = trs[i].findAll('td')
    d_list = []
    for j in tds:
        if j.text == '검색된 데이터가 없습니다.':
            return df_tmp
        d_list.append(j.text)
    link = tds[1].find("a")["href"]
    d_list.append(link)
    dfs = pd.Series(d_list, index = df_tmp.columns)
    df_tmp = df_tmp.append(dfs, ignore_index = True)

