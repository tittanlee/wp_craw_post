from CrawScripts.base_craw import *

class bepo(base_craw):

  def __init__(self, url):
    base_craw.__init__(self, url)

  def get_title(self, soup):
    self.title = soup.find('h1', class_="entry-title").text
    return self.title

  def get_content(self, soup):
    art_content_string  = str()
    article_id          = self.get_wordpress_new_post_id()
    self.dir_name       = self.cwd + '/' + article_id
    # self.dir_name       = '/home/tittanlee/public_html/wp-content/img/' + article_id

    if os.path.exists(self.dir_name):
      shutil.rmtree(self.dir_name)
    os.makedirs(self.dir_name)

    # To find article content
    art_content = soup.find('div', class_='td-post-content td-pb-padding-side')
    for k in list(art_content.attrs.keys()):
      del art_content[k]
    art_content_string = str(art_content)


    # Remove html comment
    for element in art_content(text=lambda text: isinstance(text, Comment)):
      element.extract()


    # remove ad
    for ad in art_content.find_all('div',  class_=re.compile("td-a-rec")):
      ad.decompose()

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

        if '.gif' in img_link:
          img.decompose()
          continue

        file_name = self.dir_name + "/" + str(img_idx) + '.jpg'
        try:
          self.download_image(img_link, file_name)
          new_img_tag = soup.new_tag("img")    
          new_img_tag['class'] = 'aligncenter'
          new_img_tag['src']   = PREFIX_WP_CONTENT_IMG_PATH + str(img_idx) + '.jpg'
          img.insert_before(new_img_tag)
          img.decompose()
          img_idx += 1
        except:
          print('error\n')
          pass
    
    if '<iframe' in art_content_string:
      iframe = art_content.find_all('iframe')
      for media_fram in iframe:
        new_media_fram = soup.new_tag('iframe')
        new_media_fram['height'] = "360"
        new_media_fram['width']  = "100%"
        new_media_fram['class']  = "wp-video"
        new_media_fram['src']  = media_fram['src']
        media_fram.insert_before(new_media_fram)
        media_fram.decompose()


    # if 'via' in art_content_string:
    #   try:
    #     via = art_content.find(string = re.compile('^[Vv][Ii][Aa]'))
    #     print(via.parent)
    #     # via.parent.decompose()
    #   except:
    #     pass

    art_content = str(art_content)
    return art_content
    
