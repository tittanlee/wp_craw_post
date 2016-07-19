from CrawScripts.base_craw import *

class daliulian(base_craw):
  def __init__(self, url):
    base_craw.__init__(self, url)
    self.img_server_url = 'http://tw.daliulian.net/'

  def get_content(self, soup):
    art_content_string  = str()
    article_id          = self.get_wordpress_new_post_id()
    self.dir_name       = self.cwd + '/' + article_id
    # self.dir_name       = '/home/tittanlee/public_html/wp-content/img/' + article_id

    if os.path.exists(self.dir_name):
      shutil.rmtree(self.dir_name)
    os.makedirs(self.dir_name)

    # To find article content
    art_content = soup.find('div', id = 'article-content')
    for k in list(art_content.attrs.keys()):
      del art_content[k]
    art_content_string = str(art_content)

    # Remove html comment
    for element in art_content(text=lambda text: isinstance(text, Comment)):
      element.extract()

    # Remove google ad.
    for ads_google in art_content.find_all('div', class_=re.compile("adsDiv")):
      ads_google.decompose()
    
    # Remove another Ads
    for ads in art_content.find_all(id = re.compile("[aA][dD][sS]")):
      ads.unwrap()

    # remove all text/javascript
    for javascript in art_content.find_all('script'):
      javascript.decompose()


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
        if (img.has_attr('adonis-src')):
          img_link = self.img_server_url + img['adonis-src']
        elif (img.has_attr('src')):
          img_link =  img['src']

        file_name = self.dir_name + "/" + str(img_idx) + '.jpg' 
        if (img_link.startswith('/')):
          img_link = self.img_server_url + img_link
        try:
          self.download_image(img_link, file_name)
          new_img_tag = soup.new_tag("img")    
          new_img_tag['class'] = 'aligncenter'
          new_img_tag['src']   = PREFIX_WP_CONTENT_IMG_PATH + str(img_idx) + '.jpg'
          img.insert_before(new_img_tag)
          img.decompose()
          img_idx += 1
        except:
          print('download image error, filename = ', file_name, ', image_link = ', img_link)
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
    #     via.parent.decompose()
    #   except:
    #     pass

    art_content = str(art_content)
    return art_content
    
