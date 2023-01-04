import re
from urllib.parse import ParseResult, urlencode, urlunparse
from urllib import parse
import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta

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

def No_space(text):
    text1 = re.sub('&nbsp; | &nbsp;| \n|\t|\r|\n', '', text)
    text2 = re.sub('\n\n|,', '', text1)
    text3 = text2.rstrip(' ')
    text4 = text3.lstrip(' ')
    return text4

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
    return df_tmp

if __name__ == "__main__":
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

    df = pd.DataFrame(columns = ['업무', '공고번호', '분류', '공고명', '공고기관',
                                 '수요기관', '계약방법', '입력일시(입찰마감일시)', '공동수급', '투찰', '링크'])

    print('스크래핑 시작, 종료년도를 입력하세요. 같은년도를 입력시 해당 년의 자료만 스크래핑됩니다.')
    year1 = input('스크래핑할 시작년도를 입력하세요. : ')
    year2 = input('스크래핑할 종료년도를 입력하세요. : ')

    start_year = int(year1) # 시작년도 입력
    end_year = int(year2)   # 종료년도 입력

    for y in range(start_year, end_year+1):
        date_ext = Date_extract(y)
        df.to_csv(str('./nara_' + str(y) + '.csv'), encoding='utf-8')
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
                df.to_csv(str('./nara_' + str(y) + '.csv'), header=False, mode='a', encoding='utf-8')
            print(str(y) + ' ' + start_tmp[0] + ' / 12 Done!')
        print(str(y) + ' Done!')

