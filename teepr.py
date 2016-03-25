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

  # def __init__(self):

  
  def get_content(self, url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    art_title = soup.title.text

    art_content = soup.find ("div", class_ = "post-single-content box mark-links")
    content_string = str(art_content)

    # Remove ad
    for ad in art_content.find_all("div", class_ = re.compile('[aA][dD]')):
      ad.decompose()


    # Remove google ad.
    if 'google' in content_string:
      for ads_google in art_content.find_all('ins', class_ = re.compile('adsbygoogle')):
        ads_google.decompose()

    if 'javascript' in content_string:
      for javascript in art_content.find_all('script'):
        javascript.decompose()

    for element in art_content(text=lambda text: isinstance(text, Comment)):
      element.extract()

    # print(art_content.prettify())
    print(art_title)
    print(art_content)

    hello_funny_wp = WordPress('rootroot', '123456')
    hello_funny_wp.auto_post_publish(str(art_title), str(art_content), None)

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
