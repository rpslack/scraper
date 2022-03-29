#!/usr/bin/env python
# coding: utf-8

# In[462]:


from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
from bs4 import BeautifulSoup
import os
import time
import pandas as pd


# In[463]:


def set_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


# In[464]:


def page_scrap():
    elet = driver.page_source
    soup = BeautifulSoup(elet, 'html.parser')
    return soup


# In[465]:


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



# In[466]:


def Select_loaction():
    select = Select(driver.find_element(By.ID,'selRegion'))

    # select by visible text
    select.select_by_visible_text('시도별')

    select = Select(driver.find_element(By.ID,'selSido'))
    select.select_by_visible_text('서울')
    # # select by value 
    # select.select_by_value('1')


# In[467]:


def Select_factor():
    select1 = (By.XPATH, '//*[@id="HOUSE_20000"]/a')
    driver.find_element(*select1).click()
    time.sleep(0.2)
    select2 = (By.XPATH, '//*[@id="HOUSE_21000"]/a')
    driver.find_element(*select2).click()
    time.sleep(0.2)
    select3 = (By.XPATH, '//*[@id="HOUSE_21200"]/a')
    driver.find_element(*select3).click()
    time.sleep(0.2)
    select4 = (By.XPATH, '//*[@id="HOUSE_21210"]/a')
    driver.find_element(*select4).click()
    time.sleep(0.2)
    select5 = (By.XPATH, '//*[@id="HOUSE_21211"]/a')
    try:
        driver.find_element(*select5).click()
        time.sleep(0.2)
    except:
        driver.switch_to.alert.accept()
    select1 = (By.XPATH, '//*[@id="LHT_60000"]/a')
    driver.find_element(*select1).click()
    time.sleep(0.2)
    select2 = (By.XPATH, '//*[@id="LHT_65000"]/a')
    driver.find_element(*select2).click()
    time.sleep(0.2)
    select3 = (By.XPATH, '//*[@id="LHT_65030"]/a')
    try:
        driver.find_element(*select3).click()
        time.sleep(0.2)
    except:
        driver.switch_to.alert.accept()
    time.sleep(0.5)


# In[468]:


def Select_factor2():
    if Not_alert(driver):
        select5 = (By.XPATH, '//*[@id="HOUSE_21211"]/a')
        driver.find_element(*select5).click()
        time.sleep(0.2)
        if Not_alert(driver):
            select3 = (By.XPATH, '//*[@id="LHT_65030"]/a')
            driver.find_element(*select3).click()
        else:
            driver.switch_to.alert.accept()
            select3 = (By.XPATH, '//*[@id="LHT_65030"]/a')
            driver.find_element(*select3).click()
            time.sleep(0.2)
            if Not_alert(driver):
                select5 = (By.XPATH, '//*[@id="HOUSE_21211"]/a')
                driver.find_element(*select5).click()
    else:
        driver.switch_to.alert.accept()
        select5 = (By.XPATH, '//*[@id="HOUSE_21211"]/a')
        driver.find_element(*select5).click()
        time.sleep(0.2)
        if Not_alert(driver):
            select3 = (By.XPATH, '//*[@id="LHT_65030"]/a')
            driver.find_element(*select3).click()
        else:
            driver.switch_to.alert.accept()
            select3 = (By.XPATH, '//*[@id="LHT_65030"]/a')
            driver.find_element(*select3).click()
            time.sleep(0.2)
            if Not_alert(driver):
                select5 = (By.XPATH, '//*[@id="HOUSE_21211"]/a')
                driver.find_element(*select5).click()
    time.sleep(0.5)


# In[469]:


# def Scrap_columns():
#     soup = page_scrap()
#     data = soup.find("div", {"id": "dataGridArea"})
#     data = data.findAll("div", {"class": "tabulator-col"})
#     columns = []
#     for i in data[1:]:
#         a = i.find("div", {"class": "tabulator-col-title"}).text
#         columns.append(a)
#     return columns


# In[470]:


def Scrap_data(r1, r2):
    soup = page_scrap()
    
    columns = []
    depth1 = soup.find("div", {"id": "dataGridArea"})
    depth2 = depth1.find("div", {"class": "tabulator-headers"})
    depth3 = depth2.findAll("div", {"class": "tabulator-col"})    
    for i in depth3:
        columns.append(i.text)
    
    trade_price_index = []
    trade = []
    depth1 = soup.find("div", {"id": "dataGridArea"})
    depth2 = depth1.findAll("div", {"class": "tabulator-row"})
    depth3 = depth2[0].findAll("div", {"class": "tabulator-cell"})
    for i in depth3:
        trade_price_index.append(i.text)
    if len(depth2) > 1:
        depth3 = depth2[1].findAll("div", {"class": "tabulator-cell"})    
        for i in depth3:
            trade.append(i.text)
    else:
        pass
    
    df1 = pd.DataFrame([trade_price_index], columns = columns)
    if trade != []:
        df2 = pd.DataFrame([trade], columns = columns)
        df = pd.concat([df1, df2])
    else:
        df = df1
    df.rename(columns = {'삭제' : '지역1'}, inplace = True)
    df.rename(columns = {'지역' : '지역2'}, inplace = True)
    df['지역1'] = r1
    df['지역2'] = r2
    
    return df


# In[471]:


# def Dataframe_save(df, t):
#     df = df.append({'지역':t[1], '통계명':t[2], '단위':t[3], "'21.03":t[4], "'21.04":t[5], "'21.05":t[6],"'21.06":t[7],
#                      "'21.07":t[8], "'21.08":t[9], "'21.09":t[10], "'21.10":t[11], "'21.11":t[12], "'21.12":t[13], "'22.01":t[14]}, ignore_index=True)
#     return df


# In[472]:


def Not_alert(driver):
    try:
        alert = driver.switch_to.alert
        alert.text
        return False
    except:
        return True


# In[473]:


def All_region(tdf):    
    location1 = driver.find_element(By.XPATH, '//*[@id="selRegion"]/option[1]')
    location1.click()
    time.sleep(1)
    Select_factor()
    # columns = Scrap_columns()
    df = Scrap_data('전국', '전체')
    tdf = pd.concat([tdf, df])
    return tdf


# In[474]:


def Region_1(tdf):
    location1 = driver.find_element(By.XPATH, '//*[@id="selRegion"]/option[2]')
    location1.click()
    location2 = driver.find_elements(By.XPATH, '//*[@id="selSido"]//*[name()="option"]')
    for i in range(1, len(location2)):
        if i == 1:
            location2[i].click()
            time.sleep(1)
            Select_factor()
            region = location2[i].text
            # columns = Scrap_columns()
            df = Scrap_data(region, '전체')
            tdf = pd.concat([tdf, df])
        else:
            location2[i].click()
            search.click()
            region = location2[i].text
            df = Scrap_data(region, '전체')
            tdf = pd.concat([tdf, df])

    return tdf


# In[475]:


def Region_2(tdf):
    location1 = driver.find_element(By.XPATH, '//*[@id="selRegion"]/option[3]')
    location1.click()
    location2 = driver.find_elements(By.XPATH, '//*[@id="selSido"]//*[name()="option"]')
    k = 0
    for i in range(1, len(location2)):
        location2[i].click()
        region1 = location2[i].text
        location3 = driver.find_elements(By.XPATH, '//*[@id="selSgg"]//*[name()="option"]')
        for j in range(1, len(location3)):
            if i == 1 and j == 1:
                location3[j].click()
                time.sleep(0.3)
                region2 = location3[j].text
                Select_factor()
                # columns = Scrap_columns()
                df = Scrap_data(region1, region2)
                tdf = pd.concat([tdf, df])
            elif k == 1:
                time.sleep(1)
                location3[j].click()
                time.sleep(0.3)
                region2 = location3[j].text
                Select_factor2()
                # columns = Scrap_columns()
                if Not_alert(driver):
                    df = Scrap_data(region1, region2)
                    tdf = pd.concat([tdf, df])
                    k = 0
                else:
                    driver.switch_to.alert.accept()
                    k = 1
                    print(region2,'2')
            else:
                location3[j].click()
                region2 = location3[j].text
                search.click()
                time.sleep(0.3)
                if Not_alert(driver):
                    df = Scrap_data(region1, region2)
                    tdf = pd.concat([tdf, df])
                else:
                    driver.switch_to.alert.accept()
                    k = 1
                    print(region2,'1')
    return tdf


# In[476]:


tdf = pd.DataFrame(columns = ['지역1', '지역2', '통계명', '단위', "'21.03", "'21.04", "'21.05", "'21.06", "'21.07", "'21.08", "'21.09",
                              "'21.10", "'21.11", "'21.12", "'22.01", "'22.02"])


# In[477]:


start = time.time()
driver.get('https://www.reb.or.kr/r-one/statistics/statisticsViewerMulti.do#none')
driver.implicitly_wait(3)
soup = page_scrap()
search = driver.find_element(By.XPATH, '//*[@id="lookupBtn"]')

tdf = All_region(tdf)
tdf = Region_1(tdf)
tdf = Region_2(tdf)

end = time.time()

print(f"{end - start:.5f} sec")


# In[460]:


tdf


# In[461]:


tdf.to_csv(r'C:\Users\1907043\Documents\rone.csv', encoding='utf-8')


# In[272]:


len(depth2)


# In[274]:


columns


# In[ ]:




