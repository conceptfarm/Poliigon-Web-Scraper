'''
DEPENDENCIES:
	Selenium: https://pypi.org/project/selenium/
	chromeDriver: https://sites.google.com/a/chromium.org/chromedriver/downloads
	geckodriver: https://github.com/mozilla/geckodriver/releases
	- add geckodriver dir to the path env variables & restart machine
'''
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException
import re

#option = webdriver.ChromeOptions()
#option.add_argument(' — incognito')
#browser = webdriver.Chrome(executable_path='C:\\Python35-32\\Lib\\site-packages\\selenium\\webdriver\\chrome\\chromedriver.exe', chrome_options=option)

browser = webdriver.Firefox()
browser.get('https://www.poliigon.com/search?type=texture')
urlRoot = 'https://www.poliigon.com/search?'
urlType = '&type=texture'
# Wait 20 seconds for page to load
timeout = 20

def openCategory(category):
	browser.get(urlRoot+'category='+category+urlType)
	try:
		WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//span[@class='facet-name']")))
		subCategories = browser.find_elements_by_xpath("//div[@class='ais-HierarchicalMenu ais-HierarchicalMenu-list--child']")#/ul/li/div/a[@class='facet-name']
		subTitles = [x.text for x in subCategories]
		print('sub titles:')
		print(subTitles[0], '\n')
		'''
		subTitles come in like this, need to split
		txt = 'Containers\nDrywall\nOther\nRoofing\nSolar'
		x = re.split("\n", txt)
		print(x)
		'''
	except TimeoutException:
		print('Timed out waiting for page to load')
		browser.quit()



try:
	WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//span[@class='facet-name']")))
	# find_elements_by_xpath returns an array of selenium objects.
	topCategories = browser.find_elements_by_xpath("//a[@class='facet-item ']")
	# use list comprehension to get the actual repo titles and not the selenium objects.
	titles = [x.text for x in topCategories]
	# print out all the titles.
	print('titles:')
	print(titles, '\n')
	for i in range(len(titles)):
		openCategory(titles[i])
	'''
	language_element = browser.find_elements_by_xpath("//p[@class='mb-0 f6 text-gray']")
	# same concept as for list-comprehension above.
	languages = [x.text for x in language_element]
	print("languages:")
	print(languages, '\n')
	for title, language in zip(titles, languages):
		print("RepoName : Language")
		print(title + ": " + language, '\n')
	'''
	browser.quit()
except TimeoutException:
	print('Timed out waiting for page to load')
	browser.quit()
	


