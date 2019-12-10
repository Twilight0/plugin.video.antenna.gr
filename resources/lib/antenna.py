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
from youtube_resolver import resolve as yt_resolver
from tulip import bookmarks, directory, client, cache, workers, control, youtube
from tulip.compat import range, iteritems


class Indexer:

    def __init__(self):

        self.list = [] ; self.data = []
        self.base_link = 'https://www.antenna.gr'
        self.shows_link = ''.join([self.base_link, '/shows/ALL'])
        self.archive_link = ''.join([self.base_link, '/directory/ALL'])
        self.news_link = ''.join([self.base_link, '/ant1news/videos'])
        self.weather_link = ''.join([self.base_link, '/webtv/3091/kairos?showall'])
        self.sports_link = ''.join([self.base_link, '/webtv/3062/athlitika?showall'])
        self.life_link = ''.join([self.base_link, '/webtv/5271/life?showall'])
        self.latest_link = ''.join([self.base_link, '/webtv/'])
        self.more_videos = ''.join([self.base_link, '/templates/data/morevideos?aid='])
        self.more_web_videos = ''.join([self.base_link, '/templates/data/WEBTVvideosPerVideoCategory?cid='])
        self.player_link = ''.join([self.base_link, '/templates/data/player?cid={0}'])
        self.live_link = 'https://antennalivesp-lh.akamaihd.net/i/live_1@715138/master.m3u8'
        self.yt_id = 'UC0smvAbfczoN75dP0Hw4Pzw'
        self.yt_key = 'AIzaSyBOS4uSyd27OU0XV2KSdN3vT2UG_v0g9sI'

    def root(self):

        self.list = [
            {
                'title': control.lang(32001),
                'action': 'play',
                'isFolder': 'False',
                'icon': 'live.png',
                'url': self.live_link
            }
            ,
            {
                'title': control.lang(32002),
                'action': 'listing',
                'icon': 'shows.png',
                'url': self.shows_link
            }
            ,
            {
                'title': control.lang(32003),
                'action': 'listing',
                'icon': 'archive.png',
                'url': self.archive_link
            }
            ,
            {
                'title': control.lang(32006),
                'action': 'videos',
                'icon': 'news.png',
                'url': self.news_link
            }
            ,
            {
                'title': control.lang(32007),
                'action': 'videos',
                'icon': 'weather.png',
                'url': self.weather_link
            }
            ,
            {
                'title': control.lang(32010),
                'action': 'videos',
                'icon': 'sports.png',
                'url': self.sports_link
            }
            ,
            {
                'title': control.lang(32014),
                'action': 'videos',
                'icon': 'lifestyle.png',
                'url': self.life_link
            }
            ,
            {
                'title': control.lang(32004),
                'action': 'videos',
                'icon': 'popular.png',
                'url': self.latest_link
            }
            ,
            {
                'title': control.lang(32005),
                'action': 'youtube_channel',
                'icon': 'youtube.png'
            }
            ,
            {
                'title': control.lang(32008),
                'action': 'bookmarks',
                'icon': 'bookmarks.png'
            }
        ]

        for item in self.list:

            cache_clear = {'title': 32011, 'query': {'action': 'cache_clear'}}
            item.update({'cm': [cache_clear]})

        directory.add(self.list, content='videos')

    def bookmarks(self):

        self.list = bookmarks.get()

        if self.list is None:
            return

        for i in self.list:

            bookmark = dict((k, v) for k, v in iteritems(i) if not k == 'next')
            bookmark['delbookmark'] = i['url']
            i.update({'cm': [{'title': 32502, 'query': {'action': 'deleteBookmark', 'url': json.dumps(bookmark)}}]})

        self.list = sorted(self.list, key=lambda k: k['title'].lower())

        directory.add(self.list, content='videos')

    def youtube_channel(self):

        self.list = [
            {
                'title': 32013,
                'action': 'videos',
                'icon': 'youtube.png',
                'url': self.yt_id

            }
            ,
            {
                'title': 32012,
                'action': 'playlists',
                'icon': 'youtube.png'
            }
        ]

        directory.add(self.list)

    def playlists(self):

        self.list = cache.get(youtube.youtube(key=self.yt_key).playlists, 12, self.yt_id)

        if self.list is None:
            return

        for i in self.list:

            i.update({'action': 'videos'})
            bookmark = dict((k, v) for k, v in iteritems(i) if not k == 'next')
            bookmark['bookmark'] = i['url']
            i.update({'cm': [{'title': 32501, 'query': {'action': 'addBookmark', 'url': json.dumps(bookmark)}}]})

        directory.add(self.list, content='videos')

    def items_list(self, url):

        html = client.request(url)

        items = client.parseDOM(html, 'article', attrs={'class': 'item overlay grid__col-xs-6 grid__col-lg-4'})

        for item in items:

            title = client.parseDOM(item, 'h2')[0]
            image = client.parseDOM(item, 'img', ret='src')[0]
            url = client.parseDOM(item, 'a', attrs={'rel': 'bookmark'}, ret='href')[0]
            url = ''.join([self.base_link, url, '/videos'])
            plot = client.parseDOM(item, 'p', attrs={'class': 'excerpt visible__md'})[0]

            self.list.append({'title': title, 'image': image, 'url': url, 'plot': plot})

        return self.list

    def listing(self, url):

        self.list = cache.get(self.items_list, 24, url)

        if self.list is None:
            return

        for i in self.list:

            i.update({'action': 'videos'})
            bookmark = dict((k, v) for k, v in iteritems(i) if not k == 'next')
            bookmark['bookmark'] = i['url']
            i.update({'cm': [{'title': 32501, 'query': {'action': 'addBookmark', 'url': json.dumps(bookmark)}}]})

        directory.add(self.list, content='videos')

    def video_list(self, url):

        html = client.request(url)

        if 'webtv' in url:
            attribute = 'library-add-container.+?'
        else:
            attribute = 'item overlay grid__.+?'
        tag = 'article'

        if "contentContainer_totalpages" in html or ('totalpages' in html and 'webtv' in url):
            totalPages = re.findall(r'totalpages = (\d+);', html)
            if 'webtv' in url:
                totalPages = int(totalPages[1])
            else:
                totalPages = int(totalPages[0])
            if 'webtv' in url:
                pattern = r'var cid = (\d+);'
            else:
                pattern = r'/templates/data/morevideos\?aid=(\d+)'
            seriesId = re.search(pattern, html).group(1)
            items = []
            threads = []
            for i in list(range(1, totalPages + 1)):
                if 'webtv' in url:
                    threads.append(workers.Thread(self.thread, ''.join([self.more_web_videos, seriesId, "&p=", str(i), '&h=15']), i - 1))
                else:
                    threads.append(workers.Thread(self.thread, ''.join([self.more_videos, seriesId, "&p=", str(i), ]), i - 1))
                control.sleep(200)
                self.data.append('')
            [i.start() for i in threads]
            [i.join() for i in threads]

            print self.data

            for i in self.data:
                items.extend(client.parseDOM(i, tag, attrs={'class': attribute}))
        else:
            items = client.parseDOM(html, tag, attrs={'class': attribute})

        for item in items:

            title = client.parseDOM(item, 'h2')[0]
            image = client.parseDOM(item, 'img', ret='src')[0]
            try:
                url = client.parseDOM(item, 'a', attrs={'rel': 'bookmark'}, ret='href')[0]
            except IndexError:
                url = client.parseDOM(item, 'a', attrs={'class': 'has-video'}, ret='href')[0]
            url = ''.join([self.base_link, url])
            try:
                plot = client.parseDOM(item, 'p', attrs={'class': 'excerpt visible__md.+?'})[0]
            except IndexError:
                plot = title

            self.list.append({'title': title, 'image': image, 'url': url, 'plot': plot})

        return self.list

    def videos(self, url):

        if url == self.yt_id:
            self.list = cache.get(youtube.youtube(key=self.yt_key, replace_url=False).videos, 1, url)
        elif url.startswith('http'):
            self.list = cache.get(self.video_list, 24, url)
        else:
            self.list = cache.get(youtube.youtube(key=self.yt_key, replace_url=False).playlist, 3, url)

        if self.list is None:
            return

        for i in self.list:
            i.update({'action': 'play', 'isFolder': 'False'})

        control.sortmethods()
        control.sortmethods('title')

        directory.add(self.list, content='videos')

    def play(self, url):

        stream = self.resolve(url)

        directory.resolve(stream, dash=stream.endswith('.mpd'))

    def resolve(self, url):

        if url == self.live_link:

            return url

        elif 'youtube' in url or len(url) == 11:

            return self.yt_session(url)

        else:

            id = re.search(r'watch/(\d+)/', url).group(1)
            json_ = json.loads(client.request(self.player_link.format(id)))
            media_url = json_['url']

            return media_url

    @staticmethod
    def yt_session(yt_id):

        streams = yt_resolver(yt_id)

        try:
            addon_enabled = control.addon_details('inputstream.adaptive').get('enabled')
        except KeyError:
            addon_enabled = False

        if not addon_enabled:
            streams = [s for s in streams if 'mpd' not in s['title'].lower()]

        stream = streams[0]['url']

        return stream

    def thread(self, url, i):

        try:
            result = client.request(url, mobile=True)
            self.data[i] = result
        except Exception:
            return
