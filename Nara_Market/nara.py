#!/usr/bin/env python
# coding: utf-8

# In[1]:


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


# In[2]:


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


# In[3]:


# 파싱 데이터에 대한 데이터 처리(줄바꿈 등)
def No_space(text):
    text1 = re.sub('&nbsp; | &nbsp;| \n|\t|\r|\n', '', text)
    text2 = re.sub('\n\n|,', '', text1)
    text3 = text2.rstrip(' ')
    text4 = text3.lstrip(' ')
    return text4


# In[6]:


# 데이터 스크래핑
def Scrap_data(url):
    df_tmp = pd.DataFrame(columns = ['업무', '공고번호', '분류', '공고명', '공고기관',
                                     '수요기관', '계약방법', '입력일시(입찰마감일시)', '공동수급', '투찰', '링크'])
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
    print(df_tmp)
    return df_tmp      


# In[7]:


#URL unparsing을 위한 쿼리 세팅
scheme='https'
netloc='www.g2b.go.kr:8101'
path='/ep/tbid/tbidList.do'
params=''
qs = [('searchType', '1'),
        ('bidSearchType', '1'),
        ('taskClCds', '5'),
        ('searchDtType', '1'),
        ('fromBidDt', '2021/01/01'),
        ('toBidDt', '2021/01/31'),
        ('currentPageNo', '1'),
        ('setMonth1', '3'),
        ('radOrgan', '1'),
        ('regYn', 'Y'),
        ('recordCountPerPage', '100')]
fragment = ''
query = urlencode(qs, quote_via=parse.quote)
parts = ParseResult(scheme, netloc, path, params, query, fragment)
url = urlunparse(parts)


# In[8]:


df = pd.DataFrame(columns = ['업무', '공고번호', '분류', '공고명', '공고기관',
                             '수요기관', '계약방법', '입력일시(입찰마감일시)', '공동수급', '투찰', '링크'])

start_year = 2022 # 시작년도 입력
end_year = 2022   # 종료년도 입력

for y in range(start_year, end_year+1):
    date_ext = Date_extract(y)
    for k, v in date_ext.items():
        start_tmp = [k, v[0]]
        end_tmp = [k, v[1]]
        page_no = 1
        fromBidDt = f'{y}/{start_tmp[0]}/{start_tmp[1]}'
        toBidDt = f'{y}/{end_tmp[0]}/{end_tmp[1]}'
        qs[4] = ('fromBidDt', fromBidDt)
        qs[5] = ('toBidDt', toBidDt)
        while True:
            qs[6] = ('currentPageNo', page_no)
            query=urlencode(qs, quote_via=parse.quote)
            parts = ParseResult(scheme, netloc, path, params, query, fragment)
            url = urlunparse(parts)
            df_tmp = Scrap_data(url)
            if len(df_tmp) == 0:
                break
            df = pd.concat([df, df_tmp])
            page_no += 1
            df.to_csv(str('C:/Users/1907043/Documents/' + 'nara_' + str(y) + '.csv'), header=False, mode='a', encoding='utf-8')
            df = pd.DataFrame(columns = ['업무', '공고번호', '분류', '공고명', '공고기관', '수요기관', '계약방법',
                                         '입력일시(입찰마감일시)', '공동수급', '투찰', '링크'])
        print(str(y) + ' ' + start_tmp[0] + ' / 12 Done!')
    print(str(y) + ' Done!')


# ----------------------

# ## 테스트/디버깅 영역

# In[33]:


url = parse.urlparse('https://www.g2b.go.kr:8101/ep/tbid/tbidList.do?searchType=1&bidSearchType=1&taskClCds=5&bidNm=&searchDtType=1&fromBidDt=2021%2F01%2F01&toBidDt=2021%2F01%2F31&setMonth1=3&fromOpenBidDt=&toOpenBidDt=&radOrgan=1&instNm=&instSearchRangeType=&refNo=&area=&areaNm=&strArea=&orgArea=&industry=&industryCd=&upBudget=&downBudget=&budgetCompare=&detailPrdnmNo=&detailPrdnm=&procmntReqNo=&intbidYn=&regYn=Y&recordCountPerPage=100')


# In[34]:


url


# In[35]:


parse_qsl(url.query)


# In[13]:


y = 2021
start_tmp = ['01' ,'01']
end_tmp = ['01', '31']
start_date = f'{y}%2F{start_tmp[0]}%2F{start_tmp[1]}'
end_date = f'{y}%2F{end_tmp[0]}%2F{end_tmp[1]}'
page_no = 1
url = f'https://www.g2b.go.kr:8101/ep/tbid/tbidList.do?area=&areaNm=&bidNm=&bidSearchType=1&budget=&budgetCompare=UP&detailPrdnm=&detailPrdnmNo=&fromBidDt={start_date}&fromOpenBidDt=&industry=&industryCd=&instNm=&instSearchRangeType=&intbidYn=&orgArea=&procmntReqNo=&radOrgan=1&recordCountPerPage=100&refNo=&regYn=Y&searchDtType=1&searchType=1&setMonth1=3&strArea=&taskClCds=5&toBidDt={end_date}&toOpenBidDt=&currentPageNo={page_no}&maxPageViewNoByWshan=1&'
url


# In[14]:


url = 'https://www.g2b.go.kr:8101/ep/tbid/tbidList.do?area=&bidNm=&bidSearchType=1&fromBidDt=2021%2F07%2F25&fromOpenBidDt=&radOrgan=4&regYn=Y&searchDtType=1&searchType=1&taskClCds=&toBidDt=2022%2F01%2F25&toOpenBidDt=&currentPageNo=2&maxPageViewNoByWshan=2&'
res = requests.get(url)
bs_obj = BeautifulSoup(res.content, 'html.parser')
table = bs_obj.find("table",{"class":"table_list_tbidTbl table_list"})
url


# In[12]:


trs = table.findAll('tr')
tds = trs[1].findAll('td')


# In[16]:


for i in tds:
    print(i.text)


# In[28]:


url = 'https://www.g2b.go.kr/pt/menu/'
url_sub = '/selectSubFrame.do?framesrc=/pt/menu/frameTgong.do?url=https://www.g2b.go.kr:8101/ep/tbid/tbidList.do?taskClCds=&bidNm=&searchDtType=1&fromBidDt=2021/07/25&toBidDt=2022/01/25&fromOpenBidDt=&toOpenBidDt=&radOrgan=2&instNm=%C7%D1%B1%B9%B3%B2%B5%BF%B9%DF%C0%FC(%C1%D6)&area=&regYn=Y&bidSearchType=1&searchType=1'


# In[5]:


url = 'https://www.g2b.go.kr:8101/ep/tbid/tbidList.do?area=&bidNm=&bidSearchType=1&fromBidDt=%s&fromOpenBidDt=&radOrgan=4&regYn=Y&searchDtType=1&searchType=1&taskClCds=&toBidDt=2022%2F01%2F26&toOpenBidDt=&currentPageNo=%s&maxPageViewNoByWshan=2&'
res = requests.get(url)
bs_obj = BeautifulSoup(res.content, 'html.parser')
table = bs_obj.find("table",{"class":"table_list_tbidTbl table_list"})


# In[8]:


df


# In[109]:


'https://www.g2b.go.kr:8101/ep/tbid/tbidList.do?area=&bidNm=&bidSearchType=1&fromBidDt={start_date}&fromOpenBidDt=&radOrgan=4&regYn=Y&searchDtType=1&searchType=1&taskClCds=&toBidDt={end_date}&toOpenBidDt=&currentPageNo={page_no}&maxPageViewNoByWshan=1&'


# In[108]:


'https://www.g2b.go.kr:8101/ep/tbid/tbidFwd.do?area=&areaNm=&bidNm=&bidSearchType=1&budget=&budgetCompare=UP&detailPrdnm=&detailPrdnmNo=&fromBidDt=2021%2F07%2F26&fromOpenBidDt=&industry=&industryCd=&instNm=&instSearchRangeType=&intbidYn=&orgArea=&procmntReqNo=&radOrgan=1&recordCountPerPage=100&refNo=&regYn=Y&searchDtType=1&searchType=1&setMonth1=3&strArea=&taskClCds=5&toBidDt=2022%2F01%2F26&toOpenBidDt='


# In[114]:


'https://www.g2b.go.kr:8101/ep/tbid/tbidList.do?area=&areaNm=&bidNm=&bidSearchType=1&budget=&budgetCompare=UP&detailPrdnm=&detailPrdnmNo=&fromBidDt=2021%2F01%2F01&fromOpenBidDt=&industry=&industryCd=&instNm=&instSearchRangeType=&intbidYn=&orgArea=&procmntReqNo=&radOrgan=1&recordCountPerPage=100&refNo=&regYn=Y&searchDtType=1&searchType=1&setMonth1=3&strArea=&taskClCds=5&toBidDt=2021%2F01%2F31&toOpenBidDt=toOpenBidDt=&currentPageNo=500&maxPageViewNoByWshan=1&'


# In[60]:


trs[2]


# In[26]:


trs = table.findAll('tr')
tds = trs[1].findAll('td')


# In[42]:


trs[0]


# In[39]:


d_list = []
for i in tds:
    d_list.append(i.text)


# In[27]:


tds[0].text == '검색된 데이터가 없습니다.'


# In[61]:


df = pd.DataFrame(columns = {'업무', '공고번호', '분류', '공고명', '공고기관', '수요기관', '계약방법', '입력일시(입찰마감일시)', '공동수급', '투찰'})


# In[62]:


len(df)


# In[41]:


d_list


# In[44]:


df.append(pd.Series(d_list, index = df.columns), ignore_index = True)


# In[85]:


df


# In[29]:


session = requests.Session()
response = session.get(URL, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'})
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)


# In[30]:


soup = BeautifulSoup(response.text)
frames = soup.find_all('frame')
header_link = [urljoin(BASE_URL, frame.get('src')) for frame in frames]


# In[27]:


url = 'https://www.g2b.go.kr:8101/ep/tbid/tbidList.do?area=&bidNm=&bidSearchType=1&fromBidDt=2021%2F07%2F25&fromOpenBidDt=&radOrgan=4&regYn=Y&searchDtType=1&searchType=1&taskClCds=&toBidDt=2022%2F01%2F25&toOpenBidDt=&currentPageNo=2&maxPageViewNoByWshan=2&'
url = parse.urlparse('https://www.g2b.go.kr:8101/ep/tbid/integrationWbidderList.do?area=&areaNm=&bidNm=&bidSearchType=1&budget=&budgetCompare=UP&detailPrdnm=&detailPrdnmNo=&fromBidDt={start_date}&fromOpenBidDt=&industry=&industryCd=&instNm=&instSearchRangeType=&intbidYn=&orgArea=&procmntReqNo=&radOrgan=1&recordCountPerPage=100&refNo=&regYn=Y&searchDtType=1&searchType=1&setMonth1=3&strArea=&taskClCds=5&toBidDt={end_date}&toOpenBidDt=&currentPageNo={page_no}&maxPageViewNoByWshan=1&')
url


# In[28]:


parse_qsl(url.query)


# In[ ]:





# In[32]:


header_link


# In[ ]:


header_link, document_link = [urljoin(BASE_URL, frame.get('src')) for frame in frames]

