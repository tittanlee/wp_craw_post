from CrawScripts.base_craw import *

class ptt01cc(base_craw):

  def __init__(self, url):
    base_craw.__init__(self, url)

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
	  
  def get_content(self, soup):
    art_content_string  = str()
    article_id          = self.get_wordpress_new_post_id()
    self.dir_name       = self.cwd + '/' + article_id
    # self.dir_name       = '/home/tittanlee/public_html/wp-content/img/' + article_id

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
    for ads_google in art_content.find_all(class_ = re.compile('adsbygoogle')):
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

        file_name = self.dir_name + "/" + str(img_idx) + '.' + img_link.split('.')[-1]
        try:
          self.download_image(img_link, file_name)
          new_img_tag = soup.new_tag("img")    
          new_img_tag['class'] = 'aligncenter'
          new_img_tag['src']   = PREFIX_WP_CONTENT_IMG_PATH + str(img_idx) + '.' + img_link.split('.')[-1]
          img.insert_before(new_img_tag)
          img.decompose()
          img_idx += 1
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
    
def main():
  if (len(sys.argv) != 2):
    raise RuntimeError('input error. Usage as XXXX  \'ptt01cc article url\'\n')
 
  art_link   = sys.argv[1]
  craw = ptt01cc()
  art_count = 0
  soup = craw.get_soup(art_link)
  try:
    art_title      = craw.get_title(soup)
    art_category   = craw.get_category(soup)
    post_id        = craw.get_wordpress_new_post_id()
    art_thumb_link = craw.get_thumbnail_link(soup)
    art_content    = craw.get_content(soup, post_id)
    publish_status = craw.publish_to_wordpress(art_category, art_title, art_content, art_thumb_link)
    print('No.%04d ==================================================\n' %(art_count))
    art_count = art_count + 1
    # time.sleep(25)
  except Exception as exc:
    print(exc)
    pass
  except:
    print("something to wrong")
    pass
