from CrawScripts.base_craw import *

class ptt(base_craw):

  def __init__(self, url):
    base_craw.__init__(self, url)

  def get_thumbnail_link(self, soup):
    img_link = soup.img['src']
    if not img_link.startswith('http'):
      img_link = 'http:' + img_link
    return img_link

  def get_content(self, soup):
    art_content_string  = str()
    article_id          = self.get_wordpress_new_post_id()
    self.dir_name       = self.cwd + '/' + article_id
    # self.dir_name       = '/home/tittanlee/public_html/wp-content/img/' + article_id

    if os.path.exists(self.dir_name):
      shutil.rmtree(self.dir_name)
    os.makedirs(self.dir_name)

    # To find article content
    art_content = soup.find('div', id='main-content')
    for k in list(art_content.attrs.keys()):
      del art_content[k]
    art_content_string = str(art_content)

    for mataline in art_content.find_all(class_=re.compile('article-metaline')):
      mataline.decompose()

    for mataline in art_content.find_all(class_='f2'):
      mataline.decompose()

    for mataline in art_content.find_all(class_='push'):
      mataline.decompose()

    for div in art_content.find_all('div'):
      div.unwrap()

    for href in art_content.find_all('a'):
      href.decompose()

    # replace img class setting.
    PREFIX_WP_CONTENT_IMG_PATH = 'http://www.dobee01.com/wp-content/img/' + article_id + '/'
    img_idx = 1
    if 'img' in art_content_string:
      for img in art_content.select('img'):
        img_parent = img.parent
        if (img_parent.has_attr('href')):
          img_parent.unwrap()

        if (img.has_attr('data-original')):
          img_link = img['data-original']
        elif (img.has_attr('src')):
          img_link =  img['src']

        if not img_link.startswith('http'):
          img_link = 'http:' + img_link

        file_name = self.dir_name + "/" + str(img_idx) + '.' + img_link.split('.')[-1]
        try:
          self.download_image(img_link, file_name)
          new_img_tag = soup.new_tag("img")    
          new_img_tag['class'] = 'aligncenter'
          new_img_tag['src']   = PREFIX_WP_CONTENT_IMG_PATH + str(img_idx) + '.' + img_link.split('.')[-1]
          img.insert_before(new_img_tag)
          img.decompose()
          img_idx += 1
          new_img_tag.wrap(soup.new_tag("p"))
        except:
          print('Download image error', img_link, file_name)
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
