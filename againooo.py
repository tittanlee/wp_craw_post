import requests
from bs4 import BeautifulSoup
import sys, os

# image resize lib
from PIL import Image
from resizeimage import resizeimage

from auto_post import *
import shutil

class againooo:

  def __init__(self):
    self.img_server_url = 'http://file.againooo.com/'
  
  def get_content(self, url):
    self.url      = url
    self.dir_name = url.split('/')[-2]
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    art_title = soup.title.text
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
        img['src'] = self.img_server_url + img['adonis-src']
        img['height'] = 360
        img['width']  = 620
        del img['adonis-src']

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
      os.remove(thumb_jpg_path)

    if '<iframe' in content_string:
      iframe = art_content.find('iframe')
      iframe['height'] = 360
      iframe['width']  = 620

    
    resize_thumb_jpg_path = './' + self.dir_name + '/thumb.jpg'
    if os.path.exists(resize_thumb_jpg_path):
      hello_funny_wp = WordPress('hello funny', 'Novia0829')
      hello_funny_wp.auto_post_publish(art_title, str(art_content), resize_thumb_jpg_path)

  def download_image(self, img_url, file_name):
    image = requests.get(img_url)
    if image.status_code != 200:
      return 'FAILED'

    with open(file_name, 'wb') as f:
      f.write(image.content)
      f.close()

  def resize_image(self, img_path, height = 200, width = 200):
    resize_thumb_jpg_path = './' + self.dir_name + '/thumb.jpg'
    with open(img_path, 'r+b') as f:
      with Image.open(f) as image:
        cover = resizeimage.resize_cover(image, [height, width])
        cover.save(resize_thumb_jpg_path, image.format)
        f.close()

def main():

  url = sys.argv[1]
  craw = againooo()
  craw.get_content(url)



main()
