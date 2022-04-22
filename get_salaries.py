import pandas as pd
import numpy as np
import re
import sys
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm

tqdm.pandas()

driver = uc.Chrome(executable_path = ChromeDriverManager().install())
driver.set_window_size(1120, 550)
driver.set_max_script_timeout(0.5)

def get_salary(link): 
  driver.get(link) 
  salary = driver.find_element_by_tag_name('table').find_elements_by_tag_name('tr')
  salary = salary[len(salary)-1].find_elements_by_tag_name('td')[1].get_attribute('innerHTML')
  salary = re.sub('[^0-9.]', '', salary)
  return salary

data = pd.read_csv("VA_employees_partial.csv")

chunk_list = np.array_split(data, 4)
chunk = chunk_list[sys.argv[1]]

print(f"There are {data.shape[0]} Employees in the entire dataset")
print(f"There are {chunk.shape[0]} Employees in the chunk {sys.argv[1]}")

chunk['salary'] = chunk['link'].progress_apply(get_salary)

chunk.to_csv(f"VA_employees_salaries_{sys.argv[1]}.csv", index=False)