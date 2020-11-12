import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time 
from pymongo import MongoClient
from pprint import pprint

def scraper():
    URL = 'https://scholarships.gov.in/'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    scolarships = []
    Froms =[]
    from_index=0
    results2 = soup.find_all(class_='accordion')
    for r in results2:
        # scolarships[index]['from']=r.text
        Froms.append(r.text.strip())
    # print(len(Froms))
    fi=0
    types =['Central Schemes','UGC / AICTE Schemes','State Schemes']
    for i in range(3):
        tab = soup.find_all(class_='TabbedPanelsContent')[i]
        results = tab.find_all(class_='panel')
        index = 0
        for r in results:
            curr = None
            for divs in r.find_all(['div','a']):
                if divs.get('class') == None:
                    if divs.name == 'a':
                        if curr.get('Guidelines') == None:
                            curr['Guidelines']=URL+divs['href']
                        else:
                            curr['FAQ']=URL+divs['href']
                        continue
                if 'info' in set(divs['class']):
                    index+=1
                if 'dotHead' in set(divs['class']):
                    if curr != None and len(curr['title'])>4:
                      if(len(curr['title'])>4):
                        curr['Type']=types[i]
                        curr['From']=Froms[fi]
                        scolarships.append(curr)
                    curr={}
                if 'col-md-2' in set(divs['class']):
                    if curr.get('Scheme_Closing_Date') == None:
                        curr['Scheme_Closing_Date'] = divs.text.split(' ')[-1]
                    elif curr.get('Defective_Verification') == None:
                        curr['Defective_Verification'] = divs.text.split(' ')[-1]
                    else:
                        curr['Institute_Verification'] = divs.text.split(' ')[-1]
                if 'col-md-5' in set(divs['class']):
                    curr['title'] = divs.text
            if(len(curr['title'])>4):
                curr['Type']=types[i]
                curr['From']=Froms[fi]
                scolarships.append(curr)
            fi+=1
    return scolarships

DB_URL='mongodb+srv://amit:raj@cluster0.hny5q.mongodb.net/scholarshipportal?retryWrites=true&w=majority'

refresh_minutes = 20
while 1:
    data=scraper()
    print(data)
    print( len(data) )
    client = MongoClient(DB_URL)
    db=client.scholarship
    # db.restaurants.delete_many({})
    db.scholarships.delete_many({})
    db.scholarships.insert_many(data)

    dt = datetime.now() + timedelta(minutes=1)

    while datetime.now() < dt:
        time.sleep(1)