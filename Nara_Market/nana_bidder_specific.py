import re
from urllib.parse import ParseResult, urlencode, urlunparse
from urllib import parse
import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
from tqdm import tqdm

def No_space(text):
    text1 = re.sub('&nbsp; | &nbsp;| \n|\t|\r|\n', '', text)
    text2 = re.sub('\n\n|,', '', text1)
    text3 = text2.rstrip(' ')
    text4 = text3.lstrip(' ')
    return text4

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
        df_tmp = pd.concat([df_tmp, dfs.to_frame().T], ignore_index=True)
    return df_tmp

if __name__ == '__main__':
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

    # 메인 스크립트
    df = pd.DataFrame(columns = ['번호', '공고명', '순위', '사업자등록번호', '업체명',
                                 '대표자명', '입찰금액(원)', '투찰률(%)', '추첨번호', '입찰일시', '비고'])

    filename = input('파일명을 입력해주세요. (예. nara_2022.csv) : ')

    try:
        codes = pd.read_csv(filename, dtype=str, encoding='utf-8')
    except:
        print("입력 파일이 존재하지 않습니다.")

    for idx, c in tqdm(codes.iterrows(), total=len(codes)):
        bid_code, seq = c[3].split('-')
        qs[0] = ('bidno', bid_code)
        qs[1] = ('bidseq', seq)
        project = c[4]
        query=urlencode(qs, quote_via=parse.quote)
        parts = ParseResult(scheme, netloc, path, params, query, fragment)
        url = urlunparse(parts)
        df = Scrap_data(url, bid_code, seq, project)
        df.to_csv(str('./' + 'nara_bidder_specific' + '.csv'), mode='a', encoding='utf-8')
        df = pd.DataFrame(columns = ['번호', '공고명', '순위', '사업자등록번호', '업체명',
                                     '대표자명', '입찰금액(원)', '투찰률(%)', '추첨번호', '입찰일시', '비고'])
    print('All Done!')
