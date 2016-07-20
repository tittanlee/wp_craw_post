import requests
import re
import os
from bs4 import BeautifulSoup



def get_soup(url):
  r = requests.get(url)
  soup = BeautifulSoup(r.text, 'lxml')
  return soup

def draw_seprator():
  print('==================================================================================================\n')

def save_file(file_name, data):
  f = open(file_name, 'a', encoding='UTF-8')
  f.write(data)
  f.close()


home_url = 'http://www.dobee01.com/page/{}/'
page_num = int(input('input the page number : ')) + 1

if os.path.isfile('dobee01.txt'):
  os.remove('dobee01.txt')


for page in range(1, page_num):
  url = home_url.format(page)
  soup = get_soup(url)
  for each_excerpt in soup.select('article'):
    title = each_excerpt.header.h2.text
    link  = each_excerpt.a['href']
    print(title)
    print(link)
    data = title + '\n' + link + '\n\n'
    save_file('dobee01.txt', data)
    draw_seprator()





