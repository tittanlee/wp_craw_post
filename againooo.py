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
import random
import http.client

class againooo:

  def __init__(self):
    self.img_server_url = 'http://file.againooo.com/'
    self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36'
    }

    self.wp = WordPress('http://www.dobee01.com', 'tittanlee', 'Novia0829')
    # self.wp = WordPress('http://www.dobee01.com', 'moneycome', 'Novia0829')

  def get_art_link_by_page(self, url_page):
    r = requests.get(url_page, headers = self.headers)
    soup = BeautifulSoup(r.text, "lxml")
    article_list = soup.find("div", id = "Article-list")
    for each_article in article_list.select(".thumb"):
      thumb_link = each_article.img['src']
      art_link   = each_article['href']
      yield art_link, thumb_link
      # print(art_link, " = ",  thumb_path)
  
  def get_content(self, url, thumb_link):
    status = 'BadStatusLine'
    while(status == 'BadStatusLine'):
      try:
        wp_new_post = self.wp.request_new_post()
        status = 'PASS'
      except http.client.BadStatusLine as e:
        print( 'get_content : ', e)
        time.sleep(random.choice(range(30, 80)))

    article_id  = wp_new_post.id

    self.url            = url
    self.dir_name       = "./againooo/" + article_id
    art_title_string    = str()
    art_category_string = str()
    art_content_string  = str()

    if os.path.exists(self.dir_name):
      shutil.rmtree(self.dir_name)
    os.makedirs(self.dir_name)

    r = requests.get(url, headers = self.headers)
    soup = BeautifulSoup(r.text, 'lxml')
    art_title_string = soup.title.text

    # find category
    try:
      art_category = soup.find('header', id = "Content_Header").small
    except:
      return
    if (art_category):
      art_category_string = art_category.text 


    # To find article content
    art_content = soup.find('div', class_="Content_post")
    art_content_string = str(art_content)

    # Remove html comment
    for element in art_content(text=lambda text: isinstance(text, Comment)):
      element.extract()

    # Remove google ad.
    if 'google' in art_content_string:
      for ads_google in art_content.find_all('div', class_ = 'centerBlock'):
          ads_google.decompose()
    
    # Remove another Ads
    if 'ads' in art_content_string:
      for ads in art_content.find_all(id = re.compile("[aA][dD][sS]")):
        ads.unwrap()

    # remove <p>
    self._empty_tag_attrs(art_content, 'p')

    # remove span
    self._empty_tag_attrs(art_content, 'span')

    # remove div
    self._empty_tag_attrs(art_content, 'div')
    
    # remove br
    self._empty_tag_attrs(art_content, 'br')

    # remove strong
    self._empty_tag_attrs(art_content, 'strong')

    # remove section
    self._empty_tag_attrs(art_content, 'section')

    # replace img class setting.
    PREFIX_WP_CONTENT_IMG_PATH = 'http://www.dobee01.com/wp-content/img/' + article_id + '/'
    if 'img' in art_content_string:
      for img in art_content.select('img'):
        if (img.has_attr('adonis-src')):
          img_link = self.img_server_url + img['adonis-src']
        elif (img.has_attr('src')):
          img_link =  img['src']

        try:
          self.download_image(img_link)
          new_img_tag = soup.new_tag("img")    
          new_img_tag['class'] = 'aligncenter'
          new_img_tag['src']   = PREFIX_WP_CONTENT_IMG_PATH + img_link.split("/")[-1]
          img.insert_before(new_img_tag)
          img.decompose()
        except:
          pass


    if '<iframe' in art_content_string:
      iframe = art_content.find_all('iframe')
      for media_fram in iframe:
        media_fram['height'] = "360"
        media_fram['width']  = "80%"
        media_fram['class']  = "wp-video"

    # if 'via' in art_content_string:
    #   try:
    #     via = art_content.find(string = re.compile('^[Vv][Ii][Aa]'))
    #     via.parent.decompose()
    #   except:
    #     pass

    art_content = str(art_content)
    print(article_id, url, thumb_link, art_category_string, art_title_string)
    # print(art_content)
    
    try:
      resize_thumb_jpg_path = './' + self.dir_name + '/thumb.jpg'
      status = self.download_thumb_image(thumb_link)
      self.wp.auto_post_publish(wp_new_post, art_category_string, art_title_string, art_content, resize_thumb_jpg_path)
    except:
      return


  def _empty_tag_attrs(self, art_content, tag_name):
    try:
      for lbl in art_content.select(tag_name):
        for k in list(lbl.attrs.keys()):
          del lbl[k]
    except:
      pass

  def download_image(self, img_url):
    file_name = self.dir_name + "/" + img_url.split('/')[-1]
    r = requests.get(img_url, headers = self.headers)
    f = open(file_name, 'wb')
    f.write(r.content)
    f.close()
    return file_name
    
  def download_thumb_image(self, img_url):
    file_name = self.download_image(img_url)
    self.resize_image(file_name)

  def resize_image(self, img_path, width = 220, height = 220):
    resize_thumb_jpg_path = './' + self.dir_name + '/thumb.jpg'
    try:
      fd_img = open(img_path, 'r+b')
      img = Image.open(fd_img) 
      img = resizeimage.resize_thumbnail(img, [height, width])
      img.save(resize_thumb_jpg_path, img.format)
      fd_img.close()
      os.remove(img_path)
    except imageexceptions.ImageSizeError:
      # shutil.copyfile(img_path, resize_thumb_jpg_path)
      os.renames(img_path, resize_thumb_jpg_path)

def main():
  # cat_list = ['政治', '理財', '時事', '兩性', '影劇', '科技', '親子', '運動', '健康', '新奇', '生活', '社會', '正妹', '寵物']
  # tmp_url = "http://againooo.com/category/正妹/%s"
  # craw = againooo()

  # art_count = 1
  # for page_number in range(1, 3):
  #   page_url = (tmp_url %(page_number))
  #   for art_link, thumb_link in craw.get_art_link_by_page(page_url):
  #     craw.get_content(art_link, thumb_link)
  #     print('%04d ==================================================\n' %(art_count))
  #     art_count = art_count + 1
  #     time.sleep(25)
        

  # http://againooo.com/49937/ 
  # http://file.againooo.com//n49937/t_m.jpg
  craw = againooo()
  tmp_url   = 'http://againooo.com/%s/'
  tmp_thumb = 'http://file.againooo.com/n%s/t_m.jpg'
  art_count = 1
  for idx in range(56150, 56247):
    art_link   = (tmp_url %(idx))
    thumb_link = (tmp_thumb %(idx))
    craw.get_content(art_link, thumb_link)
    print('No.%04d ==================================================\n' %(art_count))
    art_count = art_count + 1
    time.sleep(25)
main()
