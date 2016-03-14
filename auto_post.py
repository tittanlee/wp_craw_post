from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost, EditPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods.media import *

import uuid


class WordPress:

  def __init__(self, username, password):
    self.wp = Client('http://hellofunny-zerozero7.rhcloud.com/xmlrpc.php', username, password)

  def auto_post_publish(self, title, content, thumbnail_path):
    self.post         = WordPressPost()
    self.post.title   = title
    self.post.content = content

    attachment_id         = self._upload_thumbnail(thumbnail_path)
    self.post.thumbnail   = attachment_id
    self.post.post_status = 'publish'
   
    # self.wp.call(EditPost(self.post.id, self.post))
    self.post.id      = self.wp.call(NewPost(self.post))

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


def main():
  w = WordPress('hello funny', 'Novia0829')
  w.auto_post_publish('test title', 'test content', '/Users/tittanlee/Documents/Project/wp_art_craw/45748/thumb.jpg')
  return

