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

class jkforum:

  def __init__(self):
    self.base_url = 'http://www.jkforum.net'

  def get_art_link_by_page(self, url_page):
    # http://www.jkforum.net/forum-393-2.html
    r = requests.get(url_page)
    soup = BeautifulSoup(r.text, "lxml")
    art_grids = soup.find("ul", class_ = "ml waterfall cl")

    for art in art_grids.select("li"):
      art_link = art.div.a['href']
      art_link = self.base_url + "/" + art_link
      yield art_link
     

  def get_content(self, url):
    # http://www.jkforum.net/thread-6720720-1-1.html
    self.url = url
    self.dir_name = "./jk/" + url.split('-')[1]

    headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'youremail@domain.com'  # This is another valid field
    }

    r = requests.get(url, headers = headers)
    r.encoding = 'big5'
    soup = BeautifulSoup(r.text, 'lxml')

    art_title = soup.find("h1", class_ = "title-cont").get_text()
    art_title = ''.join(str(e) for e in art_title.split("\n")[1:3])

    image_content = list()
    content_body = soup.find("tbody")
    for image in content_body.select("img"):
      try:
        image['class'] = "aligncenter"
        image['src'] = image['zoomfile']
        del image['file']
        del image['zoomfile']
        del image['onclick']
        image_content.append(str(image) + "\n")
      except:
        pass

    art_content = ''.join(image_content)
    if(len(art_content) == 0):
      return

    print("%s - %s" %(url,art_title))
    
    web_img_url = BeautifulSoup(art_content, 'lxml').img['src']
    status = self.download_image(web_img_url)
    if (status == 'FAILED'):
      shutil.rmtree(self.dir_name)
      return

    resize_thumb_jpg_path = './' + self.dir_name + '/thumb.jpg'
    hello_funny_wp = WordPress('http://gigashare.tw/wordpress', 'rootroot', '123456')
    hello_funny_wp.auto_post_publish(str(art_title), str(art_content), resize_thumb_jpg_path)

  def insert_bloggerads(self, content):
    ad_code = '\
      <div style="float:none;margin:10px 0 10px 0;text-align:center;"> \
        <ins style="display:inline-block"> \
          <script src="http://js1.bloggerads.net/showbanner.aspx?blogid=20160315000013&amp;charset=utf-8" type="text/javascript"></script> \
        </ins> \
      </div>'
    return ad_code + content

  def download_image(self, img_url):
    if os.path.exists(self.dir_name):
      shutil.rmtree(self.dir_name)

    os.makedirs(self.dir_name)
    image = requests.get(img_url)
    if image.status_code != 200:
      return 'FAILED'

    file_name = self.dir_name + "/" + img_url.split('/')[-1]
    with open(file_name, 'wb') as f:
      f.write(image.content)
      f.close()
    self.resize_image(file_name)

  def resize_image(self, img_path, height = 200, width = 200):
    resize_thumb_jpg_path = './' + self.dir_name + '/thumb.jpg'
    try:
      fd_img = open(img_path, 'r+b')
      img = Image.open(fd_img) 
      img = resizeimage.resize_thumbnail(img, [height, width])
      img.save(resize_thumb_jpg_path, img.format)
      fd_img.close()
      os.remove(img_path)
    except imageexceptions.ImageSizeError:
      os.renames(img_path, resize_thumb_jpg_path)

def main():
  # http://www.teepr.com/448487/edwardliu/
  url = sys.argv[1]
  craw = jkforum()

  tmp_url = 'http://www.jkforum.net/forum-520-%s.html'

  for idx in range(12, 1550):
    url = (tmp_url %(idx))
    for art_link in craw.get_art_link_by_page(url):
      craw.get_content(art_link)
    


  # craw = teepr()
  # url = 'http://teepr.com/%s/'
  # for i in range(46921, 46926):
  #   tmp = (url %(i))
  #   print(tmp)
  #   craw.get_content(tmp)
  #   print('\n')

main()
