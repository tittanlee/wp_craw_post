from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc import WordPressTerm
from wordpress_xmlrpc.methods import taxonomies
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost, EditPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods.media import *

import uuid


class WordPress:

  def __init__(self, site, username, password):
    self.wp = Client( site + '/xmlrpc.php', username, password)
    self.categories = self.wp.call(taxonomies.GetTerms('category'))

  def auto_post_publish(self, category, title, content, thumbnail_path):
    self.post               = WordPressPost()
    self.post.terms_names   = { 'post_tag':['beautiful', 'girl'], 
                                'category':[category.name],
                              }
    self.post.title         = title
    self.post.content       = content

    attachment_id         = self._upload_thumbnail(thumbnail_path)
    self.post.thumbnail   = attachment_id
    self.post.post_status = 'publish'
   
    self.post.id      = self.wp.call(NewPost(self.post))
    # self.wp.call(EditPost(self.post.id, self.post))

  def _upload_thumbnail(self, img_filepath):
    # prepare metadata
    thumb_name = str(uuid.uuid4()) + '.jpg'
    data = {
            'name': thumb_name ,
            'type': 'image/jpeg',  # mimetype
    }
    
                                     # read the binary file and let the XMLRPC library encode it into base64
    with open(img_filepath, 'rb') as img:
      data['bits'] = xmlrpc_client.Binary(img.read())

    response = self.wp.call(UploadFile(data))
    # response == {
    #       'id': 6,
    #       'file': 'picture.jpg'
    #       'url': 'http://www.example.com/wp-content/uploads/2012/04/16/picture.jpg',
    #       'type': 'image/jpeg',
    # }

    attachment_id = response['id']
    return attachment_id

  def get_all_categories(self):
    return self.categories

  def locate_category_by_id(self, cat_id):
    for cat in self.categories:
      if(cat.id == cat_id):
        return cat

  def locate_category_by_name(self, cat_name):
    for cat in self.categories:
      if(cat.name == cat_name):
        return cat



def main():
  w = WordPress('https://hellofunny-zerozero7.rhcloud.com', 'hello funny', 'Novia0829')
  # w.auto_post_publish('test title', 'test content', '/Users/tittanlee/Documents/Project/wp_art_craw/45748/thumb.jpg')
  cat = w.locate_category_by_name("正妹")
  print("%s = %s" %(cat.name, cat.id))
  return
