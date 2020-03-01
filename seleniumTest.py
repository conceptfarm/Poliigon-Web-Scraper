'''
DEPENDENCIES:
	Selenium: https://pypi.org/project/selenium/
	if using Chrome download  chromeDriver: https://sites.google.com/a/chromium.org/chromedriver/downloads
	if using Firefox download geckodriver: https://github.com/mozilla/geckodriver/releases
	- add geckodriver dir to the path env variables & restart machine
'''
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException

import re
import sys
import os
import errno
import urllib.request

downloadRoot = 'c:/poliigon/'

option = webdriver.ChromeOptions()
option.add_argument(' — incognito')
browser = webdriver.Chrome(executable_path='C:\\webDrivers\\chromedriver.exe', chrome_options=option)
#browser = webdriver.Firefox()
browser.get('https://www.poliigon.com/search?type=texture')
urlRoot = 'https://www.poliigon.com/search?'
urlType = '&type=texture'
# Wait 20 seconds for page to load
timeout = 20

#assign a header for the urllib, otherwise 403 Forbidden
opener = urllib.request.URLopener()
opener.addheader('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36')


def makeSurePathExists(path):
	try:
		os.makedirs(path)
	except OSError as exception:
		#print('dir already here')
		if exception.errno != errno.EEXIST:
			raise

#expects 'Dimensions (metric): 21 x 21 cm'
def parseDimensionString(dim):
	x = re.split(":", dim)
	y = (re.split(' ', x[1]))[-1]
	z = re.split(' ', x[1])
	u = [num for num in z if isNum(num)]
	w = convertToMeters(float(u[0]),y)
	h = convertToMeters(float(u[1]),y)
	return [w,h]

def convertToMeters(n, dim):
	switcher={
		'km':n*1000,
		'm':n,
		'dm':n/10,
		'cm':n/100,
		'mm':n/1000
	}
	return switcher.get(dim,"Invalid")

def isNum(s):
	try:
		f = float(s)
		return True
	except ValueError:
		return False



def parseItemsInSubCategory(category, subCat):
	
	sampleGrid =  browser.find_elements_by_xpath("//a[@class='deadLink']")
	links = [x.get_attribute("href") for x in sampleGrid]
	
	#for each sphere sample in sub category page open a new tab
	for link in links:
		browser.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't') 
		browser.get(link)
		try:
			WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='slick-slide slick-current slick-active']")))
			imgDiv =  browser.find_elements_by_xpath("//div[@class='slick-slide slick-current slick-active']/img")
			images = [x.get_attribute('src') for x in imgDiv]
			print(images)
			sampleName = (browser.find_elements_by_xpath("//h2[@id='name']"))[0].text
			dims = (browser.find_elements_by_xpath("//span[@id='real_scale']"))
			dims = [x.text for x in dims]
			#print(sampleName)
			print(dims)
			makeSurePathExists(downloadRoot + category+'//'+ subCat + '//' + sampleName)
			
			if (dims!=['']):
				convertedDims = parseDimensionString(dims[0])
				f = open((downloadRoot + category+'//'+ subCat + '//' + sampleName + '//' + 'dimensions.txt'), "w")
				f.write(str(convertedDims))
				f.close()
				
			filename, headers = opener.retrieve(images[0], (downloadRoot + category+'//'+ subCat + '//' + sampleName + '//' + sampleName + '_tn.jpg'))
			browser.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'w') 
		except TimeoutException:
			print('Timed out waiting for page to load')
			browser.close()



def openCategory(category):
	browser.get(urlRoot+'category='+category+urlType)
	try:
		WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//span[@class='facet-name']")))
		subCategories = browser.find_elements_by_xpath("//div[@class='ais-HierarchicalMenu ais-HierarchicalMenu-list--child']")#/ul/li/div/a[@class='facet-name']
		print(subCategories)
		subTitlesRaw = [x.text for x in subCategories]
		#print('sub titles:')
		#print(subTitles[0], '\n')
		
		#subTitles come in with newline separation, need to split
		subTitlesList = re.split("\n", subTitlesRaw[0])
		if len(subTitlesList)> 0:
			for subCat in subTitlesList:
				makeSurePathExists(downloadRoot+category+'//'+ subCat)
				browser.get(urlRoot+'category='+category + '~' + subCat + urlType)
				try:
					WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//a[@class='deadLink']")))
					paginationContainer = browser.find_elements_by_xpath("//ul[@class='ais-Pagination-list']")
					pItems = [x.text for x in paginationContainer]
					pItems = re.split("\n", pItems[0])

					#remove first two and last two - these are page navigation items
					pItems = (pItems[:-2])[2:]

					for p in pItems:
						print('page is ' + str(p))
						if p!='1':
							#have to get back to the root subcategory URL
							browser.get(urlRoot+'category='+category + '~' + subCat + urlType)
							try:
								WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//a[@class='deadLink']")))
								#can't just use URL to get to the next page, have to send a click to the paginator for the next page
								nextPageElem = browser.find_elements_by_xpath("//a[@class='ais-Pagination-link'][@aria-label='"+p+"']")
								nextPageElem[0].click()
								try:
									WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//a[@class='deadLink']")))
									parseItemsInSubCategory(category,subCat)
								except:
									print('Timed out waiting for page to load')
									browser.quit()
							except TimeoutException:
								print('Timed out waiting for page to load')
								browser.quit()
						else:
							parseItemsInSubCategory(category,subCat)
						
				except TimeoutException:
					print('Timed out waiting for page to load')
					browser.quit()

	except TimeoutException:
		print('Timed out waiting for page to load')
		browser.quit()

makeSurePathExists(downloadRoot)

try:
	WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//span[@class='facet-name']")))
	# find_elements_by_xpath returns an array of selenium objects.
	topCategories = browser.find_elements_by_xpath("//a[@class='facet-item ']")
	# use list comprehension to get the actual repo titles and not the selenium objects.
	titles = [x.text for x in topCategories]
	# print out all the titles.
	#print('titles:')
	#print(titles, '\n')
	
	for i in range(len(titles)):
		makeSurePathExists(downloadRoot+titles[i])
		openCategory(titles[i])
	browser.quit()
except TimeoutException:
	print('Timed out waiting for page to load')
	browser.quit()
	


