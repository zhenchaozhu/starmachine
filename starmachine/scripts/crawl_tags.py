# coding: utf-8

import Queue
import urllib2
import threading
from optparse import OptionParser
from bs4 import BeautifulSoup
from starmachine.model.consts import WEB_CRAWL
from starmachine import settings

crawl_yule_url = 'http://top.baidu.com/buzz?b=618&c=9&fr=topbuzz_b618_c9' # 娱乐名人
crawl_actress_url = 'http://top.baidu.com/buzz?b=18&c=9&fr=topbuzz_b18_c9' # 女演员
crawl_actor_url = 'http://top.baidu.com/buzz?b=17&c=9&fr=topbuzz_b18_c9' # 男演员
crawl_songbird_url = 'http://top.baidu.com/buzz?b=16&c=9&fr=topbuzz_b18_c9' # 女歌手
crawl_male_singer_url = 'http://top.baidu.com/buzz?b=15&c=9&fr=topbuzz_b17_c9' # 男歌手

crawl_urls = [crawl_yule_url, crawl_actress_url, crawl_actor_url, crawl_songbird_url, crawl_male_singer_url]

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-p', '--profile', dest='profile', default='local')
    options, args = parser.parse_args()
    if not options.profile:
        profile = 'product'
    else:
        profile = options.profile

    settings.init(profile)
    from starmachine.model.tag import Tag
    for host in crawl_urls:
        req = urllib2.Request(host)
        content = urllib2.build_opener().open(req).read()
        soup = BeautifulSoup(content, from_encoding='gbk')
        tag_names = soup.find_all("a", class_="list-title")
        for tag_name in tag_names:
            tag_name = tag_name.text
            if not Tag.exists_tag(tag_name):
                Tag.add(tag_name, WEB_CRAWL)
