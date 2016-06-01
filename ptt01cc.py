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

class ptt01cc:

  def __init__(self):
    self.img_server_url = 'http://file.ptt01cc.com/'
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

  def get_soup(self, url):
    self.url = url
    r = requests.get(url, headers = self.headers)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'lxml')
    return soup

  def get_title(self, soup):
    title = soup.find('meta', property="og:title")['content']
    return title

  def get_category(self, soup):
    try:
      category = soup.find('meta', property="article:section")['content']
      if category == "影片":
        raise Exception("INVALID_CATEGORY")
      if category == "驚奇":
        category = "新奇"
      if category == "動物":
        category = "寵物"
      return category
    except:
      raise Exception("INVALID_CATEGORY")

  def get_thumbnail_link(self, soup):
    thumb_link = soup.find('meta', property="og:image")['content']
    return thumb_link
  
  def get_wordpress_new_post_id(self):
    self.wp_new_post = self.wp.request_new_post()
    self.post_id  = self.wp_new_post.id
    return self.post_id
  
  def get_content(self, soup, article_id):
    art_content_string  = str()
    self.dir_name       = "./ptt01cc/" + article_id

    if os.path.exists(self.dir_name):
      shutil.rmtree(self.dir_name)
    os.makedirs(self.dir_name)

    # To find article content
    art_content = soup.find('div', id='post-content')
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

    # remove all text/javascript
    for javascript in art_content.find_all('script', type="text/javascript"):
      javascript.decompose()

    # remove all "div-mobile-inread"
    for mobile_inread in art_content.find_all('div', id="div-mobile-inread"):
      mobile_inread.decompose()

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
    img_idx = 1
    if 'img' in art_content_string:
      for img in art_content.select('img'):
        if (img.has_attr('data-original')):
          img_link = img['data-original']
        elif (img.has_attr('src')):
          img_link =  img['src']

        try:
          self.download_image(img_link, str(img_idx))
          new_img_tag = soup.new_tag("img")    
          new_img_tag['class'] = 'aligncenter'
          new_img_tag['src']   = PREFIX_WP_CONTENT_IMG_PATH + str(img_idx) + '.' + img_link.split('.')[-1]
          img.insert_before(new_img_tag)
          img.decompose()
          img_idx += 1
        except:
          print('error\n')
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
    #     print(via.parent)
    #     # via.parent.decompose()
    #   except:
    #     pass

    art_content = str(art_content)
    return art_content
    
  def publish_to_wordpress(self, art_category, art_title, art_content, thumb_jpg_link):
    resize_thumb_jpg_path = './' + self.dir_name + '/thumb.jpg'
    status = self.download_thumb_image(thumb_jpg_link)
    print(self.post_id, self.url, art_category, art_title)
    self.wp.auto_post_publish(self.wp_new_post, art_category, art_title, art_content, thumb_jpg_link)

  def _empty_tag_attrs(self, art_content, tag_name):
    for lbl in art_content.find_all(tag_name):
      if lbl.text.lower() == 'via':
        lbl.decompose()
        continue
      for k in list(lbl.attrs.keys()):
        del lbl[k]

  def download_image(self, img_url, save_name):
    file_name = self.dir_name + "/" + save_name + '.' + img_url.split('.')[-1]
    r = requests.get(img_url, headers = self.headers)
    f = open(file_name, 'wb')
    f.write(r.content)
    f.close()
    return file_name
 
    
  def download_thumb_image(self, img_url):
    file_name = self.download_image(img_url, 'tmp_thumb')
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
  craw = ptt01cc()
  tmp_url   = 'http://ptt01.cc/post_{}'
  art_count = 1
  for idx in range(10100, 10200):
    art_link   = tmp_url.format(idx)
    soup = craw.get_soup(art_link)

    try:
      art_category   = craw.get_category(soup)
      post_id        = craw.get_wordpress_new_post_id()
      art_title      = craw.get_title(soup)
      art_thumb_link = craw.get_thumbnail_link(soup)
      art_content    = craw.get_content(soup, post_id)
      publish_status = craw.publish_to_wordpress(art_category, art_title, art_content, art_thumb_link)
      print('No.%04d ==================================================\n' %(art_count))
      art_count = art_count + 1
      time.sleep(25)
    except Exception as exc:
      print(exc)
      pass
    except:
      print("something to wrong")
      pass
main()
