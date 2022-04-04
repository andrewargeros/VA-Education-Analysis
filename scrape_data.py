import pandas as pd
import re
import undetected_chromedriver as uc
from selenium import webdriver
from tqdm import tqdm

def get_school_data(row):
  name = row.find_element_by_tag_name('a').get_attribute('innerHTML')
  link = row.find_element_by_tag_name('a').get_attribute('href')
  year = row.find_elements_by_tag_name('span')[0].get_attribute('innerHTML')
  employees = row.find_elements_by_tag_name('span')[1].get_attribute('innerHTML')
  avg = row.find_elements_by_tag_name('span')[2].get_attribute('innerHTML')
  median = row.find_elements_by_tag_name('span')[2].get_attribute('innerHTML')

  avg = re.sub('[^0-9.]', '', avg)
  median = re.sub('[^0-9.]', '', median)
  employees = re.sub('[^0-9.]', '', employees)

  return {'name': name, 'link': link, 'year': year, 'employees': employees, 'avg': avg, 'median': median}

def get_all_school_data(link):
  driver.get(link)
  table = driver.find_element_by_xpath('//*[@id="employers"]/table').find_elements_by_tag_name('tr')
  return pd.DataFrame([get_school_data(row) for row in table[1:]])

def get_pagination(link):
  driver.get(link)
  lists = driver.find_elements_by_tag_name('ul')[1].find_elements_by_tag_name('li')
  maxp =  lists[len(lists)-2].find_element_by_tag_name('a').get_attribute('innerHTML')
  return int(maxp)

def get_person(row):
  name = row.find_element_by_tag_name('a').get_attribute('innerHTML')
  link = row.find_element_by_tag_name('a').get_attribute('href')
  year = row.find_elements_by_tag_name('span')[0].get_attribute('innerHTML')
  position = row.find_elements_by_tag_name('span')[1].get_attribute('innerHTML')
  employer = row.find_elements_by_tag_name('span')[2].get_attribute('innerHTML')
  return {'name': name, 'link': link, 'year': year, 'position': position, 'employer': employer}

def get_all_people_on_page():
  table = driver.find_element_by_tag_name('table').find_elements_by_tag_name('tr')
  return pd.DataFrame([get_person(row) for row in table[1:]])

def get_entire_listing(link):
  df = pd.DataFrame()
  pagination = get_pagination(link)
  for i in range(1, pagination+1):
    driver.get(link + '&page=' + str(i))
    page = get_all_people_on_page()
    df = df.append(page)
  return df

def get_salary(link): 
  driver.get(link) 
  salary = driver.find_element_by_tag_name('table').find_elements_by_tag_name('tr')
  salary = salary[len(salary)-1].find_elements_by_tag_name('td')[1].get_attribute('innerHTML')
  salary = re.sub('[^0-9.]', '', salary)
  return salary

driver = uc.Chrome(executable_path="C:/Users/aargeros/Downloads/chromedriver.exe")

## Get Links to all VA public employers -- list is longer than needed, so we filter by hand
df = pd.DataFrame()
for i in range(1,31):
  link = "https://govsalaries.com/state/VA?page=" + str(i) + "&year=2020"
  page = get_all_school_data(link)
  df = df.append(page)
  print(i)

df.to_csv('VA_schools.csv', index=False)

## Read in the filtered VA schools list and scrape links of people
df = pd.read_csv("VA_schools_filtered.csv")

listings = pd.DataFrame()
for row in df[df.index >= 7].itertuples():
  print(row.name, row.employees)

  listings = listings.append(get_entire_listing(row.link))

listings.to_csv('VA_listings_partial.csv', index=False)

## Read in the partial VA listings and scrape salaries
tqdm.pandas()
data = pd.read_csv("VA_employees_partial.csv").head()
data['salary'] = data['link'].progress_apply(get_salary)

data.to_csv('VA_employees_salaries.csv', index=False)

