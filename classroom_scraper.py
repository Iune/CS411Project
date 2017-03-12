
# coding: utf-8

# In[10]:

url = 'https://courses.illinois.edu/schedule/2017/spring'
from IPython.display import HTML
HTML('<iframe src={0} width=800 height=400>     </iframe>'.format(url))

import requests
page = requests.get(url)
html = page.content

from bs4 import BeautifulSoup

soup = BeautifulSoup(html, 'lxml')


# In[11]:

other_url = 'https://courses.illinois.edu'
links = [] 
tables = soup.find_all('table')
tb = soup.find(id='term-dt').tbody
for row in tb.find_all('a'):
    links.append(other_url + row.get('href'))


# In[12]:

all_urls = [] 
for l in links:
    page = requests.get(l)
    html = page.content
    soup = BeautifulSoup(html, 'lxml')
    tb = soup.find(id='default-dt').tbody
    for row in tb.find_all('a'):
        all_urls.append(other_url + row.get('href'))
        print(other_url + row.get('href'))


# In[34]:

import re
import json
from lxml import html
import sys

file = open('roomlist.txt','w')

locations = []
for l in all_urls:
    page = requests.get(l)
    html = page.content
    soup = BeautifulSoup(html, 'lxml')
    tables = soup.find_all('table')
    script_tag = soup.find(type='text/javascript')
    script_txt = script_tag.contents[0]
    pattern = re.compile(r'(\{[^}]+\})')
    match = re.search(pattern, script_txt)
    json_txt = json.loads(match.group(0))
    temp = json_txt['location']
    content = temp.split("</div>")[0]
    content = content.split(">")[1]
    #content = html.fromstring(temp).xpath('//div/text()'
    if content not in locations:
        print(content)
        locations.append(content)
        file.write(content + '\n')
        
file.close() 
    


# In[ ]:



