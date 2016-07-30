from CrawScripts.base_craw import *

class coco01(base_craw):

  def __init__(self, url):
    base_craw.__init__(self, url)

  def get_content(self, soup):
    art_content_string  = str()
    article_id          = self.get_wordpress_new_post_id()
    self.dir_name       = self.cwd + '/' + article_id
    # self.dir_name       = '/home/tittanlee/public_html/wp-content/img/' + article_id

    if os.path.exists(self.dir_name):
      shutil.rmtree(self.dir_name)
    os.makedirs(self.dir_name)

    # To find article content
    art_content = soup.find('div', class_="post-html")
    for k in list(art_content.attrs.keys()):
      del art_content[k]
    art_content_string = str(art_content)

    # Remove html comment
    for element in art_content(text=lambda text: isinstance(text, Comment)):
      element.extract()

    # Remove google ad.
    for ads_google in art_content.find_all(string=re.compile('adsbygoogle|sponsored')):
      ads_google.parent.decompose()
    
    # remove all text/javascript
    for javascript in art_content.find_all('script', type="text/javascript"):
      javascript.decompose()

    # remove div class="ad-inserter"
    for ads in art_content.find_all('div', class_ = "ad-inserter"):
      ads.decompose()

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
        img_parent = img.parent
        if (img_parent.has_attr('href')):
          img_parent.unwrap()

        if (img.has_attr('data-original')):
          img_link = img['data-original']
        elif (img.has_attr('src')):
          img_link = img['src']

        try:
          file_name = self.dir_name + "/" + str(img_idx) + '.jpg' 
          self.download_image(img_link, file_name)
          new_img_tag = soup.new_tag("img")    
          new_img_tag['class'] = 'aligncenter'
          new_img_tag['src']   = PREFIX_WP_CONTENT_IMG_PATH + str(img_idx) + '.jpg' 
          new_img_tag['alt']   = self.title + ' - Dobee01 - So Funny So Easy -'
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
    
