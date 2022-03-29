#!/usr/bin/env python
# coding: utf-8

# In[8]:


from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
import os
import time


# In[9]:


def set_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options, desired_capabilities=capabilities)
    return driver


# In[10]:


# method to get the downloaded file name
def getDownLoadedFileName(waitTime):
    driver.execute_script("window.open()")
    # switch to new tab
    driver.switch_to.window(driver.window_handles[-1])
    # navigate to chrome downloads
    driver.get('chrome://downloads')
    # define the endTime
    endTime = time.time()+waitTime
    while True:
        try:
            # get downloaded percentage
            downloadPercentage = driver.execute_script(
                "return document.querySelector('downloads-manager').shadowRoot.querySelector('#downloadsList downloads-item').shadowRoot.querySelector('#progress').value")
            # check if downloadPercentage is 100 (otherwise the script will keep waiting)
            if downloadPercentage == 100:
                # return the file name once the download is completed
                return driver.execute_script("return document.querySelector('downloads-manager').shadowRoot.querySelector('#downloadsList downloads-item').shadowRoot.querySelector('div#content  #file-link').text")
        except:
            pass
        time.sleep(1)
        if time.time() > endTime:
            break


# In[11]:


run_directory = os.getcwd()
# newPath = run_directory.replace(os.sep, '/')
# path = newPath + '/tmp'

path = run_directory + '\\tmp'

try:
    os.mkdir(path)
except FileExistsError:
    print("Folder already exist.")


# In[12]:


path


# In[13]:


# driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install())
capabilities = DesiredCapabilities.CHROME.copy()
capabilities['acceptSslCerts'] = True 
capabilities['acceptInsecureCerts'] = True

options = webdriver.ChromeOptions()

options.add_experimental_option("prefs", {
        "download.default_directory": path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing_for_trusted_sources_enabled": False,
        "safebrowsing.enabled": False
        })

# options.add_argument('headless')
# options.add_argument('window-size=1920,1080')
options.add_argument("disable-gpu")
# 혹은 options.add_argument("--disable-gpu")
options.add_argument("lang=ko_KR") # 한국어!
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")

driver = set_chrome_driver()
# webdriver.Chrome(executable_path=r'C:\Users\1907043\Documents\py\chromedriver.exe', chrome_options=options)

# driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5];},});")
# driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")
# driver.execute_script("const getParameter = WebGLRenderingContext.getParameter;WebGLRenderingContext.prototype.getParameter = function(parameter) {if (parameter === 37445) {return 'NVIDIA Corporation'} if (parameter === 37446) {return 'NVIDIA GeForce GTX 980 Ti OpenGL Engine';}return getParameter(parameter);};")

# user_agent = driver.find_element_by_css_selector('#user-agent').text
# plugins_length = driver.find_element_by_css_selector('#plugins-length').text
# languages = driver.find_element_by_css_selector('#languages').text
# webgl_vendor = driver.find_element_by_css_selector('#webgl-vendor').text
# webgl_renderer = driver.find_element_by_css_selector('#webgl-renderer').text

# print('User-Agent: ', user_agent)
# print('Plugin length: ', plugins_length)
# print('languages: ', languages)
# print('WebGL Vendor: ', webgl_vendor)
# print('WebGL Renderer: ', webgl_renderer)
driver.get('about:blank')

driver.get('https://kbland.kr/webview.html#/main/statistics')
driver.implicitly_wait(3)

downloadfile_list = []
print("Start!")

# click on download link
Download_Button = (By.XPATH, '//*[@id="reference2"]/div[1]/button')
WebDriverWait(driver, 20).until(EC.element_to_be_clickable(Download_Button)).click()
# print ("Download button clicked")
# Download_exe = driver.find_element(*Download_Button)
# Download_exe.click()
time.sleep(5)

# get the downloaded file name
latestDownloadedFileName = getDownLoadedFileName(60) #waiting 1 minutes to complete the download
file1 = os.path.join(path, latestDownloadedFileName)
downloadfile_list.append(file1)

driver.execute_script("window.close()")
driver.switch_to.window(driver.window_handles[0])
# driver.get('https://kbland.kr/webview.html#/main/statistics')
time.sleep(1)

# driver.find_element_by_id('__BVID__32___BV_tab_button__').click()
Month_Button = (By.XPATH, '//*[@id="__BVID__32___BV_tab_button__"]')
driver.find_element(*Month_Button).click()

Download_Button = (By.XPATH, '//*[@id="reference2"]/div[1]/button')
WebDriverWait(driver, 20).until(EC.element_to_be_clickable(Download_Button)).click()
# Download_exe = driver.find_element(*Download_Button)
# Download_exe.click()
time.sleep(5)

# get the downloaded file name
latestDownloadedFileName = getDownLoadedFileName(60) #waiting 1 minutes to complete the download
file2 = os.path.join(path, latestDownloadedFileName)
downloadfile_list.append(file2)

print(downloadfile_list)
print('Done!')

driver.quit()


# In[ ]:




