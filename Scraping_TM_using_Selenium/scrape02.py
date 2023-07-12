from selenium import webdriver
import time

profile = webdriver.FirefoxProfile()
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.download.manager.showWhenStarting", False)
profile.set_preference("browser.download.dir", ".")
#Example:profile.set_preference("browser.download.dir", "C:\Tutorial\down")
# note that setting the download.dir parameter using set_preference does not seem 
# to have an effect with the current Firefox driver version - 
# the file downloaded to the download directory set in Firefox (the PC's Downloads directory)
profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")

driver = webdriver.Firefox(firefox_profile=profile,executable_path='.\geckodriver')

try:
    driver.get('https://www.browserstack.com/test-on-the-right-mobile-devices')
except Exception as err:
    print(f"Unexpected {err=}, {type(err)=}")
    exit()
# current version of Firefox driver object has find_element() and find_elements() methods
# the find_element() method takes the following parameters:
# 'css selector', 'link text', 'partial link text', 'tag name', 'xpath'
gotit= driver.find_element('css selector', '#accept-cookie-notification')
gotit.click()
downloadcsv= driver.find_element('css selector', '.icon-csv')
downloadcsv.click()
time.sleep(5)
driver.quit()
