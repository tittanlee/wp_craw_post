import requests
from bs4 import BeautifulSoup, Comment
import sys, os

# image resize lib
from PIL import Image
from resizeimage import resizeimage
from resizeimage import imageexceptions

from CrawScripts.auto_post import *
import shutil
import re

import urllib.request
import time
import string
import random
import http.client

class base_craw:

  def __init__(self, url):
    self.url = url
    self.headers = {
      'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36'
    }

    self.post_id = 0
    self.cwd = os.getcwd() + '/img'
    self.wp = WordPress('http://www.dobee01.com', 'tittanlee', 'Novia0829')

  def get_art_link_by_page(self, url_page):
    r = requests.get(url_page, headers = self.headers)
    soup = BeautifulSoup(r.text, "html.parser")
    article_list = soup.find("div", id = "Article-list")
    for each_article in article_list.select(".thumb"):
      thumb_link = each_article.img['src']
      art_link   = each_article['href']
      yield art_link, thumb_link
      # print(art_link, " = ",  thumb_path)

  def get_soup(self):
    r = requests.get(self.url, headers = self.headers)
    r.encoding = 'utf-8'
    try:
      soup = BeautifulSoup(r.text, 'lxml')
    except:
      soup = BeautifulSoup(r.text, 'html.parser')
    return soup

  def get_title(self, soup):
    try:
      self.title = soup.find('meta', property="og:title")['content']
      return self.title
    except:
      raise NameError(self.url, "parsing title has something wrong")

  def get_category(self, soup):
    print(self.url, self.title)
    category_list = ['健康', '兩性', '勵志', '娛樂', '寵物', '影劇', '感動', '新奇', '新聞', '時事', '正妹', '爆笑', '生活', '社會', '親子']
    category_count = len(category_list)
    idx = 0
    for category in category_list:
      print('%02s = %s' %(idx, category))
      idx += 1
    while(True):
      cate_num = input('input the category number (input \'q\' to quit): ')
      if (cate_num == 'q'):
        raise NameError('quit select category')
      cate_num = int(cate_num)
      if (cate_num < 0) or (cate_num > category_count):
        print('please input a correct category number')
      else:
        break
    return category_list[cate_num]

  def get_thumbnail_link(self, soup):
    thumb_link = soup.find('meta', property="og:image")['content']
    return thumb_link
  
  def get_wordpress_new_post_id(self):
    self.wp_new_post = self.wp.request_new_post()
    self.post_id  = self.wp_new_post.id
    return self.post_id
  
  def get_content(self, soup):
    art_content_string  = str()
    article_id = self.get_wordpress_new_post_id()
    self.dir_name       = self.cwd + "/base_craw/" + article_id
    # self.dir_name       = '/home/tittanlee/public_html/wp-content/img/' + article_id

    if os.path.exists(self.dir_name):
      shutil.rmtree(self.dir_name)
    os.makedirs(self.dir_name)

    # To find article content
    art_content = soup.find('div', id='content')
    art_content_string = str(art_content)

    # Remove html comment
    for element in art_content(text=lambda text: isinstance(text, Comment)):
      element.extract()

    # Remove google ad.
    for ads_google in art_content.find_all('div', class_ = 'centerBlock'):
      ads_google.decompose()
    
    # Remove another Ads
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
          img_link =  self.img_server_url + img['src']

        if '.gif' in img_link:
          file_name = self.dir_name + "/" + str(img_idx) + '.gif'
        else:
          file_name = self.dir_name + "/" + str(img_idx) + '.jpg'

        try:
          self.download_image(img_link, file_name)
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
        media_fram['width']  = "100%"
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
    status = self.download_image(thumb_jpg_link, self.dir_name + '/' + 'thumb.jpg')
    print(self.post_id, self.url, art_category, art_title)
    print(art_content)
    self.wp.auto_post_publish(self.wp_new_post, art_category, art_title, art_content, thumb_jpg_link)

  def _empty_tag_attrs(self, art_content, tag_name):
    for lbl in art_content.find_all(tag_name):
      if lbl.text.lower() == 'via':
        lbl.decompose()
        continue
      for k in list(lbl.attrs.keys()):
        del lbl[k]

  def download_image(self, img_url, save_name):
    file_name = save_name
    r = requests.get(img_url, headers = self.headers)
    f = open(file_name, 'wb')
    f.write(r.content)
    f.close()
    return file_name
 
  def download_thumb_image(self, img_url):
    file_name = self.download_image(img_url, 'tmp_thumb')
    self.resize_image(file_name)

  def resize_image(self, img_path, width = 220, height = 220):
    resize_thumb_jpg_path = self.dir_name + '/thumb.jpg'
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

