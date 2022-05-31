import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from bs4 import BeautifulSoup
import time
import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import os
import os.path
import threading
import sys
from sys import argv
import copy
import random

class wait_for_page_load(object):
  def __init__(self, browser):
    self.browser = browser
  def __enter__(self):
    self.old_page = self.browser.find_element_by_tag_name('html')
  def page_has_loaded(self):
    new_page = self.browser.find_element_by_tag_name('html')
    return new_page.id != self.old_page.id
  def __exit__(self, *_):
    wait_for(self.page_has_loaded)

def wait_for(condition_function):
  start_time = time.time()
  while time.time() < start_time + 5:
    if condition_function():
      return True
    else:
      time.sleep(0.1)
  raise Exception(
   'Timeout waiting for {}')

# 리스트 소스 파일 찾기
def browsefiles():
    global filename
    filename = filedialog.askopenfilename(initialdir=run_directory, title="Select a File",
                                             filetypes=(("Code files", ("*.csv*", "*.txt*")),
                                                        ("all files", "*.*")))
    label_file_explorer.configure(text="File Opened: " + filename)
    status_insert("조회할 리스트 파일을 선택하고 시작해주세요.")
    return filename

# 크롤링 시작
def doit():
    if filename == "":
        tk.messagebox.showwarning("No File", "'Import' 버튼을 눌러 \n조회할 파일을 선택해주세요.")
    elif CheckVariety_1.get() + CheckVariety_1.get() + CheckVariety_1.get() == 0:
        tk.messagebox.showwarning("No Check", "조회할 항목을 선택해주세요.")
    else:
        if run_status[0] == 0:
            btn_text.set("정지")
            run_status[0] = 1
            status_insert("시작합니다.")
            th_scrap()
            button_status.config(state=NORMAL)
            button_start.config(command=stop)
        elif run_status[0] == 1:
            btn_text.set("시작")
            run_status[0] = 0
            button_start.config(command=doit)

# 상태창 문구 삽입
def status_insert(text):
    status_tracker.insert(END, text)
    status_tracker.see('end')
    scrollbar.config(command=status_tracker.yview)

# 상태창 비우기
def clear():
    status_tracker.delete(0,END)

# 크롤링 중지 명령
def stop():
    button_start.config(state=DISABLED)
    status_insert('조회를 중지합니다.')
    # if th_scrap_alive():
    #     th_scrap_join()
    # time.sleep(10)
    btn_text.set("시작")
    # button_start.config(state=NORMAL)
    status_insert('남은 목록은 ' + os.path.splitext(os.path.basename(filename))[0] + '_temp.csv' +'에 저장합니다.')
    status_insert('현재 버전은 중지 후 시작을 지원하지 않습니다.')
    status_insert('종료 및 재시작 후 ' + os.path.splitext(os.path.basename(filename))[0] + '_temp.csv을 선택해주세요.' )
    run_status[0] = 0
    # button_start.config(command=doit)

# 메인창 닫기
def window_on_close():
    close = messagebox.askokcancel("Cretop Scraper", "종료하시겠습니까?", parent=window)
    if close:
        if th_scrap_alive():
            th_scrap_join()
            time.sleep(1)
            sys.exit()
        else:
            sys.exit()

# 윈도우창 위로 올리기(미사용)
def raise_above_all(windows):
    window.attributes('topmost' ,1)
    window.attributes('topmost', 0)

# 크레탑 로그인
def cretop_login():
    search_status[0] = 1
    driver.get('http://www.cretop.com/en/ENCOM01R0.do')
    driver.implicitly_wait(5)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, 'passwd'))
    )
    driver.find_element_by_id('id').send_keys('******')
    driver.find_element_by_id('passwd').send_keys('******')
    time.sleep(random.uniform(1, 2))
    driver.find_element_by_id('loginBtn2').click()
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, '_srchNm'))
        )
    except:
        search_status[0] = 0
    return

# 사업자번호 검색 함수
def search_code(ccode):
    search_status[0] = 1
    try:
        driver.find_element_by_id('_srchNm').clear()
    except:
        # status_insert('오류 발생. 조회를 종료합니다.(1)')
        try:
            driver.refresh()
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            driver.switch_to.alert.accept()
            driver.implicitly_wait(5)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, '_srchNm'))
            )
            driver.implicitly_wait(5)
        except:
            status_insert('오류 발생. 조회를 종료합니다.(2)')
            search_status[0] = 0
            return
    try:
        driver.find_element_by_id('_srchNm').send_keys(ccode)
        time.sleep(random.uniform(3, 5))
        driver.find_element_by_id('_srchNm').send_keys(Keys.RETURN)
    except:
        status_insert('오류 발생. 조회를 종료합니다.(2)')
        search_status[0] = 0
        return
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, 'tb_bbs_list'))
    )
    return

# 사업자 선택 함수
def click_company(driver):
    # 사업자번호 검색 후 첫번째 항목 선택
    with wait_for_page_load(driver):
        elem = driver.find_element_by_xpath("//td[@class='first lf']/a")
        time.sleep(random.uniform(1, 4))
        elem.click()
    #
    # def link_has_gone_stale():
    #     try:
    #         # poll the link with an arbitrary call
    #         link.find_elements_by_id('doesnt-matter')
    #         return False
    #     except StaleElementReferenceException:
    #         return True
    #
    # def wait_for(condition_function):
    #     start_time = time.time()
    #     while time.time() < start_time + 5:
    #         if condition_function():
    #             return True
    #         else:
    #             time.sleep(0.1)
    #     raise Exception(
    #         'Timeout waiting')
    #
    # wait_for(link_has_gone_stale)

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, 'tbl_info'))
    )
    # time.sleep(2)
    # driver.implicitly_wait(5)

# 웹페이지 파싱 함수
def page_scrap():
    elet = driver.page_source
    soup = BeautifulSoup(elet, 'html.parser')
    return soup

# IE 재시작 함수
def re_open():
    global driver
    driver.quit()
    status_insert('메모리 관리를 위해 브라우저를 재시작합니다.')
    driver = webdriver.Chrome(executable_path=str(run_directory) + '\chromedriver.exe')
    driver.implicitly_wait(5)
    return

# 기업 정보 스크래핑 함수
def company_info(code):
    global d
    global df
    d = ["N/A" for j in range(26)]
    # 입력한 사업자(d0) 번호
    d[0] = code

    # 기업명(d1) 추출
    try:
        d1 = driver.find_element_by_xpath("//div[contains(@class, 'fl btns')]")
    except NoSuchElementException:
        d[1] = "개인사업자(조회불가)"
        return

    d[1] = d1.find_element_by_class_name('mtitle').text

    ev_table = soup.select('table.tb_bbs_list')
    ev = ev_table[0]
    if ev.select('td.first nodata h99') != []:
        d[24] = "등급없음"
        d[25] = "등급없음"
    else:
        try:
            ev_now = ev.select('td.first')[0].text
            d[24] = ev_now
        except:
            d[24] = "등급없음"
        try:
            ev_date = ev.select('td')[1].get_text()
            d[25] = ev_date
        except:
            d[25] = "등급없음"

    # 기업정보 테이블 크롤링
    try:
        info = soup.select('table.tbl_info')
        info = info[0]
    except:
        return

    # 사업자 번호(d2) 추출
    d[2] = info.find('th', scope='row').find_next_sibling('td').text

    # 종업원수(d3), 전화번호(d4) 추출
    try:
        d3s = info.find('th', id='ordnEm').find_next_sibling('td').text
    except:
        return

    d3s = str(d3s).split('/')
    d3 = d3s[0].strip()
    d[3] = d3.replace("명", "")  # '명' 단위 제거
    d[4] = d3s[1].strip()

    # 법인(주민)번호(d5) 추출
    d[5] = info.find('th', id='estbDt').find_next_sibling('td').text

    # 당좌거래은행(d6) 추출
    d[6] = info.find('th', id='ovdTxBnk').find_next_sibling('td').text

    # 대표자명(d7) 추출
    tds = info.findAll('td')
    d[7] = str(tds[4].get_text()).strip()

    # 우편번호(d8), 주소(d9) 추출
    d8s = str(tds[5].get_text()).strip()
    d8s = d8s.split('	')
    d[8] = str("(우)") + str(d8s[0].replace("(","").replace(")","").replace('\n', ''))
    d[9] = d8s[-1]

    # 업종 코드(d10) 얻기
    labels = info.findAll('label')
    d10 = labels[5].get_text()
    d[10] = d10.replace("업종(", "").replace(")", "")

    # 업종(d11) 추출
    d[11] = str(tds[6].get_text()).strip()  # 업종 코드 얻기

    # 기업인증현황(d12) 추출
    d12 = str(tds[7].get_text()).strip()
    d12 = d12.replace('\n', '').replace("	", "").strip()
    d[12] = d12.replace(" · ", '\n')

    # 설립일자(d13), 기업형태(d14) 추출
    d13s = str(tds[8].get_text()).strip()
    d13s = d13s.split('	')
    d[13] = d13s[0].replace("(", "").replace(")", "").replace('\n', '')
    d[14] = d13s[-1].replace("/", '').strip()

    # 기업인증현황(d15) 추출
    d15 = str(tds[9].get_text()).strip()
    d[15] = d15.replace(" · ", '\n').strip()

    # 휴폐업정보(d16), 일자(d17)
    credit = soup.find('div', {'class': 'major_credit_box'})
    try:
        d[16] = credit.findAll('span', class_='state')[0].get_text()
        d[17] = credit.findAll('span', class_='date')[0].get_text()
    except:
        return

    # 개인사업자에 따른 분기 처리
    if d[14] == "개인사업자":
        # 법원등기정보(d18)
        try:
            d[18] = credit.findAll('span', class_='state')[1].get_text()
        except:
            return
        # 기업채무불이행상태(d20), 일자(d21)
        try:
            d[20] = credit.findAll('span', class_='state')[2].get_text()
            d[21] = credit.findAll('span', class_='date')[1].get_text()
        except:
            return
        # 행정처분정보(d22), 일자(d23)
        try:
            d[22] = credit.findAll('span', class_='state')[3].get_text()
            d[23] = credit.findAll('span', class_='date')[2].get_text()
        except:
            return
    else:
        # 법원등기정보(d18), 일자(d19)
        try:
            d[18] = credit.findAll('span', class_='state')[1].get_text()
            d[19] = credit.findAll('span', class_='date')[1].get_text()
        except:
            return

        # 기업채무불이행상태(d20), 일자(d21)
        try:
            d[20] = credit.findAll('span', class_='state')[2].get_text()
            d[21] = credit.findAll('span', class_='date')[2].get_text()
        except:
            return

        # 행정처분정보(d22), 일자(d23)
        try:
            d[22] = credit.findAll('span', class_='state')[3].get_text()
            d[23] = credit.findAll('span', class_='date')[3].get_text()
        except:
            return

# 요약재무 스크래핑 함수
def statement_5y(code):
    global at
    global df2
    at = ["N/A" for k in range(37)]
    at[0] = code

    # 주요 재무제표 최근 5년 추출(재무상태표)
    try:
        statement5y = soup.findAll('table', {'class': 'tb_bbs_list mgb20'})[0]
    except:
        at[1] = '조회불가'
        return

    at[1] = '정상'

    # 기준년도 추출

    at[2] = statement5y.findAll('th', {'class': 'fw_nor'})[0].get_text().strip()
    at[3] = statement5y.findAll('th', {'class': 'fw_nor'})[1].get_text().strip()
    at[4] = statement5y.findAll('th', {'class': 'fw_nor'})[2].get_text().strip()
    at[5] = statement5y.findAll('th', {'class': 'fw_nor'})[3].get_text().strip()
    at[6] = statement5y.findAll('th', {'class': 'fw_nor'})[4].get_text().strip()

    # 자산총계 최근 5년 값 추출 (백만원)
    try:
        at[7] = statement5y.findAll('td', {'class': 'number'})[0].find('em').get_text().strip()
        at[8] = statement5y.findAll('td', {'class': 'number'})[1].find('em').get_text().strip()
        at[9] = statement5y.findAll('td', {'class': 'number'})[2].find('em').get_text().strip()
        at[10] = statement5y.findAll('td', {'class': 'number'})[3].find('em').get_text().strip()
        at[11] = statement5y.findAll('td', {'class': 'number'})[4].find('em').get_text().strip()

        # 부채총계 최근 5년 값 추출 (백만원)
        at[12] = statement5y.findAll('td', {'class': 'number'})[5].find('em').get_text().strip()
        at[13] = statement5y.findAll('td', {'class': 'number'})[6].find('em').get_text().strip()
        at[14] = statement5y.findAll('td', {'class': 'number'})[7].find('em').get_text().strip()
        at[15] = statement5y.findAll('td', {'class': 'number'})[8].find('em').get_text().strip()
        at[16] = statement5y.findAll('td', {'class': 'number'})[9].find('em').get_text().strip()

        # 자본총계 최근 5년 값 추출 (백만원)
        at[17] = statement5y.findAll('td', {'class': 'number'})[10].find('em').get_text().strip()
        at[18] = statement5y.findAll('td', {'class': 'number'})[11].find('em').get_text().strip()
        at[19] = statement5y.findAll('td', {'class': 'number'})[12].find('em').get_text().strip()
        at[20] = statement5y.findAll('td', {'class': 'number'})[13].find('em').get_text().strip()
        at[21] = statement5y.findAll('td', {'class': 'number'})[14].find('em').get_text().strip()
    except:
        return

    # 주요 재무제표 최근 5년 추출(손익계산서)
    try:
        income5y = soup.findAll('table', {'class': 'tb_bbs_list mgb20'})[1]
    except:
        return

    # 매출액 최근 5년 값 추출 (백만원)
    try:
        at[22] = income5y.findAll('td', {'class': 'number'})[0].find('em').get_text().strip()
        at[23] = income5y.findAll('td', {'class': 'number'})[1].find('em').get_text().strip()
        at[24] = income5y.findAll('td', {'class': 'number'})[2].find('em').get_text().strip()
        at[25] = income5y.findAll('td', {'class': 'number'})[3].find('em').get_text().strip()
        at[26] = income5y.findAll('td', {'class': 'number'})[4].find('em').get_text().strip()

        # 영업이익 최근 5년 값 추출 (백만원)
        at[27] = income5y.findAll('td', {'class': 'number'})[5].find('em').get_text().strip()
        at[28] = income5y.findAll('td', {'class': 'number'})[6].find('em').get_text().strip()
        at[29] = income5y.findAll('td', {'class': 'number'})[7].find('em').get_text().strip()
        at[30] = income5y.findAll('td', {'class': 'number'})[8].find('em').get_text().strip()
        at[31] = income5y.findAll('td', {'class': 'number'})[9].find('em').get_text().strip()

        # 순이익 최근 5년 값 추출 (백만원)
        at[32] = income5y.findAll('td', {'class': 'number'})[10].find('em').get_text().strip()
        at[33] = income5y.findAll('td', {'class': 'number'})[11].find('em').get_text().strip()
        at[34] = income5y.findAll('td', {'class': 'number'})[12].find('em').get_text().strip()
        at[35] = income5y.findAll('td', {'class': 'number'})[13].find('em').get_text().strip()
        at[36] = income5y.findAll('td', {'class': 'number'})[14].find('em').get_text().strip()
    except:
        return

# 주요재무 스크래핑 함수
def statement_3y(code):
    global bt
    global df3
    bt = ["N/A" for k in range(53)]
    bt[0] = code
    # 요약 재무제표 최근 3년 추출(재무상태표)

    try:
        statement3y = soup.findAll('table', {'class': 'tb_bbs_list mgb20'})[2]
    except:
        bt[1] = '조회불가'
        return

    bt[1] = '정상'

    # 기준년도 추출
    bt[2] = statement3y.findAll('th', {'scope': 'col'})[1].get_text().strip()
    bt[3] = statement3y.findAll('th', {'scope': 'col'})[2].get_text().strip()
    bt[4] = statement3y.findAll('th', {'scope': 'col'})[3].get_text().strip()

    try:
        # 유동자산 최근 3년 값 추출 (백만원)
        bt[5] = statement3y.findAll('td', {'class': 'number'})[0].get_text().strip()
        bt[6] = statement3y.findAll('td', {'class': 'number'})[1].get_text().strip()
        bt[7] = statement3y.findAll('td', {'class': 'number'})[2].get_text().strip()

        # 비유동자산 최근 3년 값 추출 (백만원)
        bt[8] = statement3y.findAll('td', {'class': 'number'})[3].get_text().strip()
        bt[9] = statement3y.findAll('td', {'class': 'number'})[4].get_text().strip()
        bt[10] = statement3y.findAll('td', {'class': 'number'})[5].get_text().strip()

        # 자산총계 최근 3년 값 추출 (백만원)
        bt[11] = statement3y.findAll('td', {'class': 'number'})[6].get_text().strip()
        bt[12] = statement3y.findAll('td', {'class': 'number'})[7].get_text().strip()
        bt[13] = statement3y.findAll('td', {'class': 'number'})[8].get_text().strip()

        # 유동부채 최근 3년 값 추출 (백만원)
        bt[14] = statement3y.findAll('td', {'class': 'number'})[9].get_text().strip()
        bt[15] = statement3y.findAll('td', {'class': 'number'})[10].get_text().strip()
        bt[16] = statement3y.findAll('td', {'class': 'number'})[11].get_text().strip()

        # 비유동부채 최근 3년 값 추출 (백만원)
        bt[17] = statement3y.findAll('td', {'class': 'number'})[12].get_text().strip()
        bt[18] = statement3y.findAll('td', {'class': 'number'})[13].get_text().strip()
        bt[19] = statement3y.findAll('td', {'class': 'number'})[14].get_text().strip()

        # 부채총계 최근 3년 값 추출 (백만원)
        bt[20] = statement3y.findAll('td', {'class': 'number'})[15].get_text().strip()
        bt[21] = statement3y.findAll('td', {'class': 'number'})[16].get_text().strip()
        bt[22] = statement3y.findAll('td', {'class': 'number'})[17].get_text().strip()

        # 자본금 최근 3년 값 추출 (백만원)
        bt[23] = statement3y.findAll('td', {'class': 'number'})[18].get_text().strip()
        bt[24] = statement3y.findAll('td', {'class': 'number'})[19].get_text().strip()
        bt[25] = statement3y.findAll('td', {'class': 'number'})[20].get_text().strip()

        # 자본총계 최근 3년 값 추출 (백만원)
        bt[26] = statement3y.findAll('td', {'class': 'number'})[21].get_text().strip()
        bt[27] = statement3y.findAll('td', {'class': 'number'})[22].get_text().strip()
        bt[28] = statement3y.findAll('td', {'class': 'number'})[23].get_text().strip()
    except:
        return

    # 요약 재무제표 최근 3년 추출(손익계산서)
    try:
        statement3y = soup.findAll('table', {'class': 'tb_bbs_list mgb20'})[3]
    except:
        return

    try:
        # bt[29] = statement3y.findAll('th', {'scope': 'col'})[1].get_text().strip()
        # bt[30] = statement3y.findAll('th', {'scope': 'col'})[2].get_text().strip()
        # bt[31] = statement3y.findAll('th', {'scope': 'col'})[3].get_text().strip()

        # 매출액 최근 3년 값 추출 (백만원)
        bt[29] = statement3y.findAll('td', {'class': 'number'})[0].get_text().strip()
        bt[30] = statement3y.findAll('td', {'class': 'number'})[1].get_text().strip()
        bt[31] = statement3y.findAll('td', {'class': 'number'})[2].get_text().strip()

        # 매출총이익 최근 3년 값 추출 (백만원)
        bt[32] = statement3y.findAll('td', {'class': 'number'})[3].get_text().strip()
        bt[33] = statement3y.findAll('td', {'class': 'number'})[4].get_text().strip()
        bt[34] = statement3y.findAll('td', {'class': 'number'})[5].get_text().strip()

        # 영업이익 최근 3년 값 추출 (백만원)
        bt[35] = statement3y.findAll('td', {'class': 'number'})[6].get_text().strip()
        bt[36] = statement3y.findAll('td', {'class': 'number'})[7].get_text().strip()
        bt[37] = statement3y.findAll('td', {'class': 'number'})[8].get_text().strip()

        # 영업외수익 최근 3년 값 추출 (백만원)
        bt[38] = statement3y.findAll('td', {'class': 'number'})[9].get_text().strip()
        bt[39] = statement3y.findAll('td', {'class': 'number'})[10].get_text().strip()
        bt[40] = statement3y.findAll('td', {'class': 'number'})[11].get_text().strip()

        # 영업외비용 최근 3년 값 추출 (백만원)
        bt[41] = statement3y.findAll('td', {'class': 'number'})[12].get_text().strip()
        bt[42] = statement3y.findAll('td', {'class': 'number'})[13].get_text().strip()
        bt[43] = statement3y.findAll('td', {'class': 'number'})[14].get_text().strip()

        # 법인세차감전순이익 최근 3년 값 추출 (백만원)
        bt[44] = statement3y.findAll('td', {'class': 'number'})[15].get_text().strip()
        bt[45] = statement3y.findAll('td', {'class': 'number'})[16].get_text().strip()
        bt[46] = statement3y.findAll('td', {'class': 'number'})[17].get_text().strip()

        # 법인세비용 최근 3년 값 추출 (백만원)
        bt[47] = statement3y.findAll('td', {'class': 'number'})[18].get_text().strip()
        bt[48] = statement3y.findAll('td', {'class': 'number'})[19].get_text().strip()
        bt[49] = statement3y.findAll('td', {'class': 'number'})[20].get_text().strip()

        # 당기순이익 최근 3년 값 추출 (백만원)
        bt[50] = statement3y.findAll('td', {'class': 'number'})[18].get_text().strip()
        bt[51] = statement3y.findAll('td', {'class': 'number'})[19].get_text().strip()
        bt[52] = statement3y.findAll('td', {'class': 'number'})[20].get_text().strip()
    except:
        return

# 검색 결과 없음 처리 함수
def no_search():
    global df
    global df2
    global df3
    if CheckVariety_1.get() == 1:
        d[0] = code
        d[1] = '조회불가'
        df = data_append(d, df)
        df.to_csv(str(run_directory) + '\기업정보_' +
                  os.path.splitext(os.path.basename(filename))[0] +
                  '.csv', header=False, mode='a', encoding='cp949')
        df.drop(df.index, inplace=True)
        status_insert('[' + code + ']' + ' 사업자 조회가 불가합니다.')
    if CheckVariety_2.get() == 1:
        at[0] = code
        at[1] = '조회불가'
        df2 = data_append(at, df2)
        df2.to_csv(str(run_directory) + '\주요재무_' +
                   os.path.splitext(os.path.basename(filename))[0] +
                   '.csv', header=False, mode='a', encoding='cp949')
        df2.drop(df2.index, inplace=True)
        status_insert('[' + code + ']' + ' 사업자 조회가 불가합니다.')
    if CheckVariety_3.get() == 1:
        bt[0] = code
        bt[1] = '조회불가'
        df3 = data_append(bt, df3)
        df3.to_csv(str(run_directory) + '\요약재무_' +
                   os.path.splitext(os.path.basename(filename))[0] +
                   '.csv', header=False, mode='a', encoding='cp949')
        df3.drop(df3.index, inplace=True)
        status_insert('[' + code + ']' + ' 사업자 조회가 불가합니다.')

# 리스트 형식 데이터 데이터프레임로 변환 저장
def data_append(data, frame):
    datas = pd.Series(data, index=frame.columns)
    frame = frame.append(datas, ignore_index=True)
    return (frame)

# 프로그레시브바 갱신
def progress_update(total_temp, start_time):
    max_number = total_temp
    current_value = count
    if max_number == 0:
        p_percentage = '%.2f'%float(0)
    else:
        p_percentage = '%.2f'%(float(current_value) / float(max_number) * 100)

    pbar['maximum'] = max_number
    pbar['value'] = current_value
    pbar.step()

    progress_time = time.time()
    remain_time = ((progress_time - start_time) / current_value) * (max_number - current_value)
    # progressbar_text.set(str(current_value) + ' / ' + str(max_number) + ' (' + str(p_percentage) + '%)')
    style.configure('text.Horizontal.TProgressbar', text=str(current_value) + ' / ' + str(max_number) + ' (' + str(p_percentage) + '%)'
                    + ' 남은시간 ' + str(datetime.timedelta(seconds = int(remain_time))))

# 임시 파일 저장
def temp_file_save(code_o):
    temp_save.remove(code_o)
    temp_df = pd.DataFrame(temp_save, columns = [""])
    temp_df.to_csv(tempname, header=False, mode='w', encoding='cp949', index=False)

# 스크랩 구동 메인 함수
def scrap():
    global driver
    global df
    global df2
    global df3
    global soup
    global code
    global code_o
    global d
    global at
    global bt
    global temp
    global count
    global tempname
    global temp_save
    count = 0
    i = 0  # 브라우저 메모리 누수에 따른 조회수 누적 카운트 변수

    # 저장 CSV 파일 준비
    try:
        df.to_csv(str(run_directory) + '\기업정보_' +
                  os.path.splitext(os.path.basename(filename))[0] + '.csv',
                  header=True, mode='w', encoding='cp949')
        df2.to_csv(str(run_directory) + '\주요재무_' +
                   os.path.splitext(os.path.basename(filename))[0] + '.csv',
                   header=True, mode='w', encoding='cp949')
        df3.to_csv(str(run_directory) + '\요약재무_' +
                   os.path.splitext(os.path.basename(filename))[0] + '.csv',
                   header=True, mode='w', encoding='cp949')
    except:
        tk.messagebox.showwarning("Opened Files", "저장할 csv 파일 실행중이므로,\n프로그램을 종료합니다.")
        stop()
        exit()

    # 브라우저 구동
    try:
        driver = webdriver.Chrome(executable_path=str(run_directory) + '\chromedriver.exe')
    except:
        status_insert('Driver 파일이 존재하지 않습니다.')
        exit()
    driver.implicitly_wait(5)

    # 코드파일 불러오기
    ccodes = pd.read_csv(filename, header=None, dtype=str, encoding='cp949')
    tempname = os.path.splitext(os.path.basename(filename))[0] + str("_temp") + ".csv"

    # 템프 파일 유무 확인 (현 버전에 미적용)
    # if os.path.exists(tempname):
    #     temp = pd.read_csv(tempname, header=None, dtype=str, encoding='cp949')
    #     temp = temp[0].tolist()
    # else:
    #     temp = ccodes.copy(deep=True)
    #     temp = temp[0].tolist()
    temp = ccodes.copy(deep=True)
    temp = temp[0].tolist()
    temp_save = copy.deepcopy(temp)

    # 프로그레시브 바 갱신
    style.configure('text.Horizontal.TProgressbar', text='0 / ' + str(len(temp)) + ' (0.00%)')
    total_temp = len(temp)
    search_status[0] = 1
    cretop_login()
    start_time = time.time()
    for code in temp:
        if i >= 1000:  # 30회 조회시 브라우저 종료 및 재구동 (조회불가 미포함)
            re_open()
            cretop_login()
            i = 0

        code_o = code
        code = str(code.replace("-",""))
        if run_status[0] == 0:
            driver.quit()
            exit()
            stop()

        # 더미 데이터프레임 생성
        d = ["N/A" for j in range(26)]
        at = ["N/A" for k in range(37)]
        bt = ["N/A" for k in range(53)]

        # 사업자번호 검색
        try:
            search_code(code)
        except:
            no_search()
            count += 1
            progress_update(total_temp, start_time)
            temp_file_save(code_o)
            i += 1
            continue

        # 중지 상태 감지
        if search_status[0] == 0:
            exit()
            stop()

        # 기업 선택
        try:
            click_company(driver)
        except:
            no_search()
            count += 1
            progress_update(total_temp, start_time)
            temp_file_save(code_o)
            i += 1
            continue

        # 소스 스크래핑
        soup = page_scrap()

        # 저장할 요소 구분하여 저장
        if CheckVariety_1.get() == 1:
            company_info(code)
            df = data_append(d, df)
            cname = d[1]
            # print(df)
            df.to_csv(str(run_directory) + '\기업정보_' +
                      os.path.splitext(os.path.basename(filename))[0] +
                      '.csv', header=False, mode='a', encoding='cp949')
            status_insert('[' + code + ']' + cname + ' 기업정보 조회가 완료되었습니다.')
            df.drop(df.index, inplace=True)
        if CheckVariety_2.get() == 1:
            statement_5y(code)
            df2 = data_append(at, df2)
            # print(df2)
            df2.to_csv(str(run_directory) + '\주요재무_' +
                      os.path.splitext(os.path.basename(filename))[0] +
                      '.csv', header=False, mode='a', encoding='cp949')
            status_insert('[' +code+ ']' + cname + ' 주요재무 조회가 완료되었습니다.')
            df2.drop(df2.index, inplace=True)
        if CheckVariety_3.get() == 1:
            statement_3y(code)
            df3 = data_append(bt, df3)
            # print(df3)
            df3.to_csv(str(run_directory) + '\요약재무_' +
                      os.path.splitext(os.path.basename(filename))[0] +
                      '.csv', header=False, mode='a', encoding='cp949')
            status_insert('[' +code+ ']' + cname + ' 요약재무 조회가 완료되었습니다.')
            df3.drop(df3.index, inplace=True)

        cname = ""
        count += 1
        temp_file_save(code_o)
        progress_update(total_temp, start_time)

        # 브라우저 누적 조회 카운트
        i += 1

    status_insert('<'
                  ''
                  ''
                  '>')
    status_insert('모든 조회 및 저장이 완료되었습니다.')
    driver.quit()
    button_start.config(state=DISABLED)
    btn_text.set("시작")
    run_status[0] = 0
    return

# 쓰레드 생성
def th_scrap():
    threading.Thread(target = scrap).start()

def th_scrap_join():
    threading.Thread(target = scrap).join()

def th_scrap_alive():
    threading.Thread(target = scrap).is_alive()

# 메인창 설정
window = Tk()
window.title('Cretop Data Scraper (beta)')

window_width = 712
window_height = 315
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x_cordinate = int((screen_width / 2) - (window_width / 2))
y_cordinate = int((screen_height / 2) - (window_height / 2))
window.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
window.resizable(False, False)
window.config(background="white")

# 서브창 설정
scrollbar = Scrollbar(window)
status_tracker = Listbox(window, width='47', yscrollcommand=scrollbar.set, bg='light gray')

# 창 내부 오브젝트 설정
label_file_explorer = Label(window, text="사업자번호 파일을 선택해주세요.", width=50, height=2, fg="blue")

## 프로그레시브 바 설정
style = ttk.Style(window)
style.layout('text.Horizontal.TProgressbar',
             [('Horizontal.Progressbar.trough',
               {'children': [('Horizontal.Progressbar.pbar',
                              {'side': 'left', 'sticky': 'ns'})],
                'sticky': 'nswe'}),
              ('Horizontal.Progressbar.label', {'sticky': ''})])
style.configure('text.Horizontal.TProgressbar', text='0 / 0 (0.0%)')
variable = tk.DoubleVar(window)
pbar = ttk.Progressbar(window, style = 'text.Horizontal.TProgressbar', variable=variable, mode='determinate')

## 파일 검색 버튼 설정
button_explore = Button(window, text="Import", command=browsefiles)

## 시작 버튼 설정
btn_text = tk.StringVar()
button_start = Button(window, width=20, textvariable=btn_text, command=doit)
btn_text.set("시작")

## 상태 지우기 버튼 설정
button_status = Button(window, width=20, text="상태 지우기", command=clear)
button_status.config(state=DISABLED)

## 종료 버튼 설정
button_exit = Button(window, width=10, text="종료", command=window_on_close)

## 체크 박스 설정
CheckVariety_1 = tk.IntVar()
CheckVariety_2 = tk.IntVar()
CheckVariety_3 = tk.IntVar()

checkbutton1 = tk.Checkbutton(window, text="사업자 정보", width=35,
                              variable=CheckVariety_1, anchor='w', bg='white')
checkbutton2 = tk.Checkbutton(window, text="주요 재무요약(최근 5년)", width=47,
                              variable=CheckVariety_2, anchor='w', bg='white')
checkbutton3 = tk.Checkbutton(window, text="요약 재무제표(최근 3년)", width=47,
                              variable=CheckVariety_3, anchor='w', bg='white')
checkbutton1.select()
checkbutton2.select()
checkbutton3.select()

## 설명 문구 설정
label1 = Label(window, text=' ', bg='white')
label2 = Label(window, text='     (주요 재무요약은 자산/부채/자본총계, 매출/영업이익/순이익)',
               bg='white', anchor='w')
label3 = Label(window, text='     (요약 재무제표는 유동, 비유동, 영업외손익 등 포함)',
               bg='white', anchor='w')
label4 = Label(window, text='    ※ 시스템에 따라 시간당 200~500개 기업 조회가 가능하며,',
               bg='white', anchor='w')
label5 = Label(window, text='      체크 개수에 따른 크롤링 효율은 미미함',
               bg='white', anchor='w')
label6 = Label(window, text='  ',
               bg='white', anchor='w')
signature = Label(window, text='by sj.lee',
                  bg='white', anchor='e')

# 오브젝트 배치
label_file_explorer.grid(row=0, columnspan=5, sticky='w' + 'e' + 's' + 'n')
status_tracker.grid(row = 0, rowspan = 13, column = 5, sticky='w' + 'e' + 's' + 'n')
scrollbar.grid(row = 0,rowspan=13, column=6, sticky='e'+'s'+'n')
pbar.grid(row=1, columnspan=5, sticky='w' + 'e' + 's' + 'n')
checkbutton1.grid(row=2, columnspan=4)
button_explore.grid(row=2, column=4, sticky="e")
checkbutton2.grid(row=3, columnspan=5)
label2.grid(row=4, columnspan=5, sticky='w')
checkbutton3.grid(row=5, columnspan=5)
label3.grid(row=6, columnspan=5, sticky='w')
label1.grid(row=7, columnspan=5)
label4.grid(row=8, columnspan=5, sticky='w')
label5.grid(row=9, columnspan=5, sticky='w')
label6.grid(row=10, columnspan=5, sticky='w')
button_start.grid(row=11, columnspan=2, sticky='w')
signature.grid(row=11, column=4, sticky='e')
button_status.grid(row=12, columnspan=2, sticky="w")
button_exit.grid(row=12, column=4, sticky="e")

# 프로그램 종료 이벤트
window.protocol("WM_DELETE_WINDOW", window_on_close)

# 프로그램 상단
window.lift()

# 파일명 기본 설정
filename = ""
# 시작/실행 상태 체커
run_status = [0]

max_number = 0
current_value = 0
p_percentage = float(0)

search_status = [0]

skip_click = 0

df = pd.DataFrame(columns=['입력번호', '기업명', '사업자번호', '종업원수', '전화번호', '법인(주민)번호', '당좌거래은행', '대표자명', '우편번호', '주소',
                           '업종코드', '업종', '기업인증현황', '설립일자', '기업형태', '산업재산권현황',
                           '휴폐업정보', '일자', '법인등기정보', '일자', '기업채무불이행상태', '일자', '행정처분정보', '일자',
                           '평가등급(최근)', '평가일자'])

df2 = pd.DataFrame(columns=['사업자번호', '조회 상태',
                            '기준연도(Y-5)', '기준연도(Y-4)', '기준연도(Y-3)', '기준연도(Y-2)', '기준연도(Y-1)',
                            '자산총계(Y-5)', '자산총계(Y-4)', '자산총계(Y-3)', '자산총계(Y-2)', '자산총계(Y-1)',
                            '부채총계(Y-5)', '부채총계(Y-4)', '부채총계(Y-3)', '부채총계(Y-2)', '부채총계(Y-1)',
                            '자본총계(Y-5)', '자본총계(Y-4)', '자본총계(Y-3)', '자본총계(Y-2)', '자본총계(Y-1)',
                            '매출액(Y-5)', '매출액(Y-4)', '매출액(Y-3)', '매출액(Y-2)', '매출액(Y-1)',
                            '영업이익(Y-5)', '영업이익(Y-4)', '영업이익(Y-3)', '영업이익(Y-2)', '영업이익(Y-1)',
                            '당기순이익(Y-5)', '당기순이익(Y-4)', '당기순이익(Y-3)', '당기순이익(Y-2)', '당기순이익(Y-1)'])

df3 = pd.DataFrame(columns=['사업자번호', '조회 상태',
                            '기준연도(Y-3)', '기준연도(Y-2)', '기준연도(Y-1)',
                            '유동자산(Y-3)', '유동자산(Y-2)', '유동자산(Y-1)',
                            '비유동자산(Y-3)', '비유동자산(Y-2)', '비유동자산(Y-1)',
                            '자산총계(Y-3)', '자산총계(Y-2)', '자산총계(Y-1)',
                            '유동부채(Y-3)', '유동부채(Y-2)', '유동부채(Y-1)',
                            '비유동부채(Y-3)', '비유동부채(Y-2)', '비유동부채(Y-1)',
                            '부채총계(Y-3)', '부채총계(Y-2)', '부채총계(Y-1)',
                            '자본금(Y-3)', '자본금(Y-2)', '자본금(Y-1)',
                            '자본총계(Y-3)', '자본총계(Y-2)', '자본총계(Y-1)',
                            '매출액(Y-3)', '매출액(Y-2)', '매출액(Y-1)',
                            '매출총이익(Y-3)', '매출총이익(Y-2)', '매출총이익(Y-1)',
                            '영업이익(Y-3)', '영업이익(Y-2)', '영업이익(Y-1)',
                            '영업외수익(Y-3)', '영업외수익(Y-2)', '영업외수익(Y-1)',
                            '영업외비용(Y-3)', '영업외비용(Y-2)', '영업외비용(Y-1)',
                            '법인세비용차감전순손익(Y-3)', '법인세비용차감전순손익(Y-2)', '법인세비용차감전순손익(Y-1)',
                            '법인세비용(Y-3)', '법인세비용(Y-2)', '법인세비용(Y-1)',
                            '당기순이익(Y-3)', '당기순이익(Y-2)', '당기순이익(Y-1)'])

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

run_directory = os.getcwd()

status_insert(str(run_directory) + '에 저장됩니다.')
#

d = ["N/A" for j in range(23)]
at = ["N/A" for k in range(37)]
bt = ["N/A" for k in range(53)]

status_insert("파일을 선택해주세요.")

window.mainloop()
