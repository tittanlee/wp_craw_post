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

class medialnk:

  def __init__(self):
    self.img_server_url = 'http://file.medialnk.com/'
    self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36'
    }

    # self.wp = WordPress('http://www.dobee01.com', 'tittanlee', 'Novia0829')
    self.wp = WordPress('http://www.dobee01.com', 'moneycome', 'Novia0829')

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
    # wp_new_post = self.wp.request_new_post()
    # article_id  = wp_new_post.id
    article_id = url.split('/')[-1].split('.')[0]

    self.url            = url
    self.dir_name       = "./medialnk/" + article_id
    art_title_string    = str()
    art_category_string = str()
    art_content_string  = str()

    if os.path.exists(self.dir_name):
      shutil.rmtree(self.dir_name)
    os.makedirs(self.dir_name)

    r = requests.get(url, headers = self.headers)
    soup = BeautifulSoup(r.text, 'lxml')
    article_start = soup.find("article", class_ = "post")

    #Find article title
    art_title_string = article_start.h1.text

    # find category
    cat_list = ['政治', '理財', '時事', '兩性', '影劇', '科技', '親子', '運動', '健康', '新奇', '生活', '社會', '正妹', '寵物', '未分類']
    art_category_string = cat_list[-1]

    # To find article content
    art_content = article_start.find('div', id="articleContent")
    art_content_string = str(art_content)

    print(art_content)

    # Remove html comment
    for element in art_content(text=lambda text: isinstance(text, Comment)):
      element.extract()

    # Remove google ad.
    if 'google' in art_content_string:
      for ads_google in art_content.find_all('ins', class_ = 'adsbygoogle'):
        ads_google.decompose()
      for google_script in art_content.find_all("script"):
        google_script.decompose()
    
    # Remove another Ads
    if '廣告' in art_content_string:
      for ads in art_content.find_all(re.compile("ad")):
        ads.decompose()
      for ads in art_content.find_all(string = re.compile("廣告")):
        ads.parent.decompose()

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


    print('====================================================================================')
    print(str(art_content).split())
    return

    # replace img class setting.
    PREFIX_WP_CONTENT_IMG_PATH = '/wp-content/img/' + article_id + '/'
    if 'img' in art_content_string:
      for img in art_content.select('img'):
        if (img.has_attr('adonis-src')):
          img_link = self.img_server_url + img['adonis-src']
        elif (img.has_attr('src')):
          img_link =  img['src']

        self.download_image(img_link)
        new_img_tag = soup.new_tag("img")    
        new_img_tag['class'] = 'aligncenter'
        new_img_tag['src']   = PREFIX_WP_CONTENT_IMG_PATH + img_link.split("/")[-1]
        img.insert_before(new_img_tag)
        img.decompose()


    if '<iframe' in art_content_string:
      
      for media_fram in iframe:
        media_fram['height'] = 360
        media_fram['width']  = 620

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
      # self.wp.auto_post_publish(wp_new_post, art_category_string, art_title_string, art_content, resize_thumb_jpg_path)
    except:
      return


  def _empty_tag_attrs(self, art_content, tag_name):
    try:
      for lbl in art_content.select(tag_name):
        for k in list(lbl.attrs.keys()):
          del lbl[k]
        if not lbl.contents:
          lbl.decompose()
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
  # tmp_url = "http://medialnk.com/category/%s/%s"
  # tmp_url = 'http://medialnk.com/category/New/%s'
  # craw = medialnk()

  # art_count = 1
  # for page_number in range(4, 5):
  #   page_url = (tmp_url %(page_number))
  #   for art_link, thumb_link in craw.get_art_link_by_page(page_url):
  #     craw.get_content(art_link, thumb_link)
  #     print('%04d ==================================================\n' %(art_count))
  #     art_count = art_count + 1
        

  # craw = medialnk()
  # tmp_url   = 'http://medialnk.com/%s/'
  # tmp_thumb = 'http://file.medialnk.com/n%s/t_m.jpg'
  # art_count = 1
  # for idx in range(50499, 50504):
  #   art_link   = (tmp_url %(idx))
  #   thumb_link = (tmp_thumb %(idx))
  #   craw.get_content(art_link, thumb_link)
  #   print('No.%04d ==================================================\n' %(art_count))
  #   art_count = art_count + 1


  craw = medialnk()
  art_link = 'http://www.medialnk.com/post_43747-11.html'
  thumb_link = 'http://s2.medialnk.com/thumb/remote/s6.medialnk.net/uploads/dc/8/43748-11/57174969a4c8e_500x260.jpg'
  craw.get_content(art_link, thumb_link)

main()
