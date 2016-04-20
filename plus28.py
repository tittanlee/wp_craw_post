import requests
from bs4 import BeautifulSoup, Comment
import sys, os

# image resize lib
from PIL import Image
from resizeimage import resizeimage
from resizeimage import imageexceptions

from auto_post import *
import shutil
import re

import urllib.request
import time
import string

class plus28:

  def __init__(self):
    # http://plus28.com/forum-1226-1.html
    self.base_url = 'http://plus28.com'
    self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36'
    }

  def get_art_link_by_page(self, url_page):
    r = requests.get(url_page, headers = self.headers)
    r.encoding = 'big5'
    soup = BeautifulSoup(r.text, "lxml")
    for normal_thread in soup.find_all("tbody", id=re.compile("normalthread_")):
      try:
        title      = normal_thread.span.text
        title_link = self.base_url + '/' +normal_thread.span.a.get('href')
        yield title_link
      except:
        pass


    # for art in art_grids.select("li"):
    #   art_link = art.div.a['href']
    #   art_link = self.base_url + "/" + art_link
    #   yield art_link
     

  def get_content(self, url):
    self.url = url

    r = requests.get(url, headers = self.headers, verify=True)
    r.encoding = 'big5'
    soup = BeautifulSoup(r.text, 'lxml')
    content = soup.find("div", class_="postmessage defaultpost")

    art_title = content.h2.get_text(strip=True)
    art_title = re.sub('['+string.punctuation+']', '', art_title)
    art_title = re.sub("\s+", "", art_title)
    art_title = art_title.rstrip(".")


    # self.dir_name = "./plus28/" + url.split('-')[1] + '-' + art_title
    self.dir_name = "./plus28/" + art_title
    if os.path.exists(self.dir_name):
      shutil.rmtree(self.dir_name)
    os.makedirs(self.dir_name)


    print("%s - %s" %(url, art_title))
    art_content = str()
    for img in content.find_all("img"):
      if img.has_attr('src'): 
        img_url_path = img['src']
        img_save_name = self.download_image(img_url_path)

        for k in list(img.attrs.keys()):
          del img[k]
        img['src'] = ('/wordpress/article/%s/' %(art_title)) + img_save_name.split('/')[-1]
        art_content += (str(img) + '\n') 

    # print(art_content)
    # return

    first_jpg_path = self.dir_name + '/' + [f for f in os.listdir(self.dir_name)][0]
    resize_thumb_jpg_path = './' + self.dir_name + '/thumb.jpg'
    self.resize_image(first_jpg_path)
    hello_funny_wp = WordPress('http://gigashare.tw/wordpress', 'rootroot', '123456')
    cat = hello_funny_wp.locate_category_by_name("正妹")
    hello_funny_wp.auto_post_publish(cat, str(art_title), str(art_content), resize_thumb_jpg_path)

  def insert_bloggerads(self, content):
    ad_code = '\
      <div style="float:none;margin:10px 0 10px 0;text-align:center;"> \
        <ins style="display:inline-block"> \
          <script src="http://js1.bloggerads.net/showbanner.aspx?blogid=20160315000013&amp;charset=utf-8" type="text/javascript"></script> \
        </ins> \
      </div>'
    return ad_code + content

  def download_image(self, img_url):
    file_name = self.dir_name + "/" + img_url.split('/')[-1]
    r = requests.get(img_url, headers = self.headers)
    f = open(file_name, 'wb')
    f.write(r.content)
    f.close()
    return file_name


    
    # result = urllib.request.urlretrieve(img_url, file_name)

  def download_thumb_image(self, img_url):
    file_name = download_image(img_url)
    self.resize_image(file_name)

  def resize_image(self, img_path, height = 200, width = 200):
    resize_thumb_jpg_path = './' + self.dir_name + '/thumb.jpg'
    try:
      fd_img = open(img_path, 'r+b')
      img = Image.open(fd_img) 
      img = resizeimage.resize_thumbnail(img, [height, width])
      img.save(resize_thumb_jpg_path, img.format)
      fd_img.close()
      # os.remove(img_path)
    except imageexceptions.ImageSizeError:
      shutil.copyfile(img_path, resize_thumb_jpg_path)
      # os.renames(img_path, resize_thumb_jpg_path)

def main():
  craw = plus28()
  # url = 'http://www.plus28.com/thread-6547979-1-1.html'
  # craw.get_content(url)


  tmp_page_url = 'http://www.plus28.com/forum-1112-%s.html'
  for idx in range(1, 2):
    page_url = (tmp_page_url %idx)
    for art_url in craw.get_art_link_by_page(page_url):
      try_count = 0
      while True:
        try:
          craw.get_content(art_url)
          break
        except:
          if (try_count == 5):
            break
          try_count += 1
          print("failed get - %s, retry count:%s" %(art_url, try_count))
          time.sleep(1)
          pass
          

    

main()