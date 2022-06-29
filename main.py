import pandas as pd
import requests
import numpy as np
import pandas
from bs4 import BeautifulSoup

rank_url ="https://www.tapology.com/rankings/current-top-ten-heavyweight-mma-fighters-265-pounds"
response = requests.get(rank_url)
soup = BeautifulSoup(response.text,features="html.parser")

fighter_links = [fighter['href'] for fighter in soup.select(".rankingItemsItemRow .name a[href]")]

data = []

for link in fighter_links:
    url = "https://tapology.com"+link
    r = requests.get(url)
    soup = BeautifulSoup(r.text,features="html.parser")
    #Parsing info
    fid = soup.select_one('[name="fid"]').get('content')
    name = soup.select_one('strong:contains("Name:")+span').text
    nickname = soup.select_one('strong:contains("Nickname:")+span').text
    age = soup.select_one('strong:contains("Age")+span')
    dob = soup.select_one('strong:contains("DOB:")+span')
    height = soup.select_one('strong:contains("Height")+span')
    reach = soup.select_one('strong:contains("Reach")+span')
    born = soup.select_one('strong:contains("Born")+span')
    pro_mma_rec = soup.select_one('strong:contains("Pro MMA Record")+span')
    amateur_mma_rec = soup.select_one('strong:contains("Amateur MMA Record")+span')
    #id_list.append(fid)

    newRowInfo = [fid, name, nickname, age, dob, height, reach, born, pro_mma_rec]
    data.append(newRowInfo)

df = pd.DataFrame(data, columns=['fid', 'name', 'nickname', 'age', 'dob', 'height', 'reach', 'born', 'pro_mma_record'])
df.to_csv("fighter_data.csv",index=True)


