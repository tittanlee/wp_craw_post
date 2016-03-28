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

class teepr:

  def __init__(self):
    self.base_url = 'http://www.dailymail.co.uk'

  def get_content(self, url):
    self.url = url
    self.dir_name = url.split('/')[-2]

    r = requests.get(url)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'lxml')

    post_content = soup.find ("div", class_ = "article-text")
    art_title = post_content.h1.text

    art_content = post_content.find("div", attrs = {"itemprop":"articleBody"})
    content_string = str(art_content)

    # Remove div without class attr
    for null_div in art_content.find_all("div"):
      if not null_div.has_attr('class'):
        null_div.extract()
    
    # Remove AD Video
    try:
      art_content.find("div",  class_ = "moduleFull mol-video").decompose()
    except:
      pass

    # Remove html comment
    for element in art_content(text=lambda text: isinstance(text, Comment)):
      element.extract()

    # replace img class setting.
    if 'img' in content_string:
      for img in art_content.find_all('img'):
        img['class'] = 'aligncenter'
        
      # download thumb image.
      if os.path.exists(self.dir_name):
        shutil.rmtree(self.dir_name)

      thumb_jpg_path        = './' + self.dir_name + '/temp_thumb.jpg'
      os.mkdir(self.dir_name)
      status = self.download_image(art_content.img['src'], thumb_jpg_path)
      if (status == 'FAILED'):
        shutil.rmtree(self.dir_name)
        return

      self.resize_image(thumb_jpg_path)

  

    print(art_title)

    resize_thumb_jpg_path = './' + self.dir_name + '/thumb.jpg'
    hello_funny_wp = WordPress('tittanlee', 'Novia0829')
    hello_funny_wp.auto_post_publish(str(art_title), str(art_content), resize_thumb_jpg_path)

  def insert_bloggerads(self, content):
    ad_code = '\
      <div style="float:none;margin:10px 0 10px 0;text-align:center;"> \
        <ins style="display:inline-block"> \
          <script src="http://js1.bloggerads.net/showbanner.aspx?blogid=20160315000013&amp;charset=utf-8" type="text/javascript"></script> \
        </ins> \
      </div>'
    return ad_code + content

  def download_image(self, img_url, file_name):
    image = requests.get(img_url)
    if image.status_code != 200:
      return 'FAILED'

    with open(file_name, 'wb') as f:
      f.write(image.content)
      f.close()

  def resize_image(self, img_path, height = 320, width = 200):
    resize_thumb_jpg_path = './' + self.dir_name + '/thumb.jpg'
    try:
      with open(img_path, 'r+b') as f:
        with Image.open(f) as image:
          cover = resizeimage.resize_cover(image, [height, width])
          cover.save(resize_thumb_jpg_path, image.format)
          f.close()
          os.remove(img_path)
    except imageexceptions.ImageSizeError:
      os.renames(img_path, resize_thumb_jpg_path)

def main():
  # http://www.teepr.com/448487/edwardliu/
  url = sys.argv[1]
  craw = teepr()
  craw.get_content(url)



  # craw = teepr()
  # url = 'http://teepr.com/%s/'
  # for i in range(46921, 46926):
  #   tmp = (url %(i))
  #   print(tmp)
  #   craw.get_content(tmp)
  #   print('\n')

main()
