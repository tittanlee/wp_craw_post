from CrawScripts import *
import os, sys

def get_instance_of_crawler_class(url):
  if 'bomb01' in url:
    craw = bomb01.bomb01(url)
  elif 'teepr' in url:
    craw = teepr.teepr(url)
  elif 'ptt01' in url:
    craw = ptt01cc.ptt01cc(url)
  elif 'pixnet' in url:
    craw = pixnet.pixnet(url)
  elif 'toments' in url:
    craw = toments.toments(url)
  elif 'daliulian' in url:
    craw = daliulian.daliulian(url)
  elif 'buzzlife' in url:
    craw = buzzlife.buzzlife(url)
  elif 'buzzhand' in url:
    craw = buzzhand.buzzhand(url)
  elif 'gjoyz' in url:
    craw = gjoyz.gjoyz(url)
  elif 'fooding' in url:
    craw = fooding.fooding(url)
  elif 'coco01' in url or 'cocoo1' in url:  
    craw = coco01.coco01(url)
  elif 'circle01' in url:
    craw = circle01.circle01(url)
  else:
    raise RuntimeError('Get Crawler instance error', url, 'not supported')
  return craw


def main():
  tmp_url   = 'http://www.bomb01.com/article/{}'
  art_count = 1

  if (len(sys.argv) != 2):
    raise RuntimeError('input error. Usage as XXXX  article_id \n')

  art_link   = sys.argv[1]
  art_conunt = 0
  craw = get_instance_of_crawler_class(art_link)
  soup = craw.get_soup()
  try:
    art_title      = craw.get_title(soup)
    art_category   = craw.get_category(soup)
    art_thumb_link = craw.get_thumbnail_link(soup)
    print(art_title, art_category, art_thumb_link)
    art_content    = craw.get_content(soup)
    publish_status = craw.publish_to_wordpress(art_category, art_title, art_content, art_thumb_link)
    print('No.%04d ==================================================\n' %(art_count))
    art_count = art_count + 1
  except Exception as exc:
    print(exc)
    pass
 

main()
