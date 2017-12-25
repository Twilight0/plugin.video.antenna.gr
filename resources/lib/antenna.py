# -*- coding: utf-8 -*-

'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import json, re
from tulip import bookmarks, directory, client, cache, workers, control


class indexer:

    def __init__(self):

        self.list = [] ; self.data = []
        self.base_link = 'http://www.antenna.gr'
        self.tvshows_link = self.base_link.replace('www', 'mservices') + '/services/mobile/getshowbymenucategory.ashx?menu='
        self.episodes_link = self.base_link.replace('www', 'mservices') + '/services/mobile/getepisodesforshow.ashx?show='
        self.archive_link = self.base_link.replace('www', 'mservices') + '/services/mobile/getshowsbygenre.ashx?islive=0&genre=a0f33045-dfda-459a-8e4f-a65b015a0bc2'
        self.popular_link = self.base_link.replace('www', 'mservices') + '/services/mobile/getlatestepisodes.ashx?'
        self.recommended_link = self.base_link.replace('www', 'mservices') + '/services/mobile/getrecommended.ashx?'
        self.news_link = self.base_link.replace('www', 'mservices') + '/services/mobile/getepisodesforshow.ashx?show=eaa3d856-9d11-4c3f-a048-a617011cee3d'
        self.weather_link = self.base_link.replace('www', 'mservices') + '/services/mobile/getepisodesforshow.ashx?show=ffff8dbf-8600-4f4a-9eb8-a617012eebab'
        self.get_live = self.base_link.replace('www', 'mservices') + '/services/mobile/getLiveStream.ashx?'
        self.live_link_1 = 'http://antglantennatv-lh.akamaihd.net/i/live_1@421307/master.m3u8'
        self.live_link_2 = 'http://antglantennatv-lh.akamaihd.net/i/live_2@421307/master.m3u8'
        self.live_page = self.base_link + '/Live'

    def root(self):

        self.list = [
            {
                'title': control.lang(32001),
                'action': 'live',
                'isFolder': 'False',
                'icon': 'live.png'
            }
            ,
            {
                'title': control.lang(32002),
                'action': 'tvshows',
                'icon': 'tvshows.png'
            }
            ,
            {
                'title': control.lang(32003),
                'action': 'archive',
                'icon': 'archive.png'
            }
            ,
            {
                'title': control.lang(32004),
                'action': 'popular',
                'icon': 'popular.png'
            }
            ,
            {
                'title': control.lang(32005),
                'action': 'recommended',
                'icon': 'recommended.png'
            }
            ,
            {
                'title': control.lang(32006),
                'action': 'news',
                'icon': 'news.png'
            }
            ,
            {
                'title': control.lang(32007),
                'action': 'weather',
                'icon': 'weather.png'
            }
            ,
            {
                'title': control.lang(32008),
                'action': 'bookmarks',
                'icon': 'bookmarks.png'
            }
        ]

        directory.add(self.list, content='videos')

    def bookmarks(self):

        self.list = bookmarks.get()

        if self.list is None:
            return

        for i in self.list:
            bookmark = dict((k, v) for k, v in i.iteritems() if not k == 'next')
            bookmark['delbookmark'] = i['url']
            i.update({'cm': [{'title': 32502, 'query': {'action': 'deleteBookmark', 'url': json.dumps(bookmark)}}]})

        self.list = sorted(self.list, key=lambda k: k['title'].lower())
        self.list = [i for i in self.list if 'url' in i and self.episodes_link in i['url']]

        directory.add(self.list, content='videos')

    def tvshows(self):

        self.list = cache.get(self.items_list, 24, self.tvshows_link)

        if self.list is None:
            return

        for i in self.list: i.update({'action': 'episodes'})

        for i in self.list:
            bookmark = dict((k, v) for k, v in i.iteritems() if not k == 'next')
            bookmark['bookmark'] = i['url']
            i.update({'cm': [{'title': 32501, 'query': {'action': 'addBookmark', 'url': json.dumps(bookmark)}}]})

        self.list = sorted(self.list, key=lambda k: k['title'].lower())

        directory.add(self.list, content='videos')

    def archive(self):

        self.list = cache.get(self.items_list, 24, self.archive_link)

        if self.list is None:
            return

        for i in self.list: i.update({'action': 'reverseEpisodes'})

        for i in self.list:
            bookmark = dict((k, v) for k, v in i.iteritems() if not k == 'next')
            bookmark['bookmark'] = i['url']
            i.update({'cm': [{'title': 32501, 'query': {'action': 'addBookmark', 'url': json.dumps(bookmark)}}]})

        self.list = sorted(self.list, key=lambda k: k['title'].lower())

        directory.add(self.list, content='videos')

    def episodes(self, url, reverse=False):
        self.list = cache.get(self.items_list, 1, url)

        if self.list is None:
            return

        for i in self.list: i.update({'action': 'play', 'isFolder': 'False'})

        if reverse is True:
            self.list = self.list[::-1]

        directory.add(self.list, content='videos')

    def popular(self):
        self.episodes(self.popular_link)

    def recommended(self):
        self.episodes(self.recommended_link)

    def news(self):
        self.episodes(self.news_link)

    def weather(self):
        self.episodes(self.weather_link)

    def play(self, url):
        directory.resolve(self.resolve(url))

    def live(self):
        directory.resolve(self.resolve_live(), meta={'title': 'ANT1'})

    def items_list(self, url):

        try:
            page = url + '&page=1'

            result = client.request(page, mobile=True)
            result = re.findall('\((.+?)\);$', result)[0]
            result = json.loads(result)

            items = result['data']

            if 'total_pages' in result:
                pages = int(result['total_pages'])
                pages = range(2, pages + 1)[:16]

                threads = []
                for i in pages:
                    threads.append(workers.Thread(self.thread, url + '&page=%s' % str(i), i - 2))
                    self.data.append('')
                [i.start() for i in threads]
                [i.join() for i in threads]

                for i in self.data:
                    result = re.findall('\((.+?)\);$', i)
                    try:
                        items += json.loads(result[0])['data']
                    except:
                        pass
        except:
            return

        for item in items:
            try:
                if 'OwnerTitle' in item:
                    title = item['OwnerTitle'].strip()
                elif 'Title' in item:
                    title = item['Title'].strip()
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                if 'MediaFileRef' in item:
                    url = item['MediaFileRef'].strip()
                elif 'ShowId' in item:
                    url = item['ShowId'].strip()
                    url = self.episodes_link + url
                url = client.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                if 'CoverImage' in item:
                    image = item['CoverImage'].strip()
                elif 'Image' in item:
                    image = item['Image'].strip()
                if 'MediaFileRef' in item:
                    image = re.sub('w=\d*', 'w=600', image)
                    image = re.sub('h=\d*', 'h=400', image)
                else:
                    image = re.sub('w=\d*', 'w=500', image)
                    image = re.sub('h=\d*', 'h=500', image)
                image = client.replaceHTMLCodes(image)
                image = image.encode('utf-8')

                self.list.append({'title': title, 'url': url, 'image': image})
            except:
                pass

        return self.list

    def resolve_live(self):

        if control.setting('page_resolver') == 'true' and 'Greece' in self.geo_loc():

            html = client.request(self.live_page)

            param = re.findall('\$.getJSON\(\'(.+?)\?', html)[0]
            get_json = self.base_link + param
            cookie = client.request(get_json, output='cookie', close=False, referer=self.live_page)
            result = client.request(get_json, cookie=cookie, referer=self.live_page)
            url = json.loads(result)['url']

            return url

        else:

            try:

                json_obj = client.request(self.get_live)

                url = json.loads(json_obj.strip('();'))['data']['stream']

                if url.endswith('.mp4'):
                    raise StandardError
                else:
                    return url

            except (KeyError, ValueError, StandardError, TypeError):

                if client.request(self.live_link_1, output='response')[0] == '200':
                    return self.live_link_1
                else:
                    return self.live_link_2

    def resolve(self, url):

        if url.endswith('m3u8'):
            return url
        else:
            try:
                html = client.request(url)
                param = re.findall('\$.getJSON\(\'(.+?)\', \{ (.+?) \}', html)[0]
                get_json = self.base_link + param[0] + '?' + param[1].replace(': ', '=').replace('\'', '')

                result = client.request(get_json)
                link = json.loads(result)['url']

                return link
            except:
                pass

    def thread(self, url, i):

        try:
            result = client.request(url, mobile=True)
            self.data[i] = result
        except:
            return

    @staticmethod
    def geo_loc():

        json_obj = client.request('http://freegeoip.net/json/')

        return json_obj
