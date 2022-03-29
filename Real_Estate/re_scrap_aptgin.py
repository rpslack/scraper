#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.utils import ChromeType
from bs4 import BeautifulSoup
import os
import time
import pandas as pd


# In[2]:


def set_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


# In[3]:


def page_scrap():
    elet = driver.page_source
    soup = BeautifulSoup(elet, 'html.parser')
    return soup


# In[12]:


options = webdriver.ChromeOptions()

# options.add_experimental_option("prefs", {
#         "download.default_directory": path,
#         "download.prompt_for_download": False,
#         "download.directory_upgrade": True,
#         "safebrowsing_for_trusted_sources_enabled": False,
#         "safebrowsing.enabled": False
#         })

# options.add_argument('headless')
options.add_argument('window-size=1920,1080')
options.add_argument("disable-gpu")
# 혹은 options.add_argument("--disable-gpu")

options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")
options.add_argument("lang=ko_KR") # 한국어!

driver = set_chrome_driver()
# webdriver.Chrome(executable_path=r'C:\Users\1907043\Documents\py\chromedriver.exe', chrome_options=options)

driver.set_window_size(1920, 1080)

driver.get('about:blank')
driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5];},});")

driver.get('https://aptgin.com/homeLogin')
driver.implicitly_wait(3)

driver.find_element(By.ID,'user_id1').send_keys('slack')
driver.find_element(By.ID,'password1').send_keys('lsj852456')

login_button = driver.find_element(By.CLASS_NAME,'login-btn')

WebDriverWait(driver, 20).until(EC.element_to_be_clickable(login_button)).click()

time.sleep(1)

try:
    driver.switch_to.alert.accept() # 중복 로그인 얼럿 닫기
except:
    pass

# Month_Button = (By.XPATH, '/html/body/div[1]/div[1]/div/div/div/div[2]/div[1]/ul/li[2]/a')

# button class="btn btn-primary logbtn
# driver.find_element_by_id('password1').send_keys('lsj852456')
driver.implicitly_wait(3)


# In[13]:


def Hovering_Scrap1(): #시/도 기준의 툴팁 스크래핑 합수
    res = {}
    graph = driver.find_elements(By.XPATH, "//*[name()='svg']//*[name()='g' and @class='highcharts-series-group']") #그래프 element 지정
    dates = driver.find_elements(By.XPATH, "//*[name()='svg']//*[name()='g' and @class='highcharts-axis-labels highcharts-xaxis-labels']") #그래프 년도축 element 지정
    date = dates[0].text #그래프 하단 년도 데이터 저장
    date_list = list(map(str, date.split('\n'))) #그래프 하단 년도 데이터 리스트 변환
    for d in date_list:
        res[d] = ["","전체","",""] #연도별 딕셔너리 양식 추가(시/도는 구군이 없으므로 전체로 처리)
    move_ins = driver.find_elements(By.XPATH, "//*[name()='svg']//*[name()='g' and @class='highcharts-series highcharts-series-0 highcharts-column-series highcharts-color-0  highcharts-tracker']/*[name()='rect']") #그래프 연도 영역별 element 지정
    location = driver.find_elements(By.XPATH, '//*[@id="regionTxt"]') #지역명 조회
    
    actions = ActionChains(driver).move_to_element(graph[0])
    actions.perform() #그래프로 마우스 아동
    actions = ActionChains(driver).move_to_element(graph[0])
    actions.perform() #그래프로 마우스 아동 (최초 이동시 오류 있어 2번 이동)
    # graph[0].location_once_scrolled_into_view
    time.sleep(0.3) #이동 후 대기 시간

    for idx, el in enumerate(move_ins[0:26]):
        # hover = ActionChains(driver).move_to_element(el)
        hover = ActionChains(driver).move_to_element_with_offset(el, 0, -1)
        hover.perform() #연도별 영역 마우스 오버
        time.sleep(0.05) #툴팁 로딩시간 대비 대기시간
        demands = driver.find_elements(By.XPATH, "//*[name()='svg']//*[contains(@class, 'highcharts-tooltip')]//*[name()='tspan']") #툴팁 내 항목 element 지정
        try:
            date = driver.find_elements(By.CSS_SELECTOR, ".highcharts-tooltip > text:nth-child(5) > tspan:nth-child(1)")[0].text #일자 데이터 수집
            move_in = driver.find_elements(By.CSS_SELECTOR, ".highcharts-tooltip > text:nth-child(5) > tspan:nth-child(4)")[0].text #입주량 데이터 수집
            res[date][0] = location[0].text #지역명 저장
            res[date][2] = move_in #입주량 저장
            if len(demands) == 7: #툴팁에 수요량 있는 경우에 대한 처리
                demand = driver.find_elements(By.CSS_SELECTOR, ".highcharts-tooltip > text:nth-child(5) > tspan:nth-child(7)")[0].text #수요량 데이터 수집
                res[date][3] = demand #수요량 저장
        
        except Exception as e:    # 모든 예외의 에러 메시지를 출력할 때는 Exception을 사용
            print('error', date, location[0].text, move_in) #에러 발생시 출력
            pass

        time.sleep(0.1) #그래프 이동 대기시간

    return res #저장 Dictionary결과 반환


# In[14]:


def Hovering_Scrap2(): #시/도 기준의 툴팁 스크래핑 합수
    res = {}
    graph = driver.find_elements(By.XPATH, "//*[name()='svg']//*[name()='g' and @class='highcharts-series-group']") #그래프 element 지정
    dates = driver.find_elements(By.XPATH, "//*[name()='svg']//*[name()='g' and @class='highcharts-axis-labels highcharts-xaxis-labels']") #그래프 년도축 element 지정
    date = dates[0].text #그래프 하단 년도 데이터 저장
    date_list = list(map(str, date.split('\n'))) #그래프 하단 년도 데이터 리스트 변환
    for d in date_list:
        res[d] = ["","","",""] #연도별 딕셔너리 양식 추가
    move_ins = driver.find_elements(By.XPATH, "//*[name()='svg']//*[name()='g' and @class='highcharts-grid highcharts-xaxis-grid']//*[name()='path']") #전체 그래프 리스트화
    location = driver.find_elements(By.XPATH, '//*[@id="regionTxt"]') #지역명 조회
    loc_text = location[0].text #지역명 text 조회
    tmp = loc_text.split() #시도, 구군으로 텍스트 분리
    if tmp == 2:
        sido, gugun = tmp[0], tmp[1]
    else:
        sido, gugun = tmp[0], ' '.join(tmp[1:])

    actions = ActionChains(driver).move_to_element(graph[0])
    actions.perform() #그래프로 마우스 아동
    actions = ActionChains(driver).move_to_element(graph[0])
    actions.perform() #그래프로 마우스 아동 (최초 이동시 오류 있어 2번 이동)
    time.sleep(0.3) #이동 후 대기 시간
    
    for idx, el in enumerate(move_ins[0:26]):
        hover = ActionChains(driver).move_to_element(el)
        hover.perform() #연도별 영역 마우스 오버
        time.sleep(0.05) #툴팁 로딩시간 대비 대기시간
        demands = driver.find_elements(By.XPATH, "//*[name()='svg']//*[contains(@class, 'highcharts-tooltip')]//*[name()='tspan']") #툴팁 내 항목 element 지정
        try:
            date = driver.find_elements(By.CSS_SELECTOR, ".highcharts-tooltip > text:nth-child(5) > tspan:nth-child(1)")[0].text #일자 데이터 수집
            move_in = driver.find_elements(By.CSS_SELECTOR, ".highcharts-tooltip > text:nth-child(5) > tspan:nth-child(4)")[0].text #입주량 데이터 수집
            res[date][0] = sido #시도명 저장
            res[date][1] = gugun #구군명 저장
            res[date][2] = move_in #입주량 저장
            if len(demands) == 7: #툴팁에 수요량 있는 경우에 대한 처리
                demand = driver.find_elements(By.CSS_SELECTOR, ".highcharts-tooltip > text:nth-child(5) > tspan:nth-child(7)")[0].text #수요량 데이터 수집
                res[date][3] = demand #수요량 저장
        except:
            print('error', date, sido, gugun, move_in) #에러 발생시 출력
            pass

        time.sleep(0.1) #그래프 이동 대기시간

    return res #저장 Dictionary결과 반환


# In[15]:


def Data_save(res, df): #데이터프레임 Row 추가 함수
    for k, v in res.items():
        df = df.append({'년':k, '시도':v[0], '구군':v[1], '입주량':v[2], '수요량':v[3]}, ignore_index=True) #수집 정보에 대해 Dictionary Row별로 추가
    return df


# In[16]:


def Select_loc(): #지역 선택을 위한 드롭다운 열기 함수
    select1 = (By.XPATH, '//*[@id="headerFilter"]/div/div[1]/a/span[4]') #드롭다운 화살표 지정
    driver.find_element(*select1).click() #드롭다운 열기
    time.sleep(0.3) #로딩 대기
    soup = page_scrap() #페이지 소스 수집


# In[17]:


df1 = pd.DataFrame(columns = ['년', '시도', '구군', '입주량', '수요량']) #기초 데이터프레임 생성


# In[18]:


start = time.time()
driver.get('https://aptgin.com/home/gin05/gin0501') #입주/수요 웹페이지 열기
driver.implicitly_wait(3) #웹페이지 로딩 능동 대기
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "highcharts-root"))) #그래프 로딩 대기

for i in range(1, 19): #시/도단위 반복문
    Select_loc() #지역 선택 드롭다운 열기 함수
    sido = (By.XPATH, f'//*[@id="headerFilter"]/div/div[1]/fieldset/div/ul[1]/li[{i}]/button') #시/도 선택
    driver.find_element(*sido).click() # 시/도 클릭
    search = (By.XPATH, f'//*[@id="headerFilter"]/div/div[4]/button[2]') #검색버튼 선택
    driver.find_element(*search).click() #구/군 클릭
    driver.implicitly_wait(3) #웹페이지 로딩 능동대기
    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "highcharts-root"))) #그래프 로딩 대기
    time.sleep(1) #강제 대기 시간
    res = Hovering_Scrap1() #시/도 데이터 수집 함수 실행하여 Dictionary 저장
    df1 = Data_save(res, df1) #데이터프레임에 수집 결과 추가
    
    soup = page_scrap() #페이지 소스 수집
    t = soup.find('ul', {'class' : 'depth-2'}) #구/군 영역 찾기
    l = t.findAll('li') #구/군 영역 내 구/군 리스트화
    time.sleep(0.3) #강제 대기 시간
    
    if len(l) <= 1: #구/군이 없는 경우 예외 처리 (구군 한개만 있는 세종시도 예외처리)
        pass
    else: #구/군이 있는 경우 구/군 조회
        for j in range(1, len(l)+1):
            Select_loc() #지역 선택 드롭다운 열기 함수
            sido = (By.XPATH, f'//*[@id="headerFilter"]/div/div[1]/fieldset/div/ul[1]/li[{i}]/button') #시/도 선택
            driver.find_element(*sido).click()
            time.sleep(0.5)
            gugun = (By.XPATH, f'//*[@id="headerFilter"]/div/div[1]/fieldset/div/ul[2]/li[{j}]/button') #구/군 선택
            driver.find_element(*gugun).click()
            search = (By.XPATH, f'//*[@id="headerFilter"]/div/div[4]/button[2]') #검색버튼 선택
            driver.find_element(*search).click()
            driver.implicitly_wait(3)
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "highcharts-root")))
            time.sleep(1) #강제 대기 시간
            res = Hovering_Scrap2() #구/군 데이터 수집 함수 실행하여 Dictionary 저장 
            df1 = Data_save(res, df1) #데이터프레임에 수집 결과 추가
    print(df1)
end = time.time()
print(f"{end - start:.5f} sec")


# In[233]:


df1


# In[238]:


df1.to_csv(r'C:\Users\1907043\Documents\df1.csv', encoding='utf-8')


# In[50]:





# ## 준공

# In[211]:


def Completion1(df2): #시/도 단위 스크래핑 함수
    location = driver.find_elements(By.XPATH, '//*[@id="regionTxt"]') #지역명 영역 조회
    loc_text = location[0].text #지역명 저장
    
    table = driver.find_elements(By.XPATH, '//*[@id="grid"]/div[2]/table/tbody') #저장 테이블 조회
    atext = table[0].get_attribute("innerText") #텍스트 추출
    trans_text = list(map(str, atext.split('\n'))) #월단위 분리

    for t in trans_text:
        i = t.split('\t') #항목별 분리 리스트 저장
        df2 = df2.append({'년월':i[0], '시도':i[1], '구군':'전체', '전체': i[2], '준공전':i[3], '준공전(%)':i[4], '준공후':i[5], '준공후(%)':i[6]}, ignore_index=True) #항목 저장
    return df2 #데이터 반환


# In[212]:


def Completion2(df2): #구/군 단위 스크래핑 함수
    location = driver.find_elements(By.XPATH, '//*[@id="regionTxt"]') #지역명 조회
    loc_text = location[0].text #지역명 저장
    sido, gugun = loc_text.split() #시/도, 구/군 분리
    
    table = driver.find_elements(By.XPATH, '//*[@id="grid"]/div[2]/table/tbody') #저장 테이블 조회
    atext = table[0].get_attribute("innerText") #텍스트 추출
    trans_text = list(map(str, atext.split('\n'))) #월단위 분리

    for t in trans_text:
        i = t.split('\t') #항목별 분리 리스트 저장
        df2 = df2.append({'년월':i[0], '시도':sido, '구군':gugun, '전체': i[2], '준공전':i[3], '준공전(%)':i[4], '준공후':i[5], '준공후(%)':i[6]}, ignore_index=True) #항목 저장
    return df2 #데이터 반환


# In[216]:


df2 = pd.DataFrame(columns = ['년월', '시도', '구군', '전체', '준공전', '준공전(%)', '준공후', '준공후(%)']) #데이터프레임 양식 설정


# In[218]:


driver.get('https://aptgin.com/home/gin04/gin0403') #입주/수요 웹페이지 열기
driver.implicitly_wait(3)
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "highcharts-root"))) #그래프 로딩 대기

for i in range(1, 19):
    Select_loc()
    sido = (By.XPATH, f'//*[@id="headerFilter"]/div/div[1]/fieldset/div/ul[1]/li[{i}]/button')
    driver.find_element(*sido).click()
    search = (By.XPATH, f'//*[@id="headerFilter"]/div/div[3]/button[2]')
    driver.find_element(*search).click()
    driver.implicitly_wait(3)
    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "highcharts-root"))) #그래프 로딩 대기
    time.sleep(1)
    df2 = Completion1(df2)
    soup = page_scrap()
    t = soup.find('ul', {'class' : 'depth-2'})
    l = t.findAll('li')
    time.sleep(0.3)
    
    if len(l) == 0:
        pass
    else:
        for j in range(1, len(l)+1):
            Select_loc()
            sido = (By.XPATH, f'//*[@id="headerFilter"]/div/div[1]/fieldset/div/ul[1]/li[{i}]/button')
            driver.find_element(*sido).click()
            time.sleep(0.5)
            gugun = (By.XPATH, f'//*[@id="headerFilter"]/div/div[1]/fieldset/div/ul[2]/li[{j}]/button')
            driver.find_element(*gugun).click()
            search = (By.XPATH, f'//*[@id="headerFilter"]/div/div[3]/button[2]')
            driver.find_element(*search).click()
            driver.implicitly_wait(3)
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "highcharts-root")))
            time.sleep(1)
            df2 = Completion2(df2)
    print(df2)


# In[237]:


df2.to_csv(r'C:\Users\1907043\Documents\df2.csv', encoding='utf-8')


# ## 시도구군 가져오기

# In[217]:


driver.get('https://aptgin.com/home/gin05/gin0501')
select1 = (By.XPATH, '//*[@id="headerFilter"]/div/div[1]/a/span[4]')
driver.find_element(*select1).click()
soup = page_scrap()

for i in range(2, 19):
    sido = (By.XPATH, f'//*[@id="headerFilter"]/div/div[1]/fieldset/div/ul[1]/li[{i}]/button')
    driver.find_element(*sido).click()
    soup = page_scrap()
    t = soup.find('ul', {'class' : 'depth-2'})
    l = t.findAll('li')
    time.sleep(0.3)
    for j in range(1, len(l)+1):
        gugun = (By.XPATH, f'//*[@id="headerFilter"]/div/div[1]/fieldset/div/ul[2]/li[{j}]/button')
        driver.find_element(*gugun).click()
        print(driver.find_element(*sido).text, driver.find_element(*gugun).text)
        
        search = (By.XPATH, f'//*[@id="headerFilter"]/div/div[4]/button[2]')
        driver.find_element(*search).click()
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "highcharts-root")))
        res = Hovering_Scrap()
        


# In[ ]:





# #### 호버링 스크래핑(미사용)

# In[ ]:


for el in move_ins:
    x = el.location['x']
    y = el.location['y']
    print(x, y)


# In[ ]:


def Hovering_Scrap1(): #시/도 기준의 툴팁 스크래핑 합수
    res = {}
    graph = driver.find_elements(By.XPATH, "//*[name()='svg']//*[name()='g' and @class='highcharts-series-group']")
    dates = driver.find_elements(By.XPATH, "//*[name()='svg']//*[name()='g' and @class='highcharts-axis-labels highcharts-xaxis-labels']")
    date = dates[0].text
    date_list = list(map(str, date.split('\n')))
    for d in date_list:
        res[d] = ["","전체","",""]
    move_ins = driver.find_elements(By.XPATH, "//*[name()='svg']//*[name()='g' and @class='highcharts-series highcharts-series-0 highcharts-column-series highcharts-color-0  highcharts-tracker']/*[name()='rect']") #전체 그래프 리스트화
    location = driver.find_elements(By.XPATH, '//*[@id="regionTxt"]') #지역명 조회
    time.sleep(0.3)
    
    actions = ActionChains(driver).move_to_element(graph[0])
    actions.perform()
    actions = ActionChains(driver).move_to_element(graph[0])
    actions.perform()
    time.sleep(0.3)
    
    for idx, el in enumerate(move_ins):
        hover = ActionChains(driver).move_to_element(el) #그래프 마우스 오버
        hover.perform()
        time.sleep(0.1)
        demands = driver.find_elements(By.XPATH, "//*[name()='svg']//*[contains(@class, 'highcharts-tooltip')]//*[name()='tspan']")
        try:
            date = driver.find_elements(By.CSS_SELECTOR, ".highcharts-tooltip > text:nth-child(5) > tspan:nth-child(1)")[0].text #일자 데이터 수집
            move_in = driver.find_elements(By.CSS_SELECTOR, ".highcharts-tooltip > text:nth-child(5) > tspan:nth-child(4)")[0].text #입주량 데이터 수집
            res[date][0] = location[0].text
            res[date][2] = move_in
            if len(demands) == 7:
                demand = driver.find_elements(By.CSS_SELECTOR, ".highcharts-tooltip > text:nth-child(5) > tspan:nth-child(7)")[0].text
                res[date][3] = demand
        
        except:
            print('error', date, sido, gugun, move_in)
            pass
        time.sleep(0.1)
    
    # el = move_ins[0]
    # idx = 0
    #  #그래프 마우스 오버
    # hover.perform()
    # time.sleep(0.1)
    # demands = driver.find_elements(By.XPATH, "//*[name()='svg']//*[contains(@class, 'highcharts-tooltip')]//*[name()='tspan']")
    # date = driver.find_elements(By.CSS_SELECTOR, ".highcharts-tooltip > text:nth-child(5) > tspan:nth-child(1)")[0].text #일자 데이터 수집
    # move_in = driver.find_elements(By.CSS_SELECTOR, ".highcharts-tooltip > text:nth-child(5) > tspan:nth-child(4)")[0].text #입주량 데이터 수집
    # res[date][0] = location[0].text
    # res[date][2] = move_in
    # if len(demands) == 7:
    #     demand = driver.find_elements(By.CSS_SELECTOR, ".highcharts-tooltip > text:nth-child(5) > tspan:nth-child(7)")[0].text
    #     res[date][3] = demand

    return res


# In[ ]:


driver.get('https://aptgin.com/home/gin04/gin0403')
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "highcharts-root")))
test = driver.find_elements(By.XPATH, "//*[name()='svg']//*[name()='g' and @class='highcharts-series highcharts-series-1 highcharts-column-series  highcharts-tracker']/*[name()='rect']")
res2 = []
for el in test:
    hover = ActionChains(driver).move_to_element(el)
    hover.perform()
    date = driver.find_elements(By.CSS_SELECTOR, ".highcharts-tooltip > g.highcharts-label.highcharts-tooltip-box.highcharts-color-none.highcharts-tooltip-header > text > tspan")
    data1 = driver.find_elements(By.CSS_SELECTOR, ".highcharts-tooltip > g:nth-child(2) > text > tspan:nth-child(3)")
    data2 = driver.find_elements(By.CSS_SELECTOR, ".highcharts-tooltip > g:nth-child(3) > text > tspan:nth-child(3)")
    res2.append((date[0].text, data1[0].text, data2[0].text))


# In[ ]:


# def Completion1(df2):
#     # soup = page_scrap()
#     location = driver.find_elements(By.XPATH, '//*[@id="regionTxt"]') #지역명 조회
#     loc_text = location[0].text
    
#     # t = soup.findAll("tbody", {"role": "rowgroup"})
#     trs = driver.find_elements(By.XPATH, '//*[@id="grid"]/div[2]/table/tbody/*[name()="tr"]')

#     for tr in trs:
#         tds = tr.find_elements(By.XPATH, './/*[name()="td"]')
#         i = []
#         for td in tds:
#             i.append(td.text)
#         df2 = df2.append({'년월':i[0], '시도':i[1], '구군':'전체', '전체': i[2], '준공전':i[3], '준공전(%)':i[4], '준공후':i[5], '준공후(%)':i[6]}, ignore_index=True)
#     return df2

# def Completion2(df2):
#     # soup = page_scrap()
#     location = driver.find_elements(By.XPATH, '//*[@id="regionTxt"]') #지역명 조회
#     loc_text = location[0].text
#     sido, gugun = loc_text.split()
    
#     # t = soup.findAll("tbody", {"role": "rowgroup"})
#     trs = driver.find_elements(By.XPATH, '//*[@id="grid"]/div[2]/table/tbody/*[name()="tr"]')

#     for tr in trs:
#         tds = tr.find_elements(By.XPATH, './/*[name()="td"]')
#         i = []
#         for td in tds:
#             i.append(td.text)
#         df2 = df2.append({'년월':i[0], '시도':sido, '구군':gugun, '전체': i[2], '준공전':i[3], '준공전(%)':i[4], '준공후':i[5], '준공후(%)':i[6]}, ignore_index=True)
#     return df2

# def Completion2(df2):
#     soup = page_scrap()
#     location = driver.find_elements(By.XPATH, '//*[@id="regionTxt"]') #지역명 조회
#     loc_text = location[0].text
#     sido, gugun = loc_text.split()
    
#     t = soup.findAll("tbody", {"role": "rowgroup"})
#     table = driver.find_elements(By.XPATH, '//*[@id="grid"]/div[2]/table/tbody')
#     trs = driver.find_elements(By.XPATH, '//*[@id="grid"]/div[2]/table/tbody//*[name()="tr"]')
#     # trs = tb.findChildren('tr')

#     atext = table[0].text
#     trans_text = list(map(str, atext.split('\n')))

#     for t in trs:
#         t = t.text
#         i = list(map(str, t.split()))
#         print(i)
#         df2 = df2.append({'년월':i[0], '시도':i[1], '구군':i[2], '전체': i[3], '준공전':i[4], '준공전(%)':i[5], '준공후':i[6], '준공후(%)':i[7]}, ignore_index=True)
#     return df2


# In[ ]:




