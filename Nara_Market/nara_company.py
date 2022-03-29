#!/usr/bin/env python
# coding: utf-8

# In[6]:


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


# In[7]:


# 년, 월별 시작일, 종료일 추출 함수 (2월 29일이 있는 경우에 대한 예외 처리)
def Date_extract(year):
    date_list = []
    dt = datetime(year, 1, 1)
    date_list.append(dt)
    while True:
        dt = dt + timedelta(1)
        if dt.year == year+1:
            break
        date_list.append(dt)
    date_dic = dict()
    tmp = []
    from itertools import groupby
    group = groupby(date_list, lambda x: x.month)
    for key, items in group:
        for item in items:
            tmp.append(item.day)
        date_dic[str("{:02d}".format(key))] = [str("{:02d}".format(min(tmp))), str("{:02d}".format(max(tmp)))]
        tmp = []
    return date_dic


# In[8]:


# 파싱 데이터에 대한 데이터 처리(줄바꿈 등)
def No_space(text):
    text1 = re.sub('&nbsp; | &nbsp;| \n|\t|\r|\n', '', text)
    text2 = re.sub('\n\n|,', '', text1)
    text3 = text2.rstrip(' ')
    text4 = text3.lstrip(' ')
    return text4


# In[9]:


# 데이터 스크래핑
def Scrap_data(url):
    df_tmp = pd.DataFrame(columns = ['업무', '공고번호', '재입찰', '공고명', '수요기관', '개찰일시', '참가수', '낙찰자', '낙찰금액(원)', '낙찰률'])
    res = requests.get(url)
    time.sleep(0.5)
    bs_obj = BeautifulSoup(res.content, 'html.parser')
    table = bs_obj.find("table",{"class":"table_list at_table_list"})
    trs = table.findAll('tr')
    for i in range(1, len(trs)):
        tds = trs[i].findAll('td')
        d_list = []
        if tds[0].text == '검색된 데이터가 없습니다.':
            return df_tmp
        for j in tds[:-2]:
            jj = j.text
            jj = No_space(jj)
            d_list.append(jj)
        dfs = pd.Series(d_list, index = df_tmp.columns)
        df_tmp = df_tmp.append(dfs, ignore_index = True)
    return df_tmp      


# In[10]:


#URL unparsing을 위한 쿼리 세팅
scheme='https'
netloc='www.g2b.go.kr:8101'
path='/ep/tbid/integrationWbidderList.do'
params=''
qs = [('bidSearchType', '1'),
     ('budgetCompare', 'UP'),
     ('fromBidDt', 'start_date'),
     ('radOrgan', '1'),
     ('recordCountPerPage', '100'),
     ('regYn', 'Y'),
     ('searchDtType', '1'),
     ('searchType', '1'),
     ('setMonth1', '3'),
     ('taskClCds', '5'),
     ('toBidDt', 'end_date'),
     ('currentPageNo', 'page_no'),
     ('maxPageViewNoByWshan', '1')]
fragment = ''
query = urlencode(qs, quote_via=parse.quote)
parts = ParseResult(scheme, netloc, path, params, query, fragment)
url = urlunparse(parts)


# In[12]:


# 메인 스크립트
df = pd.DataFrame(columns = ['업무', '공고번호', '재입찰', '공고명', '수요기관', '개찰일시', '참가수', '낙찰자', '낙찰금액(원)', '낙찰률'])

start_year = 2022  # 시작년도 입력
end_year = 2022    # 종료년도 입력

for y in range(start_year, end_year+1):
    date_ext = Date_extract(y)
    for k, v in date_ext.items():
        start_tmp = [k, v[0]]
        end_tmp = [k, v[1]]
        page_no = 1
        fromBidDt = f'{y}/{start_tmp[0]}/{start_tmp[1]}'
        toBidDt = f'{y}/{end_tmp[0]}/{end_tmp[1]}'
        qs[2] = ('fromBidDt', fromBidDt)
        qs[10] = ('toBidDt', toBidDt)
        while True:
            qs[11] = ('currentPageNo', page_no)
            query=urlencode(qs, quote_via=parse.quote)
            parts = ParseResult(scheme, netloc, path, params, query, fragment)
            url = urlunparse(parts)
            df_tmp = Scrap_data(url)
            if len(df_tmp) == 0:
                break
            df = pd.concat([df, df_tmp])
            page_no += 1
            df.to_csv(str('C:/Users/1907043/Documents/' + 'nara_bidder_' + str(y) + '.csv'), header=False, mode='a', encoding='utf-8')
            df = pd.DataFrame(columns = ['업무', '공고번호', '재입찰', '공고명', '수요기관', '개찰일시', '참가수', '낙찰자', '낙찰금액(원)', '낙찰률'])
        print(str(y) + ' ' + start_tmp[0] + ' / 12 Done!')

    print(str(y) + ' Done!')


# -------------------------

# ## 테스트/디버깅 영역

# In[34]:


df = pd.DataFrame(columns = {'업무', '공고번호', '재입찰', '공고명', '수요기관', '개찰일시', '참가수', '낙찰자', '낙찰금액(원)', '낙찰률'})
start_date = f'2021%2F01%2F01'
end_date = f'2021%2F02%2F29'
page_no = 88
url = f'https://www.g2b.go.kr:8101/ep/tbid/integrationWbidderList.do?area=&areaNm=&bidNm=&bidSearchType=1&budget=&budgetCompare=UP&detailPrdnm=&detailPrdnmNo=&fromBidDt={start_date}&fromOpenBidDt=&industry=&industryCd=&instNm=&instSearchRangeType=&intbidYn=&orgArea=&procmntReqNo=&radOrgan=1&recordCountPerPage=100&refNo=&regYn=Y&searchDtType=1&searchType=1&setMonth1=3&strArea=&taskClCds=5&toBidDt={end_date}&toOpenBidDt=&currentPageNo={page_no}&maxPageViewNoByWshan=1&'
print(url)
df_tmp = Scrap_data(url)
df = pd.concat([df, df_tmp])
page_no += 88
url = f'https://www.g2b.go.kr:8101/ep/tbid/integrationWbidderList.do?area=&areaNm=&bidNm=&bidSearchType=1&budget=&budgetCompare=UP&detailPrdnm=&detailPrdnmNo=&fromBidDt={start_date}&fromOpenBidDt=&industry=&industryCd=&instNm=&instSearchRangeType=&intbidYn=&orgArea=&procmntReqNo=&radOrgan=1&recordCountPerPage=100&refNo=&regYn=Y&searchDtType=1&searchType=1&setMonth1=3&strArea=&taskClCds=5&toBidDt={end_date}&toOpenBidDt=&currentPageNo={page_no}&maxPageViewNoByWshan=1&'
df_tmp = Scrap_data(url)
df = pd.concat([df, df_tmp])
page_no += 90
url = f'https://www.g2b.go.kr:8101/ep/tbid/integrationWbidderList.do?area=&areaNm=&bidNm=&bidSearchType=1&budget=&budgetCompare=UP&detailPrdnm=&detailPrdnmNo=&fromBidDt={start_date}&fromOpenBidDt=&industry=&industryCd=&instNm=&instSearchRangeType=&intbidYn=&orgArea=&procmntReqNo=&radOrgan=1&recordCountPerPage=100&refNo=&regYn=Y&searchDtType=1&searchType=1&setMonth1=3&strArea=&taskClCds=5&toBidDt={end_date}&toOpenBidDt=&currentPageNo={page_no}&maxPageViewNoByWshan=1&'
df_tmp = Scrap_data(url)
df = pd.concat([df, df_tmp])


# In[112]:


url = parse.urlparse('https://www.g2b.go.kr:8101/ep/tbid/integrationWbidderList.do?area=&areaNm=&bidNm=&bidSearchType=1&budget=&budgetCompare=UP&detailPrdnm=&detailPrdnmNo=&fromBidDt={start_date}&fromOpenBidDt=&industry=&industryCd=&instNm=&instSearchRangeType=&intbidYn=&orgArea=&procmntReqNo=&radOrgan=1&recordCountPerPage=100&refNo=&regYn=Y&searchDtType=1&searchType=1&setMonth1=3&strArea=&taskClCds=5&toBidDt={end_date}&toOpenBidDt=&currentPageNo={page_no}&maxPageViewNoByWshan=1&')


# In[113]:


url


# In[114]:


parse_qsl(url.query)


# In[ ]:


start_date = f'2021%2F01%2F01'
end_date = f'2021%2F01%2F31'
url = f'https://www.g2b.go.kr:8101/ep/tbid/integrationWbidderList.do?area=&areaNm=&bidNm=&bidSearchType=1&budget=&budgetCompare=UP&detailPrdnm=&detailPrdnmNo=&fromBidDt={start_date}&fromOpenBidDt=&industry=&industryCd=&instNm=&instSearchRangeType=&intbidYn=&orgArea=&procmntReqNo=&radOrgan=1&recordCountPerPage=100&refNo=&regYn=Y&searchDtType=1&searchType=1&setMonth1=3&strArea=&taskClCds=5&toBidDt={end_date}&toOpenBidDt=&currentPageNo={page_no}&maxPageViewNoByWshan=1&'


# In[51]:


a = """                            
                                20424000
                            
                           """


# In[ ]:




