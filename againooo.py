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

class againooo:

  def __init__(self):
    self.img_server_url = 'http://file.againooo.com/'
    self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36'
    }

  
  def get_content(self, url):
    self.url      = url
    self.dir_name = url.split('/')[-2]
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    art_title = soup.title.text

    # find article header element
    try:
      art_category = soup.find('header', id = "Content_Header").small
    except:
      return
    if (art_category):
      art_category_string = art_category.text 

    art_content = soup.find('div', class_="Content_post")
    content_string = str(art_content)

    # Remove google ad.
    if 'google' in content_string:
      for ads_google in art_content.find_all('div', class_ = 'centerBlock'):
        ads_google.decompose()

    # replace img class setting.
    if 'img' in content_string:
      for img in art_content.find_all('img'):
        img['class'] = 'aligncenter'

        if (img.get('adonis-src')):
          img['src'] = self.img_server_url + img['adonis-src']
          del img['adonis-src']
        
        # img['height'] = 360
        # img['width']  = 620

      # download thumb image.
      if os.path.exists(self.dir_name):
        shutil.rmtree(self.dir_name)

      os.makedirs(self.dir_name)


    if '<iframe' in content_string:
      iframe = art_content.find('iframe')
      iframe['height'] = 360
      iframe['width']  = 620

    if 'via' in content_string:
      try:
        via = art_content.find(string = re.compile('^[Vv][Ii][Aa]'))
        via.parent.decompose()
      except:
        pass

    print(art_title, art_category_string)
    
    resize_thumb_jpg_path = './' + self.dir_name + '/thumb.jpg'
    status = self.download_thumb_image(art_content.img['src'])
    wp = WordPress('http://funnyplus-zerozero7.rhcloud.com', 'root', 'Novia0829')
    wp.auto_post_publish(art_category_string, str(art_title), str(art_content), resize_thumb_jpg_path)

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
    file_name = self.download_image(img_url)
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

  # url = sys.argv[1]
  # craw = againooo()
  # craw.get_content(url)



  craw = againooo()
  url = 'http://againooo.com/%s/'
  for i in range(46920, 46930):
    tmp = (url %(i))
    print(tmp)
    craw.get_content(tmp)

main()
